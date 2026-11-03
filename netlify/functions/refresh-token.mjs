// Weekly Instagram token refresh. Netlify runs this on schedule; it has no public URL.
import { log } from '../../lib/log.js';
import { refreshAccessToken } from '../../lib/token.js';

export default async () => {
  try {
    const { expiresAt } = await refreshAccessToken();
    log.info('token.refreshed', { expiresAt });
  } catch (err) {
    log.error('token.refresh_failed', err);
  }
  return new Response('ok');
};

export const config = { schedule: '17 14 * * 1' }; // Mondays 14:17 UTC
