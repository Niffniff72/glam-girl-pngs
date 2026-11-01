// Weekly Instagram token refresh — scheduled in vercel.json (Mondays).
// Vercel Cron calls this with "Authorization: Bearer $CRON_SECRET".

import { safeEqual } from '../../lib/crypto.js';
import { env } from '../../lib/env.js';
import { log } from '../../lib/log.js';
import { refreshAccessToken } from '../../lib/token.js';

export async function GET(request) {
  const auth = request.headers.get('authorization') ?? '';
  if (!safeEqual(auth, `Bearer ${env('CRON_SECRET')}`)) {
    return new Response('Unauthorized', { status: 401 });
  }

  try {
    const { expiresAt } = await refreshAccessToken();
    log.info('token.refreshed', { expiresAt });
    return Response.json({ ok: true, expiresAt });
  } catch (err) {
    log.error('token.refresh_failed', err);
    return Response.json({ ok: false }, { status: 500 });
  }
}
