// Gera a prévia PNG e o PDF de impressão em tamanho real (2710 x 1730 mm, vetorial).
// Uso: node render.js   (dentro desta pasta)
const {chromium}=require('playwright');const path=require('path');
(async()=>{
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:2710,height:1730}});
  await p.goto('file://'+path.join(__dirname,'backdrop-2027.html'));await p.evaluate(()=>document.fonts.ready);
  await p.screenshot({path:path.join(__dirname,'backdrop-2027-previa.png')});
  await p.pdf({path:path.join(__dirname,'backdrop-2027-impressao-271x173cm.pdf'),preferCSSPageSize:true,printBackground:true});
  await b.close();
})();
