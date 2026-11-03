// Netlify build: copy only the public storefront into dist/ (not server code,
// docs, or node_modules). Every root-level .html file plus these folders is published.
import { cp, mkdir, readdir, rm } from 'node:fs/promises';

const PUBLIC_DIRS = ['assets', 'css', 'js'];

await rm('dist', { recursive: true, force: true });
await mkdir('dist');
for (const f of await readdir('.')) if (f.endsWith('.html')) await cp(f, `dist/${f}`);
for (const d of PUBLIC_DIRS) await cp(d, `dist/${d}`, { recursive: true });
console.log('Storefront copied to dist/');
