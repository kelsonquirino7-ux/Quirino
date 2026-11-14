// Gera os quadros transparentes (30 fps) de grafismo.html em grafismo/0000.png...
// Uso: node render-grafismo.js            (todos os quadros, 28,7 s)
//      node render-grafismo.js 2 10 15    (só amostras nesses segundos, em amostra-<t>.png)
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const TOTAL=28.7, am=process.argv.slice(2).map(Number);
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve(__dirname,'grafismo.html'));await p.evaluate(()=>document.fonts.ready);
const dir=path.join(__dirname,'grafismo');if(!am.length){fs.rmSync(dir,{recursive:true,force:true});fs.mkdirSync(dir)}
const ts=am.length?am:[...Array(Math.round(TOTAL*30)).keys()].map(f=>f/30);
for(let f=0;f<ts.length;f++){await p.evaluate(t=>setT(t),ts[f]);
  await p.screenshot({path:am.length?path.join(__dirname,`amostra-${ts[f]}.png`):path.join(dir,String(f).padStart(4,'0')+'.png'),omitBackground:true})}
await b.close()})();
