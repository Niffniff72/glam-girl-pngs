// ============================================================================
//  YOUR KEYWORDS, LINKS, AND DM COPY — this is the only file you need to edit.
// ============================================================================
//
//  keyword        What people comment (case-insensitive, whole word: "glam!!" and
//                 "GLAM please 🙏" both match, "glamorous" does not).
//  name           What the freebie/product is called inside the DMs.
//  url            Where the link goes. Starts with "/" = a page on this site.
//  needsEmail     true  → ask for their email in the DM, add to Kit, then send link.
//                 false → send the link right away.
//  requireFollow  true  → must follow you before they get the link.
//  kitTag         Kit tag name to apply (created automatically if it doesn't exist).
//  mediaIds       Optional: only trigger on these post/Reel IDs. [] = any post.
//  linkButton     Text on the final link button (max 20 characters).
//
//  Any message below can be overridden per keyword with a `messages: { ... }`
//  object using the same keys as DEFAULT_MESSAGES.
// ============================================================================

export const KEYWORDS = [
  {
    keyword: 'GLAM',
    name: 'free Thank You Mini Cards PNG',
    url: '/assets/products/free-thank-you-cards/thank-you-mini-cards.png',
    needsEmail: true,
    requireFollow: true,
    kitTag: 'IG - GLAM freebie',
    mediaIds: [],
    linkButton: 'Get my freebie ✨',
  },
  {
    keyword: 'TUMBLER',
    name: 'Tumbler Wrap PNGs',
    url: 'https://payhip.com/b/3DSvO',
    needsEmail: false,
    requireFollow: true,
    kitTag: 'IG - TUMBLER',
    mediaIds: [],
    linkButton: 'Shop tumbler wraps',
  },
  {
    keyword: 'CATMOM',
    name: 'Cat Sarcasm tee PNGs',
    url: 'https://payhip.com/b/EYpyB',
    needsEmail: false,
    requireFollow: true,
    kitTag: 'IG - CATMOM',
    mediaIds: [],
    linkButton: 'Shop Cat Sarcasm 🐈‍⬛',
  },
  {
    keyword: 'JOURNAL',
    name: 'Journal Cover PNGs',
    url: 'https://payhip.com/b/n76AQ',
    needsEmail: false,
    requireFollow: true,
    kitTag: 'IG - JOURNAL',
    mediaIds: [],
    linkButton: 'Shop journal covers',
  },
];

// Placeholders: {name} {keyword} {handle} (your @username)
export const DEFAULT_MESSAGES = {
  // 1. Private-reply DM right after they comment (has the "Send me the link" button)
  opener:
    'Heyyy gorgeous! 🩷 Thanks for commenting {keyword} — your {name} is ready and waiting. Tap below and I\'ll send it right over ✨',
  openerButton: 'Send me the link',

  // Fallback if Instagram refuses the button version: plain text asking them to reply.
  openerFallback:
    'Heyyy gorgeous! 🩷 Thanks for commenting {keyword} — reply "{keyword}" right here and I\'ll send your {name} straight over ✨',

  // 2. Public replies under their comment (one is picked per comment so they don't all look identical)
  publicReplies: [
    'Sent! Check your DMs 🩷✨',
    'Sliding into your DMs now 💋',
    'On its way to your inbox, gorgeous ✨',
    'Check your DMs babe 🩷',
    'Just sent it — go peek at your DMs 👀✨',
  ],

  // 3. Not following yet
  followGate:
    'Okay wait — one tiny thing first 🙈 This one\'s just for my girls who follow along. Hit follow on @{handle}, then tap the button below and it\'s yours 🩷',
  followButton: 'I followed',
  followRetry:
    'Hmm, I\'m not seeing your follow yet 👀 Sometimes it takes a sec to show up — make sure you\'re following @{handle}, then tap again 🩷',

  // 4. Email capture (only for needsEmail: true)
  askEmail:
    'Yesss! 🎉 Last step — drop your best email right here and I\'ll send your {name} over this second. You\'ll also get first dibs on new drops + subscriber-only discounts 💌',
  emailRetry:
    'Hmm, that email doesn\'t look quite right 🤔 Can you type it one more time? Something like yourname@gmail.com 🩷',

  // 5. The link
  delivery: 'Here it is, gorgeous! 🩷 Your {name} is ready — go make something gorgeous ✨',
  deliveryAgain: 'Here\'s your {name} link again, babe 🩷',
};

// ---------------------------------------------------------------------------

export function messagesFor(kw) {
  return { ...DEFAULT_MESSAGES, ...(kw.messages ?? {}) };
}

export function fill(template, vars) {
  return template.replace(/\{(\w+)\}/g, (m, key) => (key in vars ? String(vars[key]) : m));
}

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/** Find the configured keyword contained in a comment/DM, or null. */
export function matchKeyword(text, keywords = KEYWORDS) {
  if (!text) return null;
  for (const kw of keywords) {
    const re = new RegExp(`(^|[^\\p{L}\\p{N}])${escapeRegExp(kw.keyword)}($|[^\\p{L}\\p{N}])`, 'iu');
    if (re.test(text)) return kw;
  }
  return null;
}

export function keywordByName(name, keywords = KEYWORDS) {
  return keywords.find((k) => k.keyword.toLowerCase() === String(name).toLowerCase()) ?? null;
}
