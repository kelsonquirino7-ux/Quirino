// Renderiza tv-acougue.html quadro a quadro e monta o MP4 (1920x1080, tela em pé girada, 29,97 fps).
// Uso: node render-video.js [pasta-temporaria]   ·   teste de um quadro: node render-video.js --quadro 12.3 saida.png
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path'), os = require('os');
const AQUI = __dirname, URL = 'file://' + path.join(AQUI, 'tv-acougue.html');
const FPS = 30000 / 1001, DUR = 4.6 + 37 * 4, TOTAL = Math.round(DUR * FPS), PARALELO = 4;

(async () => {
  const b = await chromium.launch();
  const nova = async () => { const p = await b.newPage({ viewport: { width: 1080, height: 1920 } }); await p.goto(URL); await p.evaluate(() => window.pronto); return p; };
  if (process.argv[2] === '--quadro') {
    const p = await nova(); await p.evaluate(t => window.setT(t), +process.argv[3]);
    await p.screenshot({ path: process.argv[4] }); await b.close(); return;
  }
  const tmp = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), 'tv-acougue-'));
  fs.mkdirSync(tmp, { recursive: true });
  await Promise.all([...Array(PARALELO)].map(async (_, w) => {
    const p = await nova();
    for (let n = w; n < TOTAL; n += PARALELO) {
      await p.evaluate(t => window.setT(t), n / FPS);
      await p.screenshot({ path: path.join(tmp, String(n).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 96 });
    }
  }));
  await b.close();
  const saida = path.join(AQUI, 'tv-acougue.mp4');
  execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-framerate', '30000/1001', '-i', path.join(tmp, '%05d.jpg'),
    '-vf', 'transpose=2', '-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', saida]);
  console.log('Pronto:', saida, TOTAL, 'quadros');
})();
