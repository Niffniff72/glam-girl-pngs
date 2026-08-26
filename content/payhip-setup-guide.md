# Payhip Setup Guide — Glam Girl PNGs

Your website (this repo) is the storefront buyers actually see and browse. Payhip runs quietly in the background — it's just the engine that takes payment, shows the Pay-in-4 option when eligible, and delivers the PNG files. Buyers click a "Shop" button on your site, land on a Payhip checkout page for a second, then get their download. They never need to know what Payhip is, and they never see your other 28 products from other niches — every button links to one specific product, not your general catalog.

Your existing account is **payhip.com/Digitalgalitis**. Every "Shop"/"Browse" button on the site currently points there as a placeholder — you're about to replace the 3 collection-card links with specific product links.

Payhip doesn't have a reliable custom-category filter on the free/basic plan, so skip categories entirely — it's simpler and just as effective to create one flagship **bundle product per collection** and link straight to it.

## 1. Add your first product (from the dashboard you're looking at)

Tap **+ Add New** next to "Your Products" → choose **Digital Product**, then:

1. **Title** — e.g. "Sarcastic Cat Quotes — T-Shirt PNG Bundle"
2. **Files** — upload the PNGs (zip them together if it's a multi-design bundle)
3. **Price** — set it in USD
4. **Description** — a good place to restate the commercial-use license in short form:
   > Instant digital download. Commercial use included — print and sell physical products you make with this design. You may not resell or redistribute the PNG file itself.
5. **Cover image** — use one of the actual design PNGs as the thumbnail
6. Save/Publish

Repeat 2 more times — one bundle for Tumbler Wraps, one for Journal Covers. You don't need dozens of individual products on day one; one solid bundle per collection is plenty to launch with. Add more later and just point the button at whichever listing you want featured.

## 2. Grab the link

Back on the dashboard, each product row has a **Share product** button (you can see it next to "Edit" on every row in your screenshot) — tap it to get that product's direct URL (`payhip.com/b/XXXXX`). That's the exact link each collection button needs.

## 3. Turn on the payment methods (this is what makes Pay-in-4 show up)

**Settings → Payments** in Payhip:
- Connect **PayPal** — this is what surfaces "Pay in 4" automatically at checkout for eligible U.S. orders. You don't configure Pay-in-4 directly; PayPal decides eligibility per order and shows it on its own when connected.
- Connect **Stripe** (or leave card payments on whatever Payhip has enabled by default) so people who don't want PayPal can still pay by card.

## 4. Set the order confirmation email

**Settings → Notifications** (or on the product itself, depending on your Payhip plan) — there's a field for a custom thank-you/confirmation message. Paste in the **Order Confirmation Email** copy from `content/marketing-kit.md` (swap in the real download-link merge tag Payhip gives you).

## 5. Swap the 3 collection links in the site

Every "Shop" button on the site currently points to your general store (`payhip.com/Digitalgalitis`) as a placeholder — that already works, it just sends people to your whole catalog (autism-awareness stuff and all) instead of the right collection.

Once you've got your 3 bundle products and their **Share product** links from step 2, open `index.html` and find these 3 lines (search for `card-link`):

```
<a href="https://payhip.com/Digitalgalitis" class="card-link">Shop Tumbler Wraps</a>
<a href="https://payhip.com/Digitalgalitis" class="card-link">Shop T-Shirt PNGs</a>
<a href="https://payhip.com/Digitalgalitis" class="card-link">Shop Journal Covers</a>
```

Replace each `https://payhip.com/Digitalgalitis` with that product's own `payhip.com/b/XXXXX` link. The rest of the "Shop"/"Browse" buttons (nav, hero, payment section, closing CTA) can stay pointed at the general store — that's normal for a "browse everything" button.

## 6. Test before you announce it

Payhip lets you test checkout without going fully live — do a $0 test coupon or a small real purchase yourself to confirm the download link works and the confirmation email fires correctly. Then update `README.md`'s checklist to check this item off.

## Quick recap of what's already done vs. what's on you

| Done in the code | Needs you in Payhip |
|---|---|
| Brand site, animations, layout | 3 bundle products created (1 per collection) |
| Payment section copy/design | PayPal connected (for Pay-in-4 to appear) |
| Legal pages | Confirmation email pasted into Payhip settings |
| Confirmation email copy written | 3 "Share product" links swapped into `index.html` |
| Comment-keyword DM scripts written | |
