// Gera os PNGs transparentes dos cartões: node cartoes.js  (na pasta da entrega)
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
  fs.mkdirSync(path.join(__dirname,'cartoes'),{recursive:true});
  await p.goto('file://'+path.resolve(__dirname,'cartoes.html'));await p.evaluate(()=>document.fonts.ready);
  for(const el of await p.$$('[data-cartao]')){
    const nome=await el.getAttribute('data-cartao');const n=+(await el.getAttribute('data-estados')||0);
    if(!n){await el.screenshot({path:path.join(__dirname,'cartoes',nome+'.png'),omitBackground:true});continue}
    for(let k=1;k<=n;k++){await el.evaluate((e,k)=>e.querySelectorAll('.it').forEach((x,i)=>x.classList.toggle('on',i<k)),k);
      await el.screenshot({path:path.join(__dirname,'cartoes',nome+'-'+k+'.png'),omitBackground:true})}}
  await b.close()})();
