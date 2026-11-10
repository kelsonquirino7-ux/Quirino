// Renderiza uma animação HTML em vídeo MP4 (sem custo, sem filmagem).
// Uso: node ferramentas/animacao.js <arquivo.html> [saida.mp4]
// O HTML precisa de <meta name="tamanho" content="1080x1920">, <meta name="duracao" content="38.5">
// e expor window.seek(t) que desenha o quadro do segundo t.
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');const {spawn}=require('child_process');
(async()=>{
  const f=process.argv[2];const out=process.argv[3]||f.replace(/\.html$/,'.mp4');const FPS=30;
  const html=fs.readFileSync(f,'utf8');
  const [,w,h]=html.match(/name="tamanho" content="(\d+)x(\d+)"/);const dur=+html.match(/name="duracao" content="([\d.]+)"/)[1];
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:+w,height:+h}});
  await p.goto('file://'+path.resolve(f));await p.evaluate(()=>document.fonts.ready);
  const ff=spawn('ffmpeg',['-hide_banner','-loglevel','error','-y','-f','image2pipe','-framerate',FPS,'-c:v','mjpeg','-i','-',
    '-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  const n=Math.round(dur*FPS);
  for(let i=0;i<n;i++){
    await p.evaluate(t=>window.seek(t),i/FPS);
    const buf=await p.screenshot({type:'jpeg',quality:96});
    if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
  }
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log(out,n+' quadros');
})();
