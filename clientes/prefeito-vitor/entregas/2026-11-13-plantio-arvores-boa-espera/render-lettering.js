// Gera os quadros transparentes (30 fps) de cada lettering em lettering/lN/0000.png
// a partir de lettering.html. Recorte: faixa y=780..1780 (sobrepor no video em y=780).
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const so=process.argv[2]; // opcional: "amostra" gera 1 quadro por lettering (t=1.6 s)
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve(__dirname,'lettering.html'));await p.evaluate(()=>document.fonts.ready);
const ls=await p.evaluate(()=>[...document.querySelectorAll('.q')].map(q=>[q.id,+q.dataset.dur]));
for(const [id,dur] of ls){const dir=path.join(__dirname,'lettering',id);fs.rmSync(dir,{recursive:true,force:true});fs.mkdirSync(dir,{recursive:true});
  await p.evaluate(id=>{document.querySelectorAll('.q').forEach(q=>q.style.display=q.id===id?'block':'none');window.scrollTo(0,0);
    window.__an=document.getAnimations();window.__an.forEach(a=>a.pause())},id);
  const n=so?1:Math.round(dur*30);
  for(let f=0;f<n;f++){const t=so?1600:f/30*1000;await p.evaluate(t=>window.__an.forEach(a=>a.currentTime=t),t);
    await p.screenshot({path:path.join(dir,String(f).padStart(4,'0')+'.png'),omitBackground:true,clip:so?{x:0,y:0,width:1080,height:1920}:{x:0,y:780,width:1080,height:1000}})}
  console.log(id,n)}
await b.close()})();
