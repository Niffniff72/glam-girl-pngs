// Thin client for Meta's Instagram API.
//
// Works with both token types Meta hands out:
//   - "IGAA…" tokens (older Instagram Login apps)    → graph.instagram.com
//   - "EAA…"  tokens (Unified login / system users)  → graph.facebook.com
// The host is picked from the token automatically (override with IG_GRAPH_HOST).
// The token travels in the Authorization header, never in a logged URL.

import { env, graphVersion } from './env.js';
import { getAccessToken } from './token.js';

/** Which Graph host a token belongs to. */
export function graphHostFor(token) {
  const override = env('IG_GRAPH_HOST', { optional: true });
  if (override) return override.replace(/^https?:\/\//, '').replace(/\/+$/, '');
  return String(token).startsWith('IG') ? 'graph.instagram.com' : 'graph.facebook.com';
}

export class GraphError extends Error {
  constructor(status, err) {
    super(`Instagram API ${status}: ${err?.message ?? 'unknown error'}`);
    this.status = status;
    this.code = err?.code;
    this.subcode = err?.error_subcode;
  }
}

async function graph(path, { method = 'GET', query, body } = {}) {
  const token = await getAccessToken();
  const url = new URL(`https://${graphHostFor(token)}/${graphVersion()}/${path}`);
  for (const [k, v] of Object.entries(query ?? {})) url.searchParams.set(k, v);

  const res = await fetch(url, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
    signal: AbortSignal.timeout(10_000),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.error) throw new GraphError(res.status, data.error);
  return data;
}

// ---- Account --------------------------------------------------------------

let account = null;

/** Your professional account's ID + username (cached per function instance). */
export async function getAccount() {
  if (account) return account;
  const envId = env('IG_USER_ID', { optional: true });
  const envName = env('IG_USERNAME', { optional: true });
  if (envId && envName) return (account = { id: envId, username: envName });

  if (envId) {
    // Unified login / system-user tokens: /me is the system user, not Instagram,
    // so look the Instagram account up by its ID instead.
    const ig = await graph(envId, { query: { fields: 'username' } });
    return (account = { id: envId, username: envName ?? ig.username });
  }
  const me = await graph('me', { query: { fields: 'user_id,username' } });
  if (!me.user_id) {
    throw new Error('Set IG_USER_ID to your Instagram account ID (needed for this token type)');
  }
  return (account = { id: String(me.user_id), username: envName ?? me.username });
}

export function _resetAccountCache() {
  account = null;
}

// ---- Message builders -----------------------------------------------------

export const textMessage = (text) => ({ text });

export const buttonMessage = (text, buttons) => ({
  attachment: {
    type: 'template',
    payload: { template_type: 'button', text: text.slice(0, 640), buttons },
  },
});

export const postbackButton = (title, payload) => ({ type: 'postback', title: title.slice(0, 20), payload });
export const urlButton = (title, url) => ({ type: 'web_url', title: title.slice(0, 20), url });

// ---- Sends ----------------------------------------------------------------

/** Private reply: the one DM Instagram lets you send in response to a comment. */
export async function sendPrivateReply(commentId, message) {
  const { id } = await getAccount();
  return graph(`${id}/messages`, { method: 'POST', body: { recipient: { comment_id: commentId }, message } });
}

/** Normal DM to someone who's in an open conversation with you. */
export async function sendMessage(igsid, message) {
  const { id } = await getAccount();
  return graph(`${id}/messages`, { method: 'POST', body: { recipient: { id: igsid }, message } });
}

/** Public reply under their comment. */
export async function replyToComment(commentId, text) {
  return graph(`${commentId}/replies`, { method: 'POST', body: { message: text } });
}

/** Does this person follow you? Uses the User Profile API. */
export async function isFollower(igsid) {
  const profile = await graph(igsid, { query: { fields: 'username,is_user_follow_business' } });
  return { follows: profile.is_user_follow_business === true, username: profile.username };
}
