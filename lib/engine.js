// The comment-to-DM flow.
//
//   comment "GLAM" ──► private-reply DM [Send me the link] + public reply
//                          │ tap
//                          ▼
//                 follows you? ──no──► "follow me first" [I followed] ──tap──┐
//                          │ yes                                            │
//                          ◄────────────────────────────────────────────────┘
//                 needs email? ──yes──► "drop your email" ──► Kit + tag ──┐
//                          │ no                                           │
//                          ▼                                              │
//                 link DM with tracked short link  ◄──────────────────────┘
//
// Every DM step is recorded in ig_sent_messages, so no step is ever sent twice.

import * as db from './db.js';
import { siteUrl } from './env.js';
import * as ig from './instagram.js';
import { subscribeAndTag } from './kit.js';
import { KEYWORDS, fill, keywordByName, matchKeyword, messagesFor } from './keywords.js';
import { log } from './log.js';

const MAX_FOLLOW_RETRIES = 3;
const MAX_EMAIL_RETRIES = 2;
const EMAIL_RE = /[A-Z0-9._%+-]+@[A-Z0-9-]+(?:\.[A-Z0-9-]+)*\.[A-Z]{2,}/i;

export const PAYLOAD = {
  link: (leadId) => `LINK:${leadId}`,
  followed: (leadId) => `FOLLOWED:${leadId}`,
};

// ---------------------------------------------------------------------------
// Entry point: a verified webhook payload
// ---------------------------------------------------------------------------

export async function processWebhook(payload, { keywords = KEYWORDS } = {}) {
  if (payload?.object !== 'instagram') return;

  for (const entry of payload.entry ?? []) {
    for (const change of entry.changes ?? []) {
      if (change.field !== 'comments' && change.field !== 'live_comments') continue;
      await safely('comment', () => handleComment(change.value, entry.id, keywords));
    }
    for (const event of entry.messaging ?? []) {
      await safely('messaging', () => handleMessaging(event, entry.id, keywords));
    }
  }
}

async function safely(kind, fn) {
  try {
    await fn();
  } catch (err) {
    log.error(`engine.${kind}_failed`, err);
  }
}

// ---------------------------------------------------------------------------
// Comments
// ---------------------------------------------------------------------------

async function handleComment(value, entryAccountId, keywords) {
  const commentId = value?.id;
  const from = value?.from;
  if (!commentId || !from?.id) return;

  const account = await ig.getAccount();
  if (from.id === account.id || from.id === entryAccountId || from.username === account.username) return;

  const kw = matchKeyword(value.text, keywords);
  if (!kw) return;
  const mediaId = value.media?.id;
  if (kw.mediaIds?.length && !kw.mediaIds.includes(mediaId)) return;

  if (!(await db.claimEvent(`comment:${commentId}`, 'comment'))) return; // Meta retry

  const lead = await db.createLead({
    igUserId: from.id,
    username: from.username,
    keyword: kw.keyword,
    source: 'comment',
    commentId,
    mediaId,
    commentText: value.text?.slice(0, 1000),
  });
  if (!lead) {
    log.info('comment.already_handled', { keyword: kw.keyword, commentId });
    return;
  }

  const m = messagesFor(kw);
  const vars = await templateVars(kw);

  await sendOnce(lead, 'opener', async () => {
    try {
      await ig.sendPrivateReply(
        commentId,
        ig.buttonMessage(fill(m.opener, vars), [ig.postbackButton(m.openerButton, PAYLOAD.link(lead.id))]),
      );
    } catch (err) {
      log.warn('comment.button_reply_failed_using_text', { error: err.message });
      await ig.sendPrivateReply(commentId, ig.textMessage(fill(m.openerFallback, vars)));
    }
  });

  try {
    const replies = m.publicReplies;
    await ig.replyToComment(commentId, replies[hash(commentId) % replies.length]);
  } catch (err) {
    log.error('comment.public_reply_failed', err, { commentId });
  }

  log.info('comment.opened', { leadId: lead.id, keyword: kw.keyword });
}

// ---------------------------------------------------------------------------
// DMs: button taps (postbacks) and typed messages
// ---------------------------------------------------------------------------

async function handleMessaging(event, entryAccountId, keywords) {
  const sender = event?.sender?.id;
  if (!sender) return;
  const account = await ig.getAccount();
  if (sender === account.id || sender === entryAccountId) return;
  if (event.message?.is_echo || event.message?.is_deleted) return;

  const mid = event.postback?.mid ?? event.message?.mid;
  if (mid && !(await db.claimEvent(`mid:${mid}`, event.postback ? 'postback' : 'message'))) return;

  // Button tap
  if (event.postback?.payload) {
    const [action, rawId] = String(event.postback.payload).split(':');
    if (action !== 'LINK' && action !== 'FOLLOWED') return;
    const lead = await db.getLead(Number(rawId));
    if (!lead || lead.ig_user_id !== sender) return; // not theirs
    const kw = keywordByName(lead.keyword, keywords);
    if (!kw) return;
    await advance(lead, kw);
    return;
  }

  const text = event.message?.text?.trim();
  if (!text) return;

  // Waiting on an email from this person?
  const awaiting = await db.findLeadAwaitingEmail(sender);
  if (awaiting) {
    const kw = keywordByName(awaiting.keyword, keywords);
    if (kw) return handleEmailReply(awaiting, kw, text);
  }

  // Typed the keyword in DMs (or replied to the text-only fallback opener)
  const kw = matchKeyword(text, keywords);
  if (!kw) return; // ordinary conversation — leave it for a human

  let lead = await db.findLead(sender, kw.keyword);
  if (!lead) {
    lead = await db.createLead({ igUserId: sender, keyword: kw.keyword, source: 'dm' });
    if (!lead) lead = await db.findLead(sender, kw.keyword); // lost a race
  }
  if (lead) await advance(lead, kw);
}

// ---------------------------------------------------------------------------
// The state machine
// ---------------------------------------------------------------------------

async function advance(lead, kw) {
  const m = messagesFor(kw);
  const vars = await templateVars(kw);

  if (lead.status === 'delivered') {
    // They tapped again after getting it. Re-send once, then stay quiet.
    await sendOnce(lead, 'link_again', () => sendLink(lead, fill(m.deliveryAgain, vars), kw));
    return;
  }

  if (kw.requireFollow !== false) {
    let follows = true;
    try {
      ({ follows } = await ig.isFollower(lead.ig_user_id));
    } catch (err) {
      // If Instagram won't tell us, don't punish the person — let them through.
      log.error('follow_check_failed_allowing', err, { leadId: lead.id });
    }
    if (!follows) {
      await db.updateLead(lead.id, { status: 'awaiting_follow' });
      const asked = await db.countSteps(lead.id, 'follow_gate');
      if (asked > MAX_FOLLOW_RETRIES) return;
      const text = asked === 0 ? fill(m.followGate, vars) : fill(m.followRetry, vars);
      await sendOnce(lead, asked === 0 ? 'follow_gate' : `follow_gate_retry_${asked}`, () =>
        ig.sendMessage(
          lead.ig_user_id,
          ig.buttonMessage(text, [ig.postbackButton(m.followButton, PAYLOAD.followed(lead.id))]),
        ),
      );
      return;
    }
  }

  if (kw.needsEmail && !lead.email) {
    await db.updateLead(lead.id, { status: 'awaiting_email' });
    await sendOnce(lead, 'ask_email', () => ig.sendMessage(lead.ig_user_id, ig.textMessage(fill(m.askEmail, vars))));
    return;
  }

  await deliver(lead, kw);
}

async function handleEmailReply(lead, kw, text) {
  const m = messagesFor(kw);
  const vars = await templateVars(kw);
  const email = text.match(EMAIL_RE)?.[0]?.toLowerCase();

  if (!email) {
    const tries = await db.countSteps(lead.id, 'email_retry');
    if (tries >= MAX_EMAIL_RETRIES) return;
    await sendOnce(lead, `email_retry_${tries + 1}`, () =>
      ig.sendMessage(lead.ig_user_id, ig.textMessage(fill(m.emailRetry, vars))),
    );
    return;
  }

  let kitStatus = 'ok';
  try {
    await subscribeAndTag(email, { tagId: kw.kitTagId, tagName: kw.kitTag });
  } catch (err) {
    // Still give them the link — the email is saved in the DB so you can re-add it.
    kitStatus = 'error';
    log.error('kit.subscribe_failed', err, { leadId: lead.id });
  }

  const updated = await db.updateLead(lead.id, { email, kit_status: kitStatus });
  await deliver(updated, kw);
}

async function deliver(lead, kw) {
  const m = messagesFor(kw);
  const vars = await templateVars(kw);
  const sent = await sendOnce(lead, 'link', () => sendLink(lead, fill(m.delivery, vars), kw));
  if (sent) {
    await db.updateLead(lead.id, { status: 'delivered', link_sent_at: new Date() });
    log.info('lead.delivered', { leadId: lead.id, keyword: kw.keyword });
  }
}

async function sendLink(lead, text, kw) {
  const target = absoluteUrl(kw.url);
  await db.updateLead(lead.id, { target_url: target });
  const code = await db.ensureShortCode(lead.id);
  const shortUrl = `${siteUrl()}/go/${code}`;
  const m = messagesFor(kw);
  await ig.sendMessage(
    lead.ig_user_id,
    ig.buttonMessage(text, [ig.urlButton(kw.linkButton ?? m.linkButton ?? 'Open the link', shortUrl)]),
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Run `send` only if this step hasn't been sent to this lead before. */
async function sendOnce(lead, step, send) {
  if (!(await db.claimStep(lead.id, step))) return false;
  try {
    await send();
    return true;
  } catch (err) {
    await db.releaseStep(lead.id, step); // let a later tap try again
    throw err;
  }
}

async function templateVars(kw) {
  const { username } = await ig.getAccount();
  return { name: kw.name, keyword: kw.keyword, handle: username };
}

function absoluteUrl(url) {
  return /^https?:\/\//i.test(url) ? url : `${siteUrl()}${url.startsWith('/') ? '' : '/'}${url}`;
}

function hash(s) {
  let h = 0;
  for (const ch of String(s)) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return h;
}
