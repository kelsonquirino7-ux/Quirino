// Renderiza grafismos.html quadro a quadro (PNG transparente, 30 fps) para sobrepor ao vídeo original.
// Uso: node render.js <pasta-dos-quadros>          · teste: node render.js --quadro 12.3 saida.png
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const URL = 'file://' + path.join(__dirname, 'grafismos.html'), FPS = 30, PARALELO = 4;

(async () => {
  const b = await chromium.launch();
  const nova = async () => { const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
    await p.goto(URL); await p.evaluate(() => window.pronto); return p; };
  if (process.argv[2] === '--quadro') {
    const p = await nova();
    for (let i = 3; i < process.argv.length; i += 2) {
      await p.evaluate(t => window.setT(t), +process.argv[i]);
      await p.screenshot({ path: process.argv[i + 1], omitBackground: true });
    }
    await b.close(); return;
  }
  const tmp = process.argv[2]; fs.mkdirSync(tmp, { recursive: true });
  const p0 = await nova(); const TOTAL = Math.round(await p0.evaluate(() => window.DUR) * FPS); await p0.close();
  await Promise.all([...Array(PARALELO)].map(async (_, w) => {
    const p = await nova();
    for (let n = w; n < TOTAL; n += PARALELO) {
      await p.evaluate(t => window.setT(t), n / FPS);
      await p.screenshot({ path: path.join(tmp, String(n).padStart(5, '0') + '.png'), omitBackground: true });
    }
  }));
  await b.close(); console.log(TOTAL, 'quadros em', tmp);
})();
