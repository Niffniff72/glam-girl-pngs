// Netlify wrapper → https://<your-site>/api/instagram/webhook
import { GET, POST } from '../../api/instagram/webhook.js';

export default async (request) => {
  if (request.method === 'GET') return GET(request);
  if (request.method === 'POST') return POST(request);
  return new Response('Method not allowed', { status: 405 });
};

export const config = { path: '/api/instagram/webhook' };
