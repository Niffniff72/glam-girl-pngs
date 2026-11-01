// Instagram access token lifecycle.
//
// Long-lived Instagram Login tokens last 60 days. Env vars can't be rewritten at
// runtime, so the weekly cron stores each refreshed token in the database
// (encrypted with a key derived from IG_APP_SECRET). IG_ACCESS_TOKEN in the
// environment is only the seed used until the first refresh. If you ever paste a
// NEW token into IG_ACCESS_TOKEN, it automatically takes over from the stored one.

import { createHash } from 'node:crypto';
import { decryptToken, encryptToken } from './crypto.js';
import { readTokenRow, writeTokenRow } from './db.js';
import { env } from './env.js';
import { log, registerSecret } from './log.js';

const TOKEN_NAME = 'instagram_access_token';
let cache = null; // { token, at }

const seedHash = () => createHash('sha256').update(env('IG_ACCESS_TOKEN')).digest('hex').slice(0, 16);

export async function getAccessToken() {
  if (cache && Date.now() - cache.at < 60_000) return cache.token;

  let token;
  try {
    const row = await readTokenRow(TOKEN_NAME);
    if (row && row.seed_hash === seedHash()) token = decryptToken(row.ciphertext, env('IG_APP_SECRET'));
  } catch (err) {
    // e.g. app secret rotated → old ciphertext unreadable. Fall back to env seed.
    log.warn('token.db_read_failed', { error: err.message });
  }
  token ??= env('IG_ACCESS_TOKEN');

  registerSecret(token);
  cache = { token, at: Date.now() };
  return token;
}

/**
 * Exchange the current long-lived token for a fresh 60-day one and store it.
 * Meta only allows refreshing tokens that are at least 24h old and not expired.
 */
export async function refreshAccessToken() {
  cache = null;
  const current = await getAccessToken();

  const url = new URL('https://graph.instagram.com/refresh_access_token');
  url.searchParams.set('grant_type', 'ig_refresh_token');
  url.searchParams.set('access_token', current);

  const res = await fetch(url, { signal: AbortSignal.timeout(15_000) });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || !data.access_token) {
    throw new Error(`Token refresh failed (${res.status}): ${data?.error?.message ?? 'no token returned'}`);
  }

  registerSecret(data.access_token);
  const expiresAt = data.expires_in ? new Date(Date.now() + data.expires_in * 1000) : null;
  await writeTokenRow(TOKEN_NAME, encryptToken(data.access_token, env('IG_APP_SECRET')), expiresAt, seedHash());
  cache = { token: data.access_token, at: Date.now() };
  return { expiresAt };
}

/** Test helper. */
export function _resetTokenCache() {
  cache = null;
}
