import {
  createCipheriv,
  createDecipheriv,
  createHmac,
  hkdfSync,
  randomBytes,
  randomInt,
  timingSafeEqual,
} from 'node:crypto';

/** Constant-time string comparison. */
export function safeEqual(a, b) {
  const ab = Buffer.from(String(a));
  const bb = Buffer.from(String(b));
  if (ab.length !== bb.length) return false;
  return timingSafeEqual(ab, bb);
}

/**
 * Verify Meta's X-Hub-Signature-256 header: "sha256=<hex HMAC of raw body>".
 * Must be computed over the exact raw bytes Meta sent, before JSON parsing.
 */
export function verifySignature(rawBody, header, appSecret) {
  if (!header || !appSecret || !header.startsWith('sha256=')) return false;
  const expected = createHmac('sha256', appSecret).update(rawBody, 'utf8').digest('hex');
  return safeEqual(header.slice('sha256='.length), expected);
}

// ---- Token encryption at rest -------------------------------------------
// Key is derived from IG_APP_SECRET so there's no extra secret to manage.

function tokenKey(appSecret) {
  return Buffer.from(hkdfSync('sha256', appSecret, 'glam-dm-engine', 'ig-token-at-rest', 32));
}

export function encryptToken(plaintext, appSecret) {
  const iv = randomBytes(12);
  const cipher = createCipheriv('aes-256-gcm', tokenKey(appSecret), iv);
  const ct = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
  return ['v1', iv.toString('base64'), cipher.getAuthTag().toString('base64'), ct.toString('base64')].join(':');
}

export function decryptToken(blob, appSecret) {
  const [version, iv, tag, ct] = String(blob).split(':');
  if (version !== 'v1') throw new Error('Unknown token format');
  const decipher = createDecipheriv('aes-256-gcm', tokenKey(appSecret), Buffer.from(iv, 'base64'));
  decipher.setAuthTag(Buffer.from(tag, 'base64'));
  return Buffer.concat([decipher.update(Buffer.from(ct, 'base64')), decipher.final()]).toString('utf8');
}

// ---- Short codes ---------------------------------------------------------
const ALPHABET = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789';

export function shortCode(length = 7) {
  let out = '';
  for (let i = 0; i < length; i++) out += ALPHABET[randomInt(ALPHABET.length)];
  return out;
}
