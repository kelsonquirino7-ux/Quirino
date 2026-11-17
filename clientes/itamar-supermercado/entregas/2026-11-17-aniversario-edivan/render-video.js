// Monta o story: bruto.mp4 (tela cheia 1080x1920) + camada animada de aniversario.html + cartão final.
// Uso: node render-video.js   ·   prévia de um quadro: node render-video.js --quadro 7.5 saida.png [--guia]
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path'), os = require('os');
const AQUI = __dirname, FPS = 30, VID = 5.14, FIM = 10.14, TOTAL = Math.round(FIM * FPS), PARALELO = 4;
const URL = g => 'file://' + path.join(AQUI, 'aniversario.html') + (g ? '?guia' : '');

(async () => {
  const b = await chromium.launch();
  const nova = async g => { const p = await b.newPage({ viewport: { width: 1080, height: 1920 } }); await p.goto(URL(g)); await p.evaluate(() => window.pronto); return p; };
  if (process.argv[2] === '--quadro') {
    const p = await nova(process.argv.includes('--guia')); await p.evaluate(t => window.setT(t), +process.argv[3]);
    await p.screenshot({ path: process.argv[4], omitBackground: true }); await b.close(); return;
  }
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'aniv-'));
  await Promise.all([...Array(PARALELO)].map(async (_, w) => {
    const p = await nova();
    for (let n = w; n < TOTAL; n += PARALELO) {
      await p.evaluate(t => window.setT(t), n / FPS);
      await p.screenshot({ path: path.join(tmp, String(n).padStart(4, '0') + '.png'), omitBackground: true });
    }
  }));
  await b.close();
  const F = `[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=${FPS},setsar=1,` +
    `tpad=stop_mode=clone:stop_duration=${FIM - VID},trim=duration=${FIM}[v];` +
    `[v][1:v]overlay=0:0:format=auto,format=yuv420p[out];` +
    `[0:a]aresample=48000,afade=t=out:st=${VID - 0.4}:d=0.4,apad,atrim=duration=${FIM}[a]`;
  execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-i', path.join(AQUI, 'bruto.mp4'),
    '-framerate', String(FPS), '-i', path.join(tmp, '%04d.png'), '-filter_complex', F, '-map', '[out]', '-map', '[a]',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart',
    path.join(AQUI, 'aniversario-edivan-story.mp4')]);
  fs.rmSync(tmp, { recursive: true });
  console.log('Pronto:', TOTAL, 'quadros');
})();
