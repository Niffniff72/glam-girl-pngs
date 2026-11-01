// Usage: DATABASE_URL=... npm run db:migrate
import { readFile } from 'node:fs/promises';
import { getPool } from '../lib/db.js';

const sql = await readFile(new URL('../db/schema.sql', import.meta.url), 'utf8');
const pool = getPool();
try {
  await pool.query(sql);
  console.log('Database schema is up to date.');
} catch (err) {
  console.error('Migration failed:', err.message);
  process.exitCode = 1;
} finally {
  await pool.end();
}
