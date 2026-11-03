import assert from 'node:assert/strict';
import { test } from 'node:test';

process.env.IG_VERIFY_TOKEN = 'netlify-verify-token';
process.env.URL = 'https://glam-girl-pngs.netlify.app';
delete process.env.SITE_URL;

const webhook = (await import('../netlify/functions/instagram-webhook.mjs'));
const go = (await import('../netlify/functions/go.mjs'));
const cron = (await import('../netlify/functions/refresh-token.mjs'));

test('netlify wrappers declare the right routes and schedule', () => {
  assert.equal(webhook.config.path, '/api/instagram/webhook');
  assert.equal(go.config.path, '/go/:code');
  assert.equal(cron.config.schedule, '17 14 * * 1');
});

test('webhook wrapper passes the hub.challenge handshake', async () => {
  const res = await webhook.default(new Request(
    'https://x/api/instagram/webhook?hub.mode=subscribe&hub.verify_token=netlify-verify-token&hub.challenge=777'));
  assert.equal(await res.text(), '777');
  const put = await webhook.default(new Request('https://x/api/instagram/webhook', { method: 'PUT' }));
  assert.equal(put.status, 405);
});

test('go wrapper reads :code and falls back to the Netlify URL', async () => {
  const res = await go.default(new Request('https://x/go/@@'), { params: { code: '@@' } });
  assert.equal(res.status, 302);
  assert.equal(res.headers.get('location'), 'https://glam-girl-pngs.netlify.app/');
});
