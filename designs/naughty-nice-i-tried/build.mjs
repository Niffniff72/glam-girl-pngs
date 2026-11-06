// "Naughty / Nice / I Tried" — chenille varsity patch Christmas tee design.
// Usage: node designs/naughty-nice-i-tried/build.mjs <fontsDir>
// Renders a transparent 4500x4950 PNG (15"x16.5" at 300 DPI) with Playwright.
import { readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');

const FONTS = process.argv[2];
const OUT = new URL('../../assets/products/naughty-nice-i-tried/', import.meta.url);
const font = (pkg, file) =>
  readFileSync(`${FONTS}/node_modules/@fontsource/${pkg}/files/${file}`).toString('base64');

const W = 1500, H = 1650, SCALE = 3;
const C = {
  black: '#16121a', cream: '#f7ecd9', gold: '#e8b64b', goldDeep: '#b8862a',
  pink: '#ff2f92', pinkDeep: '#c4166a', red: '#d6243c', green: '#1f8a55', white: '#fffaf2',
};

// Felt edge + stitch + chenille fill, using the layered-stroke trick:
// felt (wide) → dashed thread (medium) → felt cover (narrow) → fuzzy chenille.
function chenilleText({ x, y, text, size, width, fill, edge, thread, font = 'Varsity', anchor = 'start' }) {
  const t = (extra) =>
    `<text x="${x}" y="${y}" font-family="${font}" font-size="${size}" textLength="${width}" lengthAdjust="spacingAndGlyphs" text-anchor="${anchor}" ${extra}>${text}</text>`;
  return `
    ${t(`fill="${edge}" stroke="${edge}" stroke-width="38" stroke-linejoin="round" filter="url(#felt)"`)}
    ${t(`fill="none" stroke="${thread}" stroke-width="25" stroke-linejoin="round" stroke-dasharray="9 7"`)}
    ${t(`fill="${edge}" stroke="${edge}" stroke-width="19" stroke-linejoin="round" filter="url(#felt)"`)}
    ${t(`fill="${fill}" filter="url(#chenille)"`)}`;
}

// Stroke-based chenille shape (checkmark, candy cane)
function chenilleStroke({ d, w, fill, edge, thread, cap = 'round' }) {
  return `
    <path d="${d}" fill="none" stroke="${edge}" stroke-width="${w + 38}" stroke-linecap="${cap}" stroke-linejoin="round" filter="url(#felt)"/>
    <path d="${d}" fill="none" stroke="${thread}" stroke-width="${w + 25}" stroke-linecap="${cap}" stroke-linejoin="round" stroke-dasharray="9 7"/>
    <path d="${d}" fill="none" stroke="${edge}" stroke-width="${w + 19}" stroke-linecap="${cap}" stroke-linejoin="round" filter="url(#felt)"/>
    <path d="${d}" fill="none" stroke="${fill}" stroke-width="${w}" stroke-linecap="${cap}" stroke-linejoin="round" filter="url(#chenille)"/>`;
}

// A felt patch backing with an inset stitched border
function feltRect({ x, y, w, h, r, fill, thread, inset = 16 }) {
  return `
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" filter="url(#feltShadow)"/>
    <rect x="${x + inset}" y="${y + inset}" width="${w - inset * 2}" height="${h - inset * 2}" rx="${Math.max(r - inset, 4)}"
      fill="none" stroke="${thread}" stroke-width="5" stroke-dasharray="14 9" stroke-linecap="round"/>`;
}

function checkbox({ x, y, s, checked }) {
  return `
    ${feltRect({ x, y, w: s, h: s, r: 26, fill: C.cream, thread: C.goldDeep, inset: 14 })}
    <rect x="${x + 38}" y="${y + 38}" width="${s - 76}" height="${s - 76}" rx="12" fill="none" stroke="${C.black}" stroke-width="12" opacity=".85"/>
    ${checked ? chenilleStroke({ d: `M ${x + 30} ${y + s * 0.52} L ${x + s * 0.44} ${y + s * 0.86} L ${x + s * 1.18} ${y - s * 0.28}`, w: 46, fill: C.pink, edge: C.gold, thread: C.pinkDeep }) : ''}`;
}

function row({ y, rot, word, color, edge, wordWidth, checked }) {
  const x = 150, w = 1200, h = 300;
  return `
  <g transform="rotate(${rot} ${x + w / 2} ${y + h / 2})">
    ${feltRect({ x, y, w, h, r: 46, fill: C.black, thread: C.gold, inset: 20 })}
    ${checkbox({ x: x + 55, y: y + 55, s: 190, checked })}
    ${chenilleText({ x: x + 330 + (840 - wordWidth) / 2, y: y + 222, text: word, size: 205, width: wordWidth, fill: color, edge, thread: C.goldDeep })}
  </g>`;
}

// Small accent patches
const star = (cx, cy, r, rot) => {
  const pts = [...Array(10)].map((_, i) => {
    const a = (Math.PI / 5) * i - Math.PI / 2, rr = i % 2 ? r * 0.45 : r;
    return `${(cx + rr * Math.cos(a)).toFixed(1)},${(cy + rr * Math.sin(a)).toFixed(1)}`;
  }).join(' ');
  const inner = [...Array(10)].map((_, i) => {
    const a = (Math.PI / 5) * i - Math.PI / 2, rr = (i % 2 ? r * 0.45 : r) - 22;
    return `${(cx + rr * Math.cos(a)).toFixed(1)},${(cy + rr * Math.sin(a)).toFixed(1)}`;
  }).join(' ');
  return `<g transform="rotate(${rot} ${cx} ${cy})">
    <polygon points="${pts}" fill="${C.cream}" stroke="${C.cream}" stroke-width="34" stroke-linejoin="round" filter="url(#feltShadow)"/>
    <polygon points="${pts}" fill="none" stroke="${C.goldDeep}" stroke-width="5" stroke-dasharray="12 8" stroke-linejoin="round"/>
    <polygon points="${inner}" fill="${C.gold}" stroke="${C.gold}" stroke-width="10" stroke-linejoin="round" filter="url(#chenille)"/>
  </g>`;
};

const ornament = (cx, cy, r, rot) => `<g transform="rotate(${rot} ${cx} ${cy})">
    <circle cx="${cx}" cy="${cy}" r="${r + 22}" fill="${C.cream}" filter="url(#feltShadow)"/>
    <rect x="${cx - 34}" y="${cy - r - 58}" width="68" height="56" rx="10" fill="${C.cream}" stroke="${C.cream}" stroke-width="40" stroke-linejoin="round"/>
    <circle cx="${cx}" cy="${cy}" r="${r + 9}" fill="none" stroke="${C.goldDeep}" stroke-width="5" stroke-dasharray="12 8"/>
    <rect x="${cx - 30}" y="${cy - r - 50}" width="60" height="50" rx="8" fill="${C.gold}" filter="url(#chenille)"/>
    <circle cx="${cx}" cy="${cy}" r="${r - 6}" fill="${C.pink}" filter="url(#chenille)"/>
    <path d="M ${cx - r + 14} ${cy - 18} Q ${cx} ${cy + 22} ${cx + r - 14} ${cy - 18}" fill="none" stroke="${C.gold}" stroke-width="16" stroke-linecap="round"/>
    <path d="M ${cx - r + 20} ${cy + 34} Q ${cx} ${cy + 74} ${cx + r - 20} ${cy + 34}" fill="none" stroke="${C.white}" stroke-width="12" stroke-linecap="round" stroke-dasharray="2 22"/>
  </g>`;

const holly = (cx, cy, rot) => {
  const leaf = (dx, ang) => `<g transform="translate(${cx + dx} ${cy}) rotate(${ang})">
      <path d="M0 0 C 30 -40, 90 -40, 140 -10 C 125 -2, 128 12, 140 20 C 90 50, 30 40, 0 0 Z" fill="${C.cream}" stroke="${C.cream}" stroke-width="34" stroke-linejoin="round" filter="url(#feltShadow)"/>
      <path d="M0 0 C 30 -40, 90 -40, 140 -10 C 125 -2, 128 12, 140 20 C 90 50, 30 40, 0 0 Z" fill="none" stroke="${C.goldDeep}" stroke-width="4" stroke-dasharray="10 7" transform="translate(0 0)"/>
      <path d="M8 2 C 34 -30, 88 -30, 130 -8 C 118 0, 120 10, 130 16 C 88 40, 34 30, 8 2 Z" fill="${C.green}" filter="url(#chenille)"/>
    </g>`;
  return `<g transform="rotate(${rot} ${cx} ${cy})">
    ${leaf(0, -20)}${leaf(0, 200)}
    <circle cx="${cx - 6}" cy="${cy - 30}" r="34" fill="${C.cream}" filter="url(#feltShadow)"/>
    <circle cx="${cx + 30}" cy="${cy + 6}" r="34" fill="${C.cream}"/>
    <circle cx="${cx - 6}" cy="${cy - 30}" r="24" fill="${C.red}" filter="url(#chenille)"/>
    <circle cx="${cx + 30}" cy="${cy + 6}" r="24" fill="${C.red}" filter="url(#chenille)"/>
  </g>`;
};

const candyCane = (x, y, rot) => {
  const d = `M ${x} ${y + 230} L ${x} ${y + 60} Q ${x} ${y} ${x + 55} ${y} Q ${x + 110} ${y} ${x + 110} ${y + 60}`;
  return `<g transform="rotate(${rot} ${x + 55} ${y + 115})">
    ${chenilleStroke({ d, w: 52, fill: C.white, edge: C.red, thread: C.gold })}
    <path d="${d}" fill="none" stroke="${C.red}" stroke-width="52" stroke-dasharray="20 26" opacity=".95" filter="url(#chenille)"/>
  </g>`;
};

const sparkle = (cx, cy, s, color) =>
  `<path d="M ${cx} ${cy - s} Q ${cx + s * 0.18} ${cy - s * 0.18} ${cx + s} ${cy} Q ${cx + s * 0.18} ${cy + s * 0.18} ${cx} ${cy + s} Q ${cx - s * 0.18} ${cy + s * 0.18} ${cx - s} ${cy} Q ${cx - s * 0.18} ${cy - s * 0.18} ${cx} ${cy - s} Z"
    fill="${color}" stroke="${C.cream}" stroke-width="14" stroke-linejoin="round" paint-order="stroke" filter="url(#feltShadow)"/>`;

// Header banner: "Santa's List" in satin-stitch script on a red felt ribbon
const banner = () => {
  const x = 330, y = 120, w = 840, h = 230;
  const ribbon = `M ${x} ${y} Q ${x + w / 2} ${y - 46} ${x + w} ${y} L ${x + w} ${y + h} Q ${x + w / 2} ${y + h - 46} ${x} ${y + h} Z`;
  const tailL = `M ${x + 30} ${y + 60} L ${x - 120} ${y + 70} L ${x - 60} ${y + 150} L ${x - 120} ${y + 250} L ${x + 30} ${y + 250} Z`;
  const tailR = `M ${x + w - 30} ${y + 60} L ${x + w + 120} ${y + 70} L ${x + w + 60} ${y + 150} L ${x + w + 120} ${y + 250} L ${x + w - 30} ${y + 250} Z`;
  return `<g transform="rotate(-3 750 235)">
    <path d="${tailL}" fill="${C.pinkDeep}" filter="url(#feltShadow)"/>
    <path d="${tailR}" fill="${C.pinkDeep}" filter="url(#feltShadow)"/>
    <path d="${tailL}" fill="none" stroke="${C.gold}" stroke-width="4" stroke-dasharray="11 8" transform="translate(0 0)"/>
    <path d="${tailR}" fill="none" stroke="${C.gold}" stroke-width="4" stroke-dasharray="11 8"/>
    <path d="${ribbon}" fill="${C.red}" filter="url(#feltShadow)"/>
    <path d="M ${x + 22} ${y + 18} Q ${x + w / 2} ${y - 26} ${x + w - 22} ${y + 18} L ${x + w - 22} ${y + h - 18} Q ${x + w / 2} ${y + h - 62} ${x + 22} ${y + h - 18} Z"
      fill="none" stroke="${C.gold}" stroke-width="5" stroke-dasharray="14 9"/>
    <text x="${x + w / 2}" y="${y + 160}" text-anchor="middle" font-family="Script" font-size="168"
      fill="url(#satin)" stroke="${C.goldDeep}" stroke-width="3" paint-order="stroke" filter="url(#satinShade)">Santa's List</text>
  </g>`;
};

const svg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">
  <defs>
    <filter id="chenille" x="-60%" y="-60%" width="220%" height="220%">
      <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="4" result="n"/>
      <feDisplacementMap in="SourceGraphic" in2="n" scale="13" xChannelSelector="R" yChannelSelector="G" result="fuzzy"/>
      <feTurbulence type="turbulence" baseFrequency="0.17" numOctaves="2" seed="9" result="loops"/>
      <feGaussianBlur in="loops" stdDeviation="0.8" result="softLoops"/>
      <feDiffuseLighting in="softLoops" surfaceScale="3.5" diffuseConstant="1.45" lighting-color="#ffffff" result="light">
        <feDistantLight azimuth="235" elevation="62"/>
      </feDiffuseLighting>
      <feComposite in="light" in2="fuzzy" operator="in" result="lightIn"/>
      <feBlend in="fuzzy" in2="lightIn" mode="multiply" result="tex"/>
      <feGaussianBlur in="SourceAlpha" stdDeviation="10" result="puff"/>
      <feSpecularLighting in="puff" surfaceScale="9" specularConstant=".75" specularExponent="12" lighting-color="#ffffff" result="spec">
        <feDistantLight azimuth="235" elevation="48"/>
      </feSpecularLighting>
      <feComposite in="spec" in2="fuzzy" operator="in" result="specIn"/>
      <feComposite in="tex" in2="specIn" operator="arithmetic" k2="1" k3=".6"/>
    </filter>
    <filter id="felt" x="-60%" y="-60%" width="220%" height="220%">
      <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="2" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -.9 .62" result="speck"/>
      <feComposite in="speck" in2="SourceGraphic" operator="in" result="speckIn"/>
      <feBlend in="SourceGraphic" in2="speckIn" mode="multiply"/>
    </filter>
    <filter id="feltShadow" x="-60%" y="-60%" width="220%" height="220%">
      <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="2" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -.9 .62" result="speck"/>
      <feComposite in="speck" in2="SourceGraphic" operator="in" result="speckIn"/>
      <feBlend in="SourceGraphic" in2="speckIn" mode="multiply" result="feltTex"/>
      <feDropShadow in="feltTex" dx="0" dy="7" stdDeviation="5" flood-color="#000" flood-opacity=".45"/>
    </filter>
    <linearGradient id="satin" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff1c2"/><stop offset=".45" stop-color="${C.gold}"/><stop offset="1" stop-color="${C.goldDeep}"/>
    </linearGradient>
    <filter id="satinShade" x="-5%" y="-10%" width="110%" height="130%">
      <feTurbulence type="turbulence" baseFrequency="0.02 0.9" numOctaves="1" seed="5" result="threads"/>
      <feColorMatrix in="threads" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -.6 .5" result="lines"/>
      <feComposite in="lines" in2="SourceGraphic" operator="in" result="linesIn"/>
      <feBlend in="SourceGraphic" in2="linesIn" mode="multiply" result="sat"/>
      <feDropShadow in="sat" dx="0" dy="4" stdDeviation="2" flood-color="#5a0d18" flood-opacity=".6"/>
    </filter>
  </defs>

  ${banner()}
  ${row({ y: 440, rot: -2.2, word: 'NAUGHTY', color: C.red, edge: C.cream, wordWidth: 820, checked: false })}
  ${row({ y: 815, rot: 1.6, word: 'NICE', color: C.green, edge: C.cream, wordWidth: 520, checked: false })}
  ${row({ y: 1190, rot: -1.2, word: 'I TRIED', color: C.pink, edge: C.gold, wordWidth: 780, checked: true })}

  ${candyCane(95, 300, -18)}
  ${star(1365, 300, 92, 14)}
  ${ornament(1330, 840, 70, 10)}
  ${holly(205, 1560, -8)}
  ${sparkle(1290, 1555, 46, C.gold)}
  ${sparkle(1395, 1480, 30, C.pink)}
  ${sparkle(110, 1060, 30, C.gold)}
</svg>`;

const html = `<!doctype html><html><head><style>
  @font-face { font-family: Varsity; src: url(data:font/woff2;base64,${font('graduate', 'graduate-latin-400-normal.woff2')}) format('woff2'); }
  @font-face { font-family: Script; src: url(data:font/woff2;base64,${font('yellowtail', 'yellowtail-latin-400-normal.woff2')}) format('woff2'); }
  html, body { margin: 0; background: transparent; }
</style></head><body>${svg}</body></html>`;

writeFileSync(new URL('design.html', import.meta.url), html);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: SCALE });
await page.setContent(html);
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(300);
const png = new URL('naughty-nice-i-tried-4500x4950.png', OUT);
await page.locator('svg').screenshot({ path: png.pathname, omitBackground: true });

// Preview on a heather-gray tee color so the patches are easy to judge
await page.setContent(html.replace('background: transparent', 'background: #cfcfd4'));
await page.evaluate(() => document.fonts.ready);
const prev = new URL('preview-small.jpg', OUT);
const p2 = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 0.6 });
await p2.setContent(html.replace('background: transparent', 'background: #cfcfd4'));
await p2.evaluate(() => document.fonts.ready);
await p2.waitForTimeout(300);
await p2.screenshot({ path: prev.pathname, type: 'jpeg', quality: 88 });
await browser.close();
console.log('wrote', png.pathname);
