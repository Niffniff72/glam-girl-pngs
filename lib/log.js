// Structured logger that scrubs secrets. Every log line goes through redact(),
// so even an error message that somehow echoes a token or key gets masked.

const SECRET_ENV_VARS = [
  'IG_APP_SECRET',
  'IG_ACCESS_TOKEN',
  'IG_VERIFY_TOKEN',
  'KIT_API_KEY',
  'CRON_SECRET',
  'DATABASE_URL',
];

const runtimeSecrets = new Set();

/** Register a value (e.g. a freshly refreshed token) so it is never logged. */
export function registerSecret(value) {
  if (typeof value === 'string' && value.length >= 8) runtimeSecrets.add(value);
}

export function redact(input) {
  let out = String(input);
  const secrets = [...runtimeSecrets];
  for (const name of SECRET_ENV_VARS) {
    const v = process.env[name];
    if (v && v.length >= 8) secrets.push(v);
  }
  for (const s of secrets) out = out.split(s).join('[redacted]');
  // Belt and braces: mask anything shaped like a token in a query string.
  out = out.replace(/(access_token=)[^&\s"]+/gi, '$1[redacted]');
  return out;
}

function write(level, event, fields = {}) {
  const line = redact(JSON.stringify({ level, event, ...fields, at: new Date().toISOString() }));
  (level === 'error' ? console.error : console.log)(line);
}

export const log = {
  info: (event, fields) => write('info', event, fields),
  warn: (event, fields) => write('warn', event, fields),
  error: (event, err, fields = {}) =>
    write('error', event, { ...fields, error: err?.message ?? String(err) }),
};
