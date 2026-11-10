// Gera PNG de impressão (5420x3460), PDF vetorial e prévia para celular.
const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const f='file://'+path.resolve(__dirname,'banner-ano-novo-2027.html');
  for(const [s,out] of [[2,'banner-ano-novo-2027.png'],[0.5,'previa.png']]){
    const p=await b.newPage({viewport:{width:2710,height:1730},deviceScaleFactor:s});
    await p.goto(f);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
    await p.screenshot({path:path.join(__dirname,out)});
    if(s===2)await p.pdf({path:path.join(__dirname,'banner-ano-novo-2027.pdf'),width:'2710px',height:'1730px',printBackground:true,pageRanges:'1'});
    await p.close();}
  await b.close();})();
