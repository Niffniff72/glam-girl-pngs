// Kit (formerly ConvertKit) API v4. Auth via X-Kit-Api-Key header.

import { env } from './env.js';

const BASE = 'https://api.kit.com/v4';

async function kit(path, { method = 'GET', body } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      'X-Kit-Api-Key': env('KIT_API_KEY'),
      Accept: 'application/json',
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
    signal: AbortSignal.timeout(10_000),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = Array.isArray(data.errors) ? data.errors.join('; ') : res.statusText;
    throw new Error(`Kit API ${res.status}: ${detail}`);
  }
  return data;
}

const tagIdCache = new Map();

/** Look up a tag by name, creating it if it doesn't exist yet. */
async function resolveTagId(name) {
  const key = name.trim().toLowerCase();
  if (tagIdCache.has(key)) return tagIdCache.get(key);

  let after;
  do {
    const qs = new URLSearchParams({ per_page: '1000', ...(after ? { after } : {}) });
    const page = await kit(`/tags?${qs}`);
    const hit = page.tags?.find((t) => t.name.trim().toLowerCase() === key);
    if (hit) {
      tagIdCache.set(key, hit.id);
      return hit.id;
    }
    after = page.pagination?.has_next_page ? page.pagination.end_cursor : undefined;
  } while (after);

  const created = await kit('/tags', { method: 'POST', body: { name } });
  tagIdCache.set(key, created.tag.id);
  return created.tag.id;
}

/** Add (or update) a subscriber and tag them. */
export async function subscribeAndTag(email, { tagId, tagName }) {
  await kit('/subscribers', { method: 'POST', body: { email_address: email } });
  const id = tagId ?? (tagName ? await resolveTagId(tagName) : undefined);
  if (id) await kit(`/tags/${id}/subscribers`, { method: 'POST', body: { email_address: email } });
}
