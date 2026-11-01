-- Instagram comment-to-DM engine schema (Postgres).
-- Safe to run repeatedly: `npm run db:migrate`.

-- Every webhook event we've handled (comment IDs, message/postback mids).
-- Meta retries webhooks, so this stops the same event being processed twice.
CREATE TABLE IF NOT EXISTS ig_processed_events (
  event_id    text PRIMARY KEY,
  kind        text NOT NULL,
  received_at timestamptz NOT NULL DEFAULT now()
);

-- One row per person per keyword. The UNIQUE constraint is what guarantees
-- nobody gets the same keyword flow twice, even if they comment 10 times.
CREATE TABLE IF NOT EXISTS ig_leads (
  id               bigserial PRIMARY KEY,
  ig_user_id       text NOT NULL,             -- Instagram-scoped user ID (IGSID)
  username         text,
  keyword          text NOT NULL,
  source           text NOT NULL DEFAULT 'comment',  -- 'comment' | 'dm'
  comment_id       text,
  media_id         text,
  comment_text     text,
  status           text NOT NULL DEFAULT 'opened',
    -- opened → awaiting_follow → awaiting_email → delivered
  email            text,
  kit_status       text,                      -- 'ok' | 'error' | NULL
  target_url       text,                      -- where the short link points
  short_code       text UNIQUE,
  click_count      integer NOT NULL DEFAULT 0,
  first_clicked_at timestamptz,
  link_sent_at     timestamptz,
  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now(),
  UNIQUE (ig_user_id, keyword)
);
CREATE INDEX IF NOT EXISTS ig_leads_user_status_idx ON ig_leads (ig_user_id, status);

-- Each individual DM step sent to a lead. Primary key = never the same step twice.
CREATE TABLE IF NOT EXISTS ig_sent_messages (
  lead_id bigint NOT NULL REFERENCES ig_leads(id) ON DELETE CASCADE,
  step    text   NOT NULL,
  sent_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (lead_id, step)
);

-- Short-link clicks (/go/<code>).
CREATE TABLE IF NOT EXISTS link_clicks (
  id         bigserial PRIMARY KEY,
  short_code text NOT NULL,
  lead_id    bigint REFERENCES ig_leads(id) ON DELETE SET NULL,
  clicked_at timestamptz NOT NULL DEFAULT now(),
  user_agent text,
  referer    text
);
CREATE INDEX IF NOT EXISTS link_clicks_code_idx ON link_clicks (short_code);

-- The refreshed Instagram token, encrypted (AES-256-GCM) — never stored in plain text.
CREATE TABLE IF NOT EXISTS app_tokens (
  name         text PRIMARY KEY,
  ciphertext   text NOT NULL,
  seed_hash    text,          -- fingerprint of IG_ACCESS_TOKEN this row descends from
  refreshed_at timestamptz NOT NULL DEFAULT now(),
  expires_at   timestamptz
);
