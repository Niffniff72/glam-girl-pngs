import pg from 'pg';
import { env } from './env.js';
import { shortCode } from './crypto.js';

let pool;

export function getPool() {
  if (!pool) {
    // max: 1 — serverless functions each hold one connection. Use your
    // provider's *pooled* connection string (Neon/Supabase "pooler" URL).
    pool = new pg.Pool({ connectionString: env('DATABASE_URL'), max: 1, idleTimeoutMillis: 10_000 });
  }
  return pool;
}

const q = (text, params) => getPool().query(text, params);

/** Returns true the first time an event ID is seen, false on any repeat. */
export async function claimEvent(eventId, kind) {
  const r = await q(
    `INSERT INTO ig_processed_events (event_id, kind) VALUES ($1, $2)
     ON CONFLICT (event_id) DO NOTHING RETURNING event_id`,
    [eventId, kind],
  );
  return r.rowCount === 1;
}

/** Creates the lead, or returns null if this person already has one for this keyword. */
export async function createLead({ igUserId, username, keyword, source, commentId, mediaId, commentText }) {
  const r = await q(
    `INSERT INTO ig_leads (ig_user_id, username, keyword, source, comment_id, media_id, comment_text)
     VALUES ($1, $2, $3, $4, $5, $6, $7)
     ON CONFLICT (ig_user_id, keyword) DO NOTHING
     RETURNING *`,
    [igUserId, username ?? null, keyword, source, commentId ?? null, mediaId ?? null, commentText ?? null],
  );
  return r.rows[0] ?? null;
}

export async function getLead(id) {
  const r = await q(`SELECT * FROM ig_leads WHERE id = $1`, [id]);
  return r.rows[0] ?? null;
}

export async function findLead(igUserId, keyword) {
  const r = await q(`SELECT * FROM ig_leads WHERE ig_user_id = $1 AND keyword = $2`, [igUserId, keyword]);
  return r.rows[0] ?? null;
}

export async function findLeadAwaitingEmail(igUserId) {
  const r = await q(
    `SELECT * FROM ig_leads WHERE ig_user_id = $1 AND status = 'awaiting_email'
     ORDER BY updated_at DESC LIMIT 1`,
    [igUserId],
  );
  return r.rows[0] ?? null;
}

const UPDATABLE = new Set(['status', 'email', 'kit_status', 'target_url', 'link_sent_at', 'username']);

export async function updateLead(id, fields) {
  const keys = Object.keys(fields).filter((k) => UPDATABLE.has(k));
  if (!keys.length) return getLead(id);
  const sets = keys.map((k, i) => `${k} = $${i + 2}`).join(', ');
  const r = await q(
    `UPDATE ig_leads SET ${sets}, updated_at = now() WHERE id = $1 RETURNING *`,
    [id, ...keys.map((k) => fields[k])],
  );
  return r.rows[0] ?? null;
}

/** Reserve a DM step. Returns false if that step was already sent to this lead. */
export async function claimStep(leadId, step) {
  const r = await q(
    `INSERT INTO ig_sent_messages (lead_id, step) VALUES ($1, $2)
     ON CONFLICT DO NOTHING RETURNING step`,
    [leadId, step],
  );
  return r.rowCount === 1;
}

/** Undo a reservation when the send itself failed, so a later tap can retry. */
export async function releaseStep(leadId, step) {
  await q(`DELETE FROM ig_sent_messages WHERE lead_id = $1 AND step = $2`, [leadId, step]);
}

export async function countSteps(leadId, prefix) {
  const r = await q(
    `SELECT count(*)::int AS n FROM ig_sent_messages WHERE lead_id = $1 AND step LIKE $2`,
    [leadId, `${prefix}%`],
  );
  return r.rows[0].n;
}

/** Give the lead a unique short code (idempotent). */
export async function ensureShortCode(leadId) {
  for (let attempt = 0; attempt < 5; attempt++) {
    try {
      const r = await q(
        `UPDATE ig_leads SET short_code = COALESCE(short_code, $2), updated_at = now()
         WHERE id = $1 RETURNING short_code`,
        [leadId, shortCode()],
      );
      return r.rows[0].short_code;
    } catch (err) {
      if (err.code !== '23505') throw err; // unique violation → try another code
    }
  }
  throw new Error('Could not allocate a unique short code');
}

/** Log a click and return where to send the visitor (null if unknown code). */
export async function recordClick(code, { userAgent, referer }) {
  const r = await q(
    `UPDATE ig_leads
        SET click_count = click_count + 1,
            first_clicked_at = COALESCE(first_clicked_at, now())
      WHERE short_code = $1
      RETURNING id, target_url`,
    [code],
  );
  const lead = r.rows[0];
  if (!lead) return null;
  await q(
    `INSERT INTO link_clicks (short_code, lead_id, user_agent, referer) VALUES ($1, $2, $3, $4)`,
    [code, lead.id, userAgent?.slice(0, 500) ?? null, referer?.slice(0, 500) ?? null],
  );
  return lead.target_url;
}

// ---- Encrypted token storage ----------------------------------------------

export async function readTokenRow(name) {
  const r = await q(`SELECT ciphertext, seed_hash, refreshed_at, expires_at FROM app_tokens WHERE name = $1`, [name]);
  return r.rows[0] ?? null;
}

export async function writeTokenRow(name, ciphertext, expiresAt, seedHash) {
  await q(
    `INSERT INTO app_tokens (name, ciphertext, seed_hash, refreshed_at, expires_at) VALUES ($1, $2, $3, now(), $4)
     ON CONFLICT (name) DO UPDATE SET ciphertext = EXCLUDED.ciphertext, seed_hash = EXCLUDED.seed_hash,
       refreshed_at = now(), expires_at = EXCLUDED.expires_at`,
    [name, ciphertext, seedHash, expiresAt],
  );
}
