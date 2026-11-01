// Short-link redirect: https://<your-site>/go/<code>  (rewritten here by vercel.json)
// Counts the click against the person's lead, then 302s to the real link.

import { recordClick } from '../lib/db.js';
import { siteUrl } from '../lib/env.js';
import { log } from '../lib/log.js';

export async function GET(request) {
  const code = new URL(request.url).searchParams.get('code') ?? '';
  let target = null;

  if (/^[A-Za-z0-9]{4,16}$/.test(code)) {
    try {
      target = await recordClick(code, {
        userAgent: request.headers.get('user-agent'),
        referer: request.headers.get('referer'),
      });
    } catch (err) {
      log.error('shortlink.click_failed', err, { code });
    }
  }

  return new Response(null, {
    status: 302,
    headers: { Location: target ?? `${siteUrl()}/`, 'Cache-Control': 'no-store' },
  });
}
