// Meta webhook endpoint: https://<your-site>/api/instagram/webhook
//
// GET  — Meta's one-time verification handshake (hub.challenge).
// POST — comment + message events. Rejected unless X-Hub-Signature-256 matches
//        an HMAC of the raw body using your Instagram app secret.

import { safeEqual, verifySignature } from '../../lib/crypto.js';
import { processWebhook } from '../../lib/engine.js';
import { env } from '../../lib/env.js';
import { log } from '../../lib/log.js';

export async function GET(request) {
  const params = new URL(request.url).searchParams;
  const mode = params.get('hub.mode');
  const token = params.get('hub.verify_token') ?? '';
  const challenge = params.get('hub.challenge') ?? '';

  if (mode === 'subscribe' && safeEqual(token, env('IG_VERIFY_TOKEN'))) {
    log.info('webhook.verified');
    return new Response(challenge, { status: 200, headers: { 'Content-Type': 'text/plain' } });
  }
  log.warn('webhook.verify_rejected');
  return new Response('Forbidden', { status: 403 });
}

export async function POST(request) {
  const raw = await request.text(); // raw bytes — must be hashed before parsing

  if (!verifySignature(raw, request.headers.get('x-hub-signature-256'), env('IG_APP_SECRET'))) {
    log.warn('webhook.bad_signature');
    return new Response('Invalid signature', { status: 401 });
  }

  let payload;
  try {
    payload = JSON.parse(raw);
  } catch {
    return new Response('Bad JSON', { status: 400 });
  }

  try {
    await processWebhook(payload);
  } catch (err) {
    log.error('webhook.process_failed', err);
  }
  // Always 200 once the signature is valid — failures are logged, and
  // de-duplication makes Meta's retries harmless anyway.
  return new Response('EVENT_RECEIVED', { status: 200 });
}
