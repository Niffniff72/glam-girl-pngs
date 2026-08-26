# Payhip Setup Guide — Glam Girl PNGs

Your website (this repo) is the storefront buyers actually see and browse. Payhip runs quietly in the background — it's just the engine that takes payment, shows the Pay-in-4 option when eligible, and delivers the PNG files. Buyers click a "Shop" button on your site, land on a Payhip checkout page for a second, then get their download. They never need to know what Payhip is.

You have a Payhip account but no products yet — here's exactly what to set up so the site's buttons have real links to point to.

## 1. Create your 3 categories (once)

In Payhip: **Products → Categories** (or from a product's edit screen, under "Category")

Create three:
- `Tumbler Wraps`
- `T-Shirt PNGs`
- `Journal Covers`

These give you clean filtered links like `payhip.com/YourStoreName/category/tumbler-wraps` — this is what the site's "Shop Tumbler Wraps," "Shop T-Shirt PNGs," and "Shop Journal Covers" buttons should point to, so a click lands on just that collection instead of your whole catalog.

## 2. Create a product

**Products → New Product → Digital Product**, then:

1. **Title** — e.g. "Sarcastic Cat Quotes — T-Shirt PNG Bundle"
2. **Files** — upload the PNGs (zip them if it's a multi-design bundle)
3. **Price** — set it; USD
4. **Category** — assign it to the matching one from step 1
5. **Description** — this is a good place to restate the commercial-use license in short form (link back to your site's `terms.html` if you want the full version), e.g.:
   > Instant digital download. Commercial use included — print and sell physical products you make with this design. You may not resell or redistribute the PNG file itself.
6. **Cover image** — use one of the actual design PNGs as the thumbnail

Repeat for each product/bundle. You don't need dozens of individual products on day one — 3-6 solid bundles (one or two per category) is plenty to launch with; add more as new drops go live.

## 3. Turn on the payment methods (this is what makes Pay-in-4 show up)

**Settings → Payments** in Payhip:
- Connect **PayPal** — this is what surfaces "Pay in 4" automatically at checkout for eligible U.S. orders. You don't configure Pay-in-4 directly; PayPal decides eligibility per order and shows it on its own when connected.
- Connect **Stripe** (or leave card payments on whatever Payhip has enabled by default) so people who don't want PayPal can still pay by card.

## 4. Set the order confirmation email

**Settings → Notifications** (or on the product itself, depending on your Payhip plan) — there's a field for a custom thank-you/confirmation message. Paste in the **Order Confirmation Email** copy from `content/marketing-kit.md` (swap in the real download-link merge tag Payhip gives you).

## 5. Grab your real links

Once products exist, copy:
- Your **category URLs** (3 of them) → these replace `#payhip-tumblers`, `#payhip-tees`, `#payhip-journals` in `index.html`
- Your **main store URL** → replaces `#payhip-shop` (used for the hero CTA, closing CTA, and nav "Shop Now" button)

Find every `href="#payhip-` in `index.html` (there are about 6) and swap in the real URLs.

## 6. Test before you announce it

Payhip lets you test checkout without going fully live — do a $0 test coupon or a small real purchase yourself to confirm the download link works and the confirmation email fires correctly. Then update `README.md`'s checklist to check this item off.

## Quick recap of what's already done vs. what's on you

| Done in the code | Needs you in Payhip |
|---|---|
| Brand site, animations, layout | 3 categories created |
| Payment section copy/design | Products uploaded with files + prices |
| Legal pages | PayPal connected (for Pay-in-4 to appear) |
| Confirmation email copy written | Confirmation email pasted into Payhip settings |
| Comment-keyword DM scripts written | Real product/category links swapped into `index.html` |
