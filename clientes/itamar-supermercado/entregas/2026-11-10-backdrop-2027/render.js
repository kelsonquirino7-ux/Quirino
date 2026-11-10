// Gera, para cada backdrop-*.html desta pasta, a prévia PNG e o PDF de impressão
// em tamanho real (2710 x 1730 mm, vetorial).  Uso: node render.js
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
(async()=>{
  const b=await chromium.launch();
  for(const f of fs.readdirSync(__dirname).filter(f=>/^backdrop-.*\.html$/.test(f))){
    const base=path.join(__dirname,f.replace(/\.html$/,''));
    const p=await b.newPage({viewport:{width:2710,height:1730}});
    await p.goto('file://'+path.join(__dirname,f));await p.evaluate(()=>document.fonts.ready);
    await p.screenshot({path:base+'-previa.png'});
    await p.pdf({path:base+'-impressao-271x173cm.pdf',preferCSSPageSize:true,printBackground:true});
    await p.close();
  }
  await b.close();
})();
