// Renderiza index.html fotograma a fotograma con Playwright + Chromium.
// Uso:
//   node render.js frames            -> out/frames/00000.png ... y out/cues.json
//   node render.js stills 1.2 5 9.5  -> out/stills/t_1.20.png ...
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const FPS = 30;
const WORKERS = Number(process.env.WORKERS || 4);
const ROOT = __dirname;
const OUT = path.join(ROOT, 'out');
const hasProof = fs.existsSync(path.join(ROOT, 'assets', 'tienda.png'));
const url = 'file://' + path.join(ROOT, 'index.html') + `?play=0&proof=${hasProof ? 1 : 0}`;

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => { window.__frozen = true; });
  return page;
}

async function shot(page, t, file) {
  await page.evaluate(t => window.render(t), t);
  await page.screenshot({ path: file, clip: { x: 0, y: 0, width: 1080, height: 1920 } });
}

(async () => {
  const [mode, ...args] = process.argv.slice(2);
  const browser = await chromium.launch({
    executablePath: fs.existsSync('/opt/pw-browsers/chromium') ? undefined : undefined,
  });
  if (mode === 'stills') {
    const dir = path.join(OUT, 'stills');
    fs.mkdirSync(dir, { recursive: true });
    const page = await openPage(browser);
    for (const a of args) await shot(page, Number(a), path.join(dir, `t_${Number(a).toFixed(2)}.png`));
  } else {
    const dir = path.join(OUT, 'frames');
    fs.rmSync(dir, { recursive: true, force: true });
    fs.mkdirSync(dir, { recursive: true });
    const probe = await openPage(browser);
    const info = await probe.evaluate(() => ({ cues: window.CUES, duration: window.DURATION, times: window.TIMES, proof: window.HAS_PROOF }));
    fs.writeFileSync(path.join(OUT, 'cues.json'), JSON.stringify(info, null, 1));
    await probe.close();
    const total = Math.round(info.duration * FPS);
    let next = 0, done = 0;
    const started = Date.now();
    await Promise.all(Array.from({ length: WORKERS }, async () => {
      const page = await openPage(browser);
      while (next < total) {
        const f = next++;
        await shot(page, f / FPS, path.join(dir, String(f).padStart(5, '0') + '.png'));
        if (++done % 150 === 0) console.log(`${done}/${total} fotogramas (${((Date.now() - started) / 1000).toFixed(0)} s)`);
      }
    }));
    console.log(`listo: ${total} fotogramas, prueba social: ${info.proof ? 'sí' : 'no'}`);
  }
  await browser.close();
})();
