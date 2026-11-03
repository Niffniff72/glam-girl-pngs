// Netlify wrapper → https://<your-site>/go/<code>  (tracked short links)
import { GET } from '../../api/go.js';

export default async (request, context) => {
  const url = new URL(request.url);
  url.searchParams.set('code', context.params?.code ?? '');
  return GET(new Request(url, { headers: request.headers }));
};

export const config = { path: '/go/:code' };
