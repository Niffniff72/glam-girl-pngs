// End-to-end flow test against a real Postgres, with Instagram + Kit mocked.
// Runs only when TEST_DATABASE_URL is set:
//   TEST_DATABASE_URL=postgres://localhost/dmtest npm test

import assert from 'node:assert/strict';
import { createHmac } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { after, before, beforeEach, describe, test } from 'node:test';

const DB = process.env.TEST_DATABASE_URL;

describe('comment-to-DM flow', { skip: !DB && 'set TEST_DATABASE_URL to run' }, () => {
  const ACCOUNT = '17840000000000001';
  const calls = [];
  const following = new Map();
  let kitShouldFail = false;
  let mod, pool;

  // ---- Mock Instagram + Kit ------------------------------------------------
  const realFetch = globalThis.fetch;
  function mockFetch(input, init = {}) {
    const url = new URL(String(input));
    const body = init.body ? JSON.parse(init.body) : undefined;
    const method = init.method ?? 'GET';
    calls.push({ host: url.host, path: url.pathname, method, body, auth: init.headers?.Authorization, url: url.toString() });
    const json = (data, status = 200) => Promise.resolve(new Response(JSON.stringify(data), { status }));

    if (url.host === 'graph.instagram.com' || url.host === 'graph.facebook.com') {
      if (url.pathname === '/refresh_access_token') return json({ access_token: 'IGAArefreshedTOKEN000', token_type: 'bearer', expires_in: 5184000 });
      const p = url.pathname.replace(/^\/v[\d.]+\//, '');
      if (p === 'me') return json({ user_id: ACCOUNT, username: 'glamgirlpngs' });
      if (p === ACCOUNT && method === 'GET') return json({ id: ACCOUNT, username: 'glamgirlpngs' });
      if (p === `${ACCOUNT}/messages`) return json({ recipient_id: 'x', message_id: 'm' });
      if (p.endsWith('/replies')) return json({ id: 'reply1' });
      if (method === 'GET') return json({ username: 'someone', is_user_follow_business: following.get(p) ?? false });
    }
    if (url.host === 'api.kit.com') {
      if (kitShouldFail) return json({ errors: ['boom'] }, 500);
      if (url.pathname === '/v4/tags' && method === 'GET') return json({ tags: [], pagination: { has_next_page: false } });
      if (url.pathname === '/v4/tags' && method === 'POST') return json({ tag: { id: 4242, name: body.name } }, 201);
      return json({ subscriber: { id: 1 } }, 201);
    }
    return json({ error: { message: 'unmocked ' + url } }, 500);
  }

  const dms = () => calls.filter((c) => c.path.endsWith('/messages') && c.method === 'POST');
  const sign = (raw) => 'sha256=' + createHmac('sha256', process.env.IG_APP_SECRET).update(raw).digest('hex');

  const commentEvent = (commentId, userId, text, username = 'fan_' + userId) => ({
    object: 'instagram',
    entry: [{ id: ACCOUNT, time: 1, changes: [{ field: 'comments', value: { id: commentId, text, from: { id: userId, username }, media: { id: 'media1', media_product_type: 'REELS' } } }] }],
  });
  const msgEvent = (userId, inner) => ({
    object: 'instagram',
    entry: [{ id: ACCOUNT, time: 1, messaging: [{ sender: { id: userId }, recipient: { id: ACCOUNT }, timestamp: 1, ...inner }] }],
  });
  let midSeq = 0;
  const tap = (userId, payload) => msgEvent(userId, { postback: { mid: 'pb' + ++midSeq, title: 'x', payload } });
  const text = (userId, t) => msgEvent(userId, { message: { mid: 'tx' + ++midSeq, text: t } });

  async function post(payload) {
    const raw = JSON.stringify(payload);
    const res = await mod.webhook.POST(
      new Request('https://site.test/api/instagram/webhook', { method: 'POST', body: raw, headers: { 'x-hub-signature-256': sign(raw) } }),
    );
    assert.equal(res.status, 200);
  }
  const lead = async (userId, keyword) =>
    (await pool.query('SELECT * FROM ig_leads WHERE ig_user_id=$1 AND keyword=$2', [userId, keyword])).rows[0];

  before(async () => {
    Object.assign(process.env, {
      DATABASE_URL: DB,
      SITE_URL: 'https://glam.test',
      IG_APP_SECRET: 'test-app-secret-abc',
      IG_ACCESS_TOKEN: 'IGAAseedTOKEN123',
      IG_VERIFY_TOKEN: 'verify-me-please',
      KIT_API_KEY: 'kit-key-xyz-123',
      CRON_SECRET: 'cron-secret-789',
    });
    globalThis.fetch = mockFetch;
    mod = {
      webhook: await import('../api/instagram/webhook.js'),
      go: await import('../api/go.js'),
      cron: await import('../api/cron/refresh-token.js'),
      db: await import('../lib/db.js'),
    };
    pool = mod.db.getPool();
    await pool.query(await readFile(new URL('../db/schema.sql', import.meta.url), 'utf8'));
    await pool.query('TRUNCATE ig_processed_events, ig_leads, ig_sent_messages, link_clicks, app_tokens RESTART IDENTITY CASCADE');
  });
  after(async () => {
    globalThis.fetch = realFetch;
    await pool.end();
  });
  beforeEach(() => (calls.length = 0));

  test('GET verification echoes hub.challenge only with the right verify token', async () => {
    const ok = await mod.webhook.GET(new Request('https://s/api/instagram/webhook?hub.mode=subscribe&hub.verify_token=verify-me-please&hub.challenge=12345'));
    assert.equal(ok.status, 200);
    assert.equal(await ok.text(), '12345');
    const bad = await mod.webhook.GET(new Request('https://s/api/instagram/webhook?hub.mode=subscribe&hub.verify_token=nope&hub.challenge=12345'));
    assert.equal(bad.status, 403);
  });

  test('POST with a bad signature is rejected and does nothing', async () => {
    const raw = JSON.stringify(commentEvent('c-bad', 'u-bad', 'GLAM'));
    const res = await mod.webhook.POST(new Request('https://s/x', { method: 'POST', body: raw, headers: { 'x-hub-signature-256': 'sha256=deadbeef' } }));
    assert.equal(res.status, 401);
    assert.equal(calls.length, 0);
  });

  test('full GLAM flow: comment → button → follow gate → email → Kit → tracked link → click', async () => {
    const U = 'igsid-100';

    // 1. Comment
    await post(commentEvent('c1', U, 'GLAM pleaseee 🩷'));
    const opener = dms()[0];
    assert.deepEqual(opener.body.recipient, { comment_id: 'c1' });
    assert.equal(opener.body.message.attachment.payload.buttons[0].title, 'Send me the link');
    const linkPayload = opener.body.message.attachment.payload.buttons[0].payload;
    assert.ok(calls.some((c) => c.path.endsWith('/c1/replies')), 'public reply posted');
    assert.equal(opener.auth, 'Bearer IGAAseedTOKEN123');
    assert.ok(!opener.url.includes('access_token'), 'token not in URL');

    // 2. Same person comments again (and Meta retries the first) → nothing new
    calls.length = 0;
    await post(commentEvent('c1', U, 'GLAM pleaseee 🩷'));
    await post(commentEvent('c2', U, 'glam again'));
    assert.equal(dms().length, 0);

    // 3. Tap "Send me the link" while NOT following → follow gate
    calls.length = 0;
    await post(tap(U, linkPayload));
    assert.match(dms()[0].body.message.attachment.payload.text, /follow on @glamgirlpngs/);
    const followedPayload = dms()[0].body.message.attachment.payload.buttons[0].payload;
    assert.match(followedPayload, /^FOLLOWED:/);
    assert.equal((await lead(U, 'GLAM')).status, 'awaiting_follow');

    // 4. Tap "I followed" but still not following → different retry message
    calls.length = 0;
    await post(tap(U, followedPayload));
    assert.match(dms()[0].body.message.attachment.payload.text, /not seeing your follow/);

    // 5. Follows, taps → asked for email
    following.set(U, true);
    calls.length = 0;
    await post(tap(U, followedPayload));
    assert.match(dms()[0].body.message.text, /drop your best email/);
    assert.equal((await lead(U, 'GLAM')).status, 'awaiting_email');

    // 6. Garbage → retry prompt; then real email → Kit subscribe + tag + link
    calls.length = 0;
    await post(text(U, 'hiii'));
    assert.match(dms()[0].body.message.text, /doesn't look quite right/);

    calls.length = 0;
    await post(text(U, 'sure it is Jane.Doe@Gmail.com thanks!'));
    const kitCalls = calls.filter((c) => c.host === 'api.kit.com');
    assert.deepEqual(kitCalls.find((c) => c.path === '/v4/subscribers').body, { email_address: 'jane.doe@gmail.com' });
    assert.ok(kitCalls.some((c) => c.path === '/v4/tags' && c.method === 'POST' && c.body.name === 'IG - GLAM freebie'));
    assert.ok(kitCalls.some((c) => c.path === '/v4/tags/4242/subscribers'));
    const btn = dms()[0].body.message.attachment.payload.buttons[0];
    assert.equal(btn.type, 'web_url');
    assert.match(btn.url, /^https:\/\/glam\.test\/go\/[A-Za-z0-9]{7}$/);

    const l = await lead(U, 'GLAM');
    assert.equal(l.status, 'delivered');
    assert.equal(l.email, 'jane.doe@gmail.com');
    assert.equal(l.kit_status, 'ok');
    assert.equal(l.target_url, 'https://glam.test/assets/products/free-thank-you-cards/thank-you-mini-cards.png');

    // 7. Click the short link
    const code = btn.url.split('/go/')[1];
    const res = await mod.go.GET(new Request(`https://glam.test/api/go?code=${code}`, { headers: { 'user-agent': 'Instagram 300' } }));
    assert.equal(res.status, 302);
    assert.equal(res.headers.get('location'), l.target_url);
    assert.equal((await lead(U, 'GLAM')).click_count, 1);

    // 8. Tapping again after delivery → link re-sent ONCE, then silence
    calls.length = 0;
    await post(tap(U, linkPayload));
    await post(tap(U, linkPayload));
    assert.equal(dms().length, 1);
  });

  test('no-email keyword, already following → link immediately on tap', async () => {
    const U = 'igsid-200';
    following.set(U, true);
    await post(commentEvent('c10', U, 'TUMBLER'));
    const payload = dms()[0].body.message.attachment.payload.buttons[0].payload;
    calls.length = 0;
    await post(tap(U, payload));
    assert.equal(dms().length, 1);
    assert.equal(dms()[0].body.message.attachment.payload.buttons[0].type, 'web_url');
    assert.equal((await lead(U, 'TUMBLER')).target_url, 'https://payhip.com/b/3DSvO');
  });

  test('Kit failure still delivers the link and flags the lead', async () => {
    const U = 'igsid-300';
    following.set(U, true);
    await post(commentEvent('c20', U, 'glam'));
    const payload = dms()[0].body.message.attachment.payload.buttons[0].payload;
    await post(tap(U, payload));
    kitShouldFail = true;
    calls.length = 0;
    await post(text(U, 'me@example.com'));
    kitShouldFail = false;
    assert.equal(dms().length, 1);
    const l = await lead(U, 'GLAM');
    assert.equal(l.status, 'delivered');
    assert.equal(l.kit_status, 'error');
  });

  test('ignores own comments, non-keywords, and someone else tapping your button', async () => {
    await post(commentEvent('c30', ACCOUNT, 'GLAM', 'glamgirlpngs'));
    await post(commentEvent('c31', 'igsid-400', 'love this!!'));
    assert.equal(calls.filter((c) => c.method === 'POST').length, 0);

    following.set('igsid-500', true);
    await post(commentEvent('c32', 'igsid-500', 'JOURNAL'));
    const payload = dms()[0].body.message.attachment.payload.buttons[0].payload;
    calls.length = 0;
    await post(tap('igsid-intruder', payload));
    assert.equal(dms().length, 0);
  });

  test('Unified-login system-user token: uses graph.facebook.com + IG_USER_ID, cron skips refresh', async () => {
    const saved = process.env.IG_ACCESS_TOKEN;
    process.env.IG_ACCESS_TOKEN = 'EAAYsystemUserTOKEN999';
    process.env.IG_USER_ID = ACCOUNT;
    await pool.query('DELETE FROM app_tokens');
    (await import('../lib/token.js'))._resetTokenCache();
    (await import('../lib/instagram.js'))._resetAccountCache();

    following.set('igsid-800', true);
    calls.length = 0;
    await post(commentEvent('c50', 'igsid-800', 'JOURNAL'));
    const dm = dms()[0];
    assert.equal(dm.host, 'graph.facebook.com');
    assert.equal(dm.auth, 'Bearer EAAYsystemUserTOKEN999');
    assert.equal(dm.path, `/v24.0/${ACCOUNT}/messages`);

    calls.length = 0;
    const res = await mod.cron.GET(new Request('https://s/api/cron/refresh-token', { headers: { authorization: 'Bearer cron-secret-789' } }));
    assert.equal(res.status, 200);
    assert.equal(calls.filter((c) => c.path === '/refresh_access_token').length, 0, 'no refresh attempted');

    process.env.IG_ACCESS_TOKEN = saved;
    delete process.env.IG_USER_ID;
    (await import('../lib/token.js'))._resetTokenCache();
    (await import('../lib/instagram.js'))._resetAccountCache();
  });

  test('weekly cron refreshes and stores the token encrypted; new token is used after', async () => {
    const denied = await mod.cron.GET(new Request('https://s/api/cron/refresh-token'));
    assert.equal(denied.status, 401);

    const res = await mod.cron.GET(new Request('https://s/api/cron/refresh-token', { headers: { authorization: 'Bearer cron-secret-789' } }));
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.equal(body.ok, true);
    assert.ok(!JSON.stringify(body).includes('IGAA'), 'token not returned');

    const row = (await pool.query('SELECT ciphertext FROM app_tokens')).rows[0];
    assert.ok(!row.ciphertext.includes('IGAArefreshedTOKEN000'), 'stored encrypted');

    following.set('igsid-600', true);
    calls.length = 0;
    await post(commentEvent('c40', 'igsid-600', 'CATMOM'));
    assert.equal(dms()[0].auth, 'Bearer IGAArefreshedTOKEN000');

    // Pasting a brand-new token into the env var overrides the stored one
    process.env.IG_ACCESS_TOKEN = 'IGAAbrandNewManualTOKEN';
    (await import('../lib/token.js'))._resetTokenCache();
    following.set('igsid-700', true);
    calls.length = 0;
    await post(commentEvent('c41', 'igsid-700', 'CATMOM'));
    assert.equal(dms()[0].auth, 'Bearer IGAAbrandNewManualTOKEN');
  });
});
