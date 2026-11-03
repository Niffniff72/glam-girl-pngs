// Read configuration from environment variables only. Values are never logged.

export function env(name, { optional = false, fallback } = {}) {
  const value = process.env[name];
  if (value !== undefined && value !== '') return value;
  if (fallback !== undefined) return fallback;
  if (optional) return undefined;
  throw new Error(`Missing required environment variable ${name}`);
}

export const graphVersion = () => env('IG_GRAPH_VERSION', { fallback: 'v24.0' });

/** Public base URL of the site, no trailing slash. Used for short links. */
// Netlify sets URL automatically, so SITE_URL is only needed for a custom domain.
export const siteUrl = () => env('SITE_URL', { fallback: process.env.URL }).replace(/\/+$/, '');
