// Monta o story de aniversário: abertura do Magnific (abertura-magnific.mp4) + extrai os quadros do bruto.mp4, renderiza aniversario.html quadro a quadro e junta com o áudio.
// Uso: node render-video.js   ·   prévia de um quadro: node render-video.js --quadro 2.1 saida.jpg
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path'), os = require('os');
const AQUI = __dirname, FPS = 30, AB = 5.04, FIM = AB + 9.8, TOTAL = Math.round(FIM * FPS), PARALELO = 4, Q = path.join(AQUI, 'quadros');
const ff = a => execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...a]);
if (!fs.existsSync(Q)) { fs.mkdirSync(Q);
  ff(['-i', path.join(AQUI, 'bruto.mp4'), '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30', '-q:v', '2', path.join(Q, '%04d.jpg')]); }
const QA = path.join(AQUI, 'quadros-abertura');
if (!fs.existsSync(QA)) { fs.mkdirSync(QA); ff(['-i', path.join(AQUI, 'abertura-magnific.mp4'), '-q:v', '2', path.join(QA, '%04d.jpg')]); }
(async () => {
  const b = await chromium.launch();
  const nova = async () => { const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
    await p.goto('file://' + path.join(AQUI, 'aniversario.html')); await p.evaluate(() => window.pronto); return p; };
  if (process.argv[2] === '--quadro') { const p = await nova(); await p.evaluate(t => window.setT(t), +process.argv[3]);
    await p.screenshot({ path: process.argv[4], type: 'jpeg', quality: 90 }); await b.close(); return; }
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'aniv-'));
  await Promise.all([...Array(PARALELO)].map(async (_, w) => { const p = await nova();
    for (let n = w; n < TOTAL; n += PARALELO) { await p.evaluate(t => window.setT(t), n / FPS);
      await p.screenshot({ path: path.join(tmp, String(n).padStart(4, '0') + '.jpg'), type: 'jpeg', quality: 95 }); } }));
  await b.close();
  ff(['-framerate', String(FPS), '-i', path.join(tmp, '%04d.jpg'), '-i', path.join(AQUI, 'bruto.mp4'),
    '-filter_complex', `[1:a]aresample=48000,afade=t=out:st=4.8:d=0.34,adelay=${AB*1000}|${AB*1000},apad,atrim=duration=${FIM}[a]`,
    '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', path.join(AQUI, 'aniversario-edivan-story.mp4')]);
  fs.rmSync(tmp, { recursive: true }); console.log('Pronto:', TOTAL, 'quadros');
})();
