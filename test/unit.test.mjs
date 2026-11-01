import assert from 'node:assert/strict';
import { createHmac } from 'node:crypto';
import { test } from 'node:test';

process.env.IG_APP_SECRET = 'unit-test-app-secret-123';
process.env.KIT_API_KEY = 'unit-test-kit-key-456';

const { verifySignature, encryptToken, decryptToken, shortCode } = await import('../lib/crypto.js');
const { matchKeyword, fill } = await import('../lib/keywords.js');
const { redact, registerSecret } = await import('../lib/log.js');

test('signature: accepts a correct X-Hub-Signature-256, rejects anything else', () => {
  const body = '{"object":"instagram","entry":[]}';
  const sig = 'sha256=' + createHmac('sha256', 'secret').update(body).digest('hex');
  assert.equal(verifySignature(body, sig, 'secret'), true);
  assert.equal(verifySignature(body + ' ', sig, 'secret'), false);
  assert.equal(verifySignature(body, sig, 'wrong'), false);
  assert.equal(verifySignature(body, null, 'secret'), false);
  assert.equal(verifySignature(body, sig.replace('sha256=', 'sha1='), 'secret'), false);
});

test('keywords: whole-word, case-insensitive, emoji/punctuation tolerant', () => {
  const kws = [{ keyword: 'GLAM' }, { keyword: 'CATMOM' }];
  assert.equal(matchKeyword('glam', kws)?.keyword, 'GLAM');
  assert.equal(matchKeyword('GLAM!!! 🙏', kws)?.keyword, 'GLAM');
  assert.equal(matchKeyword('omg I need this. Glam please', kws)?.keyword, 'GLAM');
  assert.equal(matchKeyword('🩷catmom🩷', kws)?.keyword, 'CATMOM');
  assert.equal(matchKeyword('so glamorous', kws), null);
  assert.equal(matchKeyword('', kws), null);
});

test('fill: substitutes known placeholders and leaves unknown ones', () => {
  assert.equal(fill('Hi {name} from @{handle} {x}', { name: 'cards', handle: 'me' }), 'Hi cards from @me {x}');
});

test('token encryption round-trips and fails with the wrong secret', () => {
  const blob = encryptToken('IGAAtoken', 's1');
  assert.ok(!blob.includes('IGAAtoken'));
  assert.equal(decryptToken(blob, 's1'), 'IGAAtoken');
  assert.throws(() => decryptToken(blob, 's2'));
});

test('short codes look right', () => {
  const c = shortCode();
  assert.match(c, /^[A-Za-z0-9]{7}$/);
});

test('logger redacts env secrets, registered tokens, and access_token params', () => {
  registerSecret('IGAAruntimeToken999');
  const out = redact(
    'key=unit-test-kit-key-456 tok=IGAAruntimeToken999 url=https://x/?access_token=abc123&y=1 s=unit-test-app-secret-123',
  );
  assert.ok(!out.includes('unit-test-kit-key-456'));
  assert.ok(!out.includes('IGAAruntimeToken999'));
  assert.ok(!out.includes('abc123'));
  assert.ok(!out.includes('unit-test-app-secret-123'));
});
