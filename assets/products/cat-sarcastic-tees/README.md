# Cat Sarcasm T-Shirt PNGs

The homepage's T-Shirt PNGs card (`index.html`) expects 3 images in this exact folder, named:

```
cat-quote-01.png
cat-quote-02.png
cat-quote-03.png
```

(You have 6 total in the Canva design — feel free to swap in your 3 favorites, or add more `<img>` slots to the `.mini-gallery` block in `index.html` for all 6.)

## Why they're not already here

This build environment's network is locked down to an allowlist and can't pull files directly from Canva's export servers — so the images couldn't be downloaded automatically. Grab them yourself (takes under a minute):

1. Open the design in Canva: **https://www.canva.com/d/nbaWQYgfXxmNK0n** ("Cat Sarcasm Tshirt Quotes 12x12 inches")
2. **Share → Download**
3. File type: **PNG**, check **Transparent background**, select **All pages**
4. Unzip and rename the 3 (or 6) you want into this folder using the filenames above

Once they're in place, the homepage gallery will pick them up automatically — the fallback 🐈‍⬛ emoji tiles disappear as soon as a real file loads at that path.

## Full product listings

For the actual Payhip product PNGs (full-resolution, not the homepage preview thumbnails), export each page individually at full size and upload those to your Payhip product files — the homepage only needs small preview crops.
