// Renderiza modelos HTML em PNG.
// Uso: node ferramentas/render.js <arquivo.html> [saida.png]
// O tamanho vem de <meta name="tamanho" content="1080x1350"> no HTML.
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{
  const files=process.argv.slice(2).filter(f=>f.endsWith('.html'));
  const b=await chromium.launch();
  for(const f of files){
    const html=fs.readFileSync(f,'utf8');const m=html.match(/name="tamanho" content="(\d+)x(\d+)"/);
    const [w,h]=m?[+m[1],+m[2]]:[1080,1350];
    const p=await b.newPage({viewport:{width:w,height:h}});
    await p.goto('file://'+path.resolve(f));await p.evaluate(()=>document.fonts.ready);
    const out=f.replace(/\.html$/,'.png');await p.screenshot({path:out});console.log(out);await p.close();
  }
  await b.close();
})();
