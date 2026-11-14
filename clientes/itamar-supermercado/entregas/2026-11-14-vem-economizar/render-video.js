// Renderiza vem-economizar.html quadro a quadro e monta os MP4.
// Uso: node render-video.js h|v        ·  teste: node render-video.js h --quadro 3.2 saida.png
//  h = TV 65" horizontal, 3840x2160 (4K) · v = TV 32" em pé, 1920x1080 com a imagem girada (igual ao vídeo do açougue)
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path'), os = require('os');
const AQUI = __dirname, FMT = process.argv[2] === 'v' ? 'v' : 'h';
const URL = 'file://' + path.join(AQUI, 'vem-economizar.html') + '?fmt=' + FMT;
const FPS = 30, PARALELO = 4;
const VP = FMT === 'v' ? { width: 1080, height: 1920 } : { width: 1920, height: 1080 }, ESC = FMT === 'v' ? 1 : 2;
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const nova = async () => { const p = await b.newPage({ viewport: VP, deviceScaleFactor: ESC }); await p.goto(URL); await p.evaluate(() => window.pronto); return p; };
  if (process.argv[3] === '--quadro') {
    const p = await nova(); await p.evaluate(t => window.setT(t), +process.argv[4]);
    await p.screenshot({ path: process.argv[5] }); await b.close(); return;
  }
  const p0 = await nova(); const DUR = await p0.evaluate(() => window.DUR); await p0.close();
  const TOTAL = Math.round(DUR * FPS);
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'vem-economizar-' + FMT + '-'));
  await Promise.all([...Array(PARALELO)].map(async (_, w) => {
    const p = await nova();
    for (let n = w; n < TOTAL; n += PARALELO) {
      await p.evaluate(t => window.setT(t), n / FPS);
      await p.screenshot({ path: path.join(tmp, String(n).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 95 });
    }
  }));
  await b.close();
  const saida = path.join(AQUI, FMT === 'v' ? 'vem-economizar-tv32-vertical.mp4' : 'vem-economizar-tv65-4k.mp4');
  const vf = FMT === 'v' ? ['-vf', 'transpose=2'] : [];
  execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-framerate', String(FPS), '-i', path.join(tmp, '%05d.jpg'), ...vf,
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', saida]);
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log('Pronto:', saida, TOTAL, 'quadros');
})();
