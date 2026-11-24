// Exporta a faixa: PNG 8000x2000 (impressão), PDF vetorial 4000x1000 px (proporção 4:1) e preview.jpg para o celular.
const {chromium}=require('playwright');const path=require('path');
(async()=>{
  const nome=process.argv[2]||'faixa-4x1';const f=path.join(__dirname,nome+'.html');const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:4000,height:1000},deviceScaleFactor:2});
  await p.goto('file://'+f);await p.evaluate(()=>document.fonts.ready);
  await p.screenshot({path:path.join(__dirname,nome+'.png')});
  await p.pdf({path:path.join(__dirname,nome+'.pdf'),width:'4000px',height:'1000px',printBackground:true,pageRanges:'1'});
  const q=await b.newPage({viewport:{width:4000,height:1000},deviceScaleFactor:0.5});
  await q.goto('file://'+f);await q.evaluate(()=>document.fonts.ready);
  await q.screenshot({path:path.join(__dirname,(nome==='faixa-4x1'?'preview':nome+'-preview')+'.jpg'),type:'jpeg',quality:85});
  await b.close();console.log('ok');
})();
