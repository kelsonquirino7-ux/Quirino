// Gera PNG de impressão (5420x3460), PDF e prévia para celular.
const {chromium}=require('playwright');const path=require('path');const N='ano-novo-2027-dourado';
(async()=>{const b=await chromium.launch();const f='file://'+path.resolve(__dirname,N+'.html');
  for(const [s,out] of [[2,N+'.png'],[0.5,'previa.png']]){
    const p=await b.newPage({viewport:{width:2710,height:1730},deviceScaleFactor:s});
    await p.goto(f);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
    await p.screenshot({path:path.join(__dirname,out)});
    if(s===2)await p.pdf({path:path.join(__dirname,N+'.pdf'),width:'2710px',height:'1730px',printBackground:true,pageRanges:'1'});
    await p.close();}
  await b.close();})();
