// Versão em pé (TV 32" vertical) de tv-carnes.html: palco 1080x1920 (?v).
// Gera tv-carnes-vertical.mp4 (1080x1920) e tv-carnes-vertical-girado.mp4 (1920x1080, girado 90° anti-horário, para TV montada em pé que só toca vídeo deitado).
// Uso: node render-vertical.js   ·   teste: node render-vertical.js --quadro 12.3 saida.png
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path'), os = require('os');
const NOME = 'tv-carnes', AQUI = __dirname, URL = 'file://' + path.join(AQUI, NOME + '.html') + '?v', FPS = 30, PARALELO = 4;
(async () => {
  const b = await chromium.launch();
  const nova = async () => { const p = await b.newPage({ viewport: { width: 1080, height: 1920 } }); await p.goto(URL); await p.evaluate(() => window.pronto); return p; };
  if (process.argv[2] === '--quadro') {
    const p = await nova();
    for (let k = 3; k < process.argv.length; k += 2) { await p.evaluate(t => window.setT(t), +process.argv[k]); await p.screenshot({ path: process.argv[k + 1] }); }
    await b.close(); return;
  }
  const p0 = await nova(); const DUR = await p0.evaluate(() => window.DUR); await p0.close();
  const TOTAL = Math.round(DUR * FPS), tmp = fs.mkdtempSync(path.join(os.tmpdir(), NOME + '-v-'));
  await Promise.all([...Array(PARALELO)].map(async (_, w) => {
    const p = await nova();
    for (let n = w; n < TOTAL; n += PARALELO) {
      await p.evaluate(t => window.setT(t), n / FPS);
      await p.screenshot({ path: path.join(tmp, String(n).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 95 });
    }
  }));
  await b.close();
  const enc = (vf, saida) => execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-framerate', String(FPS), '-i', path.join(tmp, '%05d.jpg'),
    ...(vf ? ['-vf', vf] : []), '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path.join(AQUI, saida)]);
  enc(null, NOME + '-vertical.mp4');
  enc('transpose=2', NOME + '-vertical-girado.mp4');
  fs.rmSync(tmp, { recursive: true });
  console.log('Pronto:', NOME, TOTAL, 'quadros');
})();
