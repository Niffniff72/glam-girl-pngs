# Glam Girl PNGs

Landing page for **Glam Girl PNGs** — instant-download PNG designs for tumblers, tees, and journal covers. Static HTML/CSS/JS, no build step.

This site is the storefront buyers see and browse — it's a fully custom build on your own domain, not a Payhip-hosted page. Payhip only runs in the background as the checkout + file-delivery engine behind the "Shop" buttons; buyers never land on anything that looks like Payhip's own store.

## Structure

```
index.html          Homepage (hero, collections, trust section, payment/Pay-in-4, email opt-in, comment-keyword section)
privacy.html         Privacy Policy
terms.html            Terms & Conditions
refund.html           Refund / Delivery Policy
css/style.css         Brand styles (glossy pink/gold/black, all animations)
js/main.js             Sparkle field, scroll reveal, nav behavior, opt-in confetti
content/marketing-kit.md          Confirmation emails, DM scripts, comment-keyword automations
content/payhip-setup-guide.md     Step-by-step: create your Payhip categories/products and get the real links
assets/products/       Product preview images (see cat-sarcastic-tees/README.md)
```

## Before you launch — things to plug in

1. **Payhip products & links.** You have a Payhip account but no products listed yet — follow `content/payhip-setup-guide.md` to create your 3 categories and first products, then swap the real URLs into every `href="#payhip-..."` in `index.html` and the footer (`id="payhip-tumblers"`, `#payhip-tees`, `#payhip-journals`, `#payhip-shop`).
2. **Cat Sarcasm PNGs.** See `assets/products/cat-sarcastic-tees/README.md` — the network in this build environment couldn't pull the Canva export directly, so grab those 3 files from Canva and drop them in.
3. **Email opt-in form.** `index.html` → `.optin-form` — point the `action` at your Brevo signup form.
4. **Pay in 4.** The payment section is written around **PayPal Pay Later**, which shows up automatically at PayPal checkout for eligible U.S. orders once PayPal is connected in Payhip — see step 3 of the setup guide. Sellers don't configure Pay-in-4 directly; PayPal decides eligibility per order. If you'd rather offer Klarna or Afterpay instead/also, that depends on which processor Payhip has enabled in your account at the time — check Payhip's current payment settings, since this changes as they roll features out.
5. **Legal pages.** Contact email is set to `tdelaney671@gmail.com` and effective date to today. Update the business/legal name and website URL once your domain is live (search-replace `glamgirlpngs.com` placeholders if you add real domain references). These drafts are a starting point, not legal advice — worth a quick attorney review before launch, same as the original notes said.
6. **Social links.** Footer has placeholder Instagram/TikTok/Pinterest URLs (`@glamgirlpngs`) — update to your real handles.

## Brand

- **Colors:** black (`#0b0b0d`), hot pink (`#ff2f92`), gold (`#e8b64b`), cream accents.
- **Logo font:** Yellowtail (Google Fonts) — brush-script style, gold-to-pink shimmer gradient.
- **Headings/UI font:** Montserrat. **Body font:** Poppins.
- **Animations:** floating gradient blobs + twinkling sparkles in the hero, brush-stroke logo reveal, scroll-triggered fade-ins, glossy button shine sweep, Pay-in-4 progress dots, Instagram-style typing loop on the comment-keyword mockup, confetti burst on email signup. All animations respect `prefers-reduced-motion`.

## Running it locally

No build tools needed — open `index.html` in a browser, or serve the folder:

```
python3 -m http.server 8080
```

Then visit `http://localhost:8080`.

## Deploying

Any static host works — GitHub Pages, Netlify, Vercel, Cloudflare Pages. For GitHub Pages: Settings → Pages → deploy from this branch's root.
