// Renderiza encerramento.html quadro a quadro → encerramento.mp4 (1080x1920, 30 fps, 11 s, sem áudio).
// Uso: node render-video.js   ·   teste de um quadro: node render-video.js --quadro 6 saida.png
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path'), os = require('os');
const AQUI = __dirname, URL = 'file://' + path.join(AQUI, 'encerramento.html');
const FPS = 30, DUR = 11, TOTAL = DUR * FPS, PARALELO = 4;
(async () => {
  const b = await chromium.launch();
  const nova = async () => { const p = await b.newPage({ viewport: { width: 1080, height: 1920 } }); await p.goto(URL); await p.evaluate(() => window.pronto); return p; };
  if (process.argv[2] === '--quadro') {
    const p = await nova(); await p.evaluate(t => window.setT(t), +process.argv[3]);
    await p.screenshot({ path: process.argv[4] }); await b.close(); return;
  }
  const tmp = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), 'encerramento-'));
  await Promise.all([...Array(PARALELO)].map(async (_, w) => {
    const p = await nova();
    for (let n = w; n < TOTAL; n += PARALELO) {
      await p.evaluate(t => window.setT(t), n / FPS);
      await p.screenshot({ path: path.join(tmp, String(n).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 96 });
    }
  }));
  await b.close();
  execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-framerate', String(FPS), '-i', path.join(tmp, '%05d.jpg'),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path.join(AQUI, 'encerramento.mp4')]);
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log('Pronto: encerramento.mp4', TOTAL, 'quadros');
})();
