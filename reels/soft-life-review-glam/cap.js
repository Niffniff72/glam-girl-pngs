const { chromium } = require('playwright');
const { spawn } = require('child_process');
const [,, html, mode, out] = process.argv;
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await pg.goto('file://' + html); await pg.evaluate(() => document.fonts.ready);
  await pg.waitForTimeout(300);
  if (mode === 'preview') {
    for (const t of [1.0, 3.4, 5.6, 10.0]) { await pg.evaluate(t => render(t), t); await pg.screenshot({ path: `${out}/prev_${t}.png` }); }
  } else {
    const FPS = 30, DUR = 11, ff = spawn('ffmpeg', ['-y','-v','error','-f','image2pipe','-framerate',String(FPS),'-i','-',
      '-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart', out], { stdio: ['pipe','inherit','inherit'] });
    for (let f = 0; f < FPS * DUR; f++) { await pg.evaluate(t => render(t), f / FPS); ff.stdin.write(await pg.screenshot({ type: 'png' })); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await b.close();
})();
