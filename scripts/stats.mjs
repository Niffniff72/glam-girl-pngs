// Usage: DATABASE_URL=... npm run stats  — per-keyword funnel numbers.
import { getPool } from '../lib/db.js';

const pool = getPool();
try {
  const { rows } = await pool.query(`
    SELECT keyword,
           count(*)::int                                          AS leads,
           count(*) FILTER (WHERE status = 'awaiting_follow')::int AS waiting_on_follow,
           count(*) FILTER (WHERE status = 'awaiting_email')::int  AS waiting_on_email,
           count(email)::int                                      AS emails,
           count(*) FILTER (WHERE status = 'delivered')::int       AS links_sent,
           count(*) FILTER (WHERE click_count > 0)::int            AS clicked,
           coalesce(sum(click_count), 0)::int                     AS total_clicks
      FROM ig_leads GROUP BY keyword ORDER BY leads DESC`);
  console.table(rows);
} finally {
  await pool.end();
}
