# Instagram Comment-to-DM Engine

> **Meta update (Nov 2026):** new Meta apps can no longer use "API setup with Instagram login". They get **"API setup with Unified login"** instead, which issues a never-expiring **system-user token** (starts with `EAA`) used on `graph.facebook.com`. The engine detects the token type automatically. For a Unified-login app you need: `IG_ACCESS_TOKEN` (the EAA token), `IG_USER_ID` (your Instagram account ID), and `IG_APP_SECRET` = the **Meta app secret** (App settings → Basic). The weekly refresh is skipped for EAA tokens because they don't expire.

Built on Meta's **Instagram API with Instagram Login** (`graph.instagram.com`). You don't need a Facebook Page.

## How it works

```
Someone comments "GLAM"
  ├─ Private-reply DM: "Heyyy gorgeous! …" [Send me the link]
  └─ Public reply under their comment: "Sent! Check your DMs 🩷✨"

They tap [Send me the link]
  ├─ Not following you?  → "Hit follow on @you…" [I followed]   (re-checked on every tap)
  ├─ Freebie needs email? → "Drop your best email…" → added to Kit + tagged
  └─ Link DM with a button → https://yoursite.com/go/AbC12xy  → click counted → redirect
```

- **No double DMs.** Each person can only get each keyword's flow once (`UNIQUE(ig_user_id, keyword)`), and each DM step is logged and never sent twice. Meta's webhook retries are de-duplicated by comment ID and message ID.
- **Keywords also work in DMs.** If someone types `GLAM` straight into your DMs, they get the same flow.
- **If Kit is down**, they still get the link. The email is saved in the database with `kit_status = 'error'` so you can add it to Kit later.
- **If Instagram won't report follow status**, the person is let through instead of getting stuck.

## Files

| File | What it is |
|---|---|
| `lib/keywords.js` | **Edit this one.** Keywords, links, email yes/no, Kit tags, all the DM copy |
| `api/instagram/webhook.js` | Webhook. GET handles the `hub.challenge` handshake; POST checks `X-Hub-Signature-256` |
| `api/go.js` | Short-link redirect + click tracking (`/go/<code>`) |
| `api/cron/refresh-token.js` | Weekly token refresh for Vercel (Mondays, scheduled in `vercel.json`) |
| `netlify/functions/*.mjs` | Netlify versions of the three routes above (token refresh is scheduled in the file) |
| `netlify.toml` | Netlify build settings: copies only the storefront to `dist/` |
| `lib/engine.js` | The flow / state machine |
| `db/schema.sql` | Database tables |
| `scripts/stats.mjs` | `npm run stats` shows leads, emails, links sent, and clicks per keyword |

## Setup

### 1. Host on Netlify (free) — or Vercel Pro

The webhook needs server code, so GitHub Pages alone won't run it. **Netlify's free plan** allows business sites: sign in at app.netlify.com with GitHub, then **Add new project → Import an existing project → GitHub → glam-girl-pngs**. `netlify.toml` already has the build settings, so leave them as they are and click Deploy. Your site will be at `https://<name>.netlify.app`, and Netlify fills in `SITE_URL` for you. You only set it yourself when you add a custom domain.

(Vercel also works with no code changes, using `vercel.json`. Vercel's free Hobby plan isn't allowed for commercial sites, though, so a shop there needs Pro at $20/month.)

### 2. Database

Create a free Postgres database at **neon.tech** and copy the **pooled** connection string (the one with `-pooler` in the hostname). That's `DATABASE_URL`. Then create the tables once, either by pasting `db/schema.sql` into Neon's **SQL Editor** and clicking Run, or from a computer:

```
DATABASE_URL="<pooled connection string>" npm install && npm run db:migrate
```

### 3. Meta app

1. Go to developers.facebook.com → **Create app**, and pick the use case **"Manage messaging & content on Instagram"**.
2. Go to **Instagram → API setup with Instagram login**:
   - **Generate access tokens**: add your Instagram account (it must be a Business or Creator account) and copy the token. That's `IG_ACCESS_TOKEN`.
   - Copy the **Instagram app secret** from the same page. That's `IG_APP_SECRET`. This is *not* the "App secret" under Settings → Basic. Webhook signatures are signed with the Instagram one.
3. **Configure webhooks** on that page:
   - Callback URL: `https://YOURSITE.com/api/instagram/webhook`
   - Verify token: any random string you make up. Put the same value in `IG_VERIFY_TOKEN`.
   - Subscribe to: **comments**, **messages**, **messaging_postbacks**
4. Permissions used: `instagram_business_basic`, `instagram_business_manage_messages`, `instagram_business_manage_comments`.
5. In the **Instagram app** on your phone, go to Settings → Messages and story replies → Message controls → **Connected tools** → turn on **Allow access to messages**.
6. **Development mode only works for accounts that have a role on the app.** Comment from a tester account to try it out. For the public, submit App Review for Advanced Access on the three permissions above and switch the app to **Live**.

### 4. Kit

Go to Kit → Settings → Developer → **API keys (v4)** → create a key and put it in `KIT_API_KEY`. Tags listed in `kitTag` are created automatically the first time they're used.

### 5. Environment variables

Netlify: go to Site configuration → **Environment variables** and add everything in `.env.example`. You can skip `SITE_URL` (Netlify sets it) and `CRON_SECRET` (that's only for Vercel). **Trigger a new deploy** after adding variables.

## Token refresh

Long-lived tokens last 60 days. Every Monday the cron swaps the token for a fresh 60-day one and stores it **encrypted** in the `app_tokens` table. `IG_ACCESS_TOKEN` is only the starting token. If the token ever dies (for example, you change your Instagram password), generate a new one in Meta and paste it into `IG_ACCESS_TOKEN`. The app sees it's new and uses it instead of the stored one.

Notes: Meta only refreshes tokens at least 24 hours old, so the first Monday after setup may skip if you just generated it. That's fine, since there are about 8 more chances before expiry. You can check runs in Netlify → Logs → Functions → refresh-token.

## Instagram's rules to know

- A private reply can only be sent **within 7 days** of the comment, and **only once per comment**.
- Button titles are capped at 20 characters, and DM text at 640.
- After someone taps a button, you have a 24-hour window to message them, which this flow uses.

## Testing locally

```
npm install
npm test                                      # unit tests
TEST_DATABASE_URL=postgres://... npm test     # + full end-to-end flow (mocked Instagram/Kit)
```
