// Gera lettering/l1..l5.png (transparentes, 1080x1920) a partir de lettering.html
const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve(__dirname,'lettering.html'));await p.evaluate(()=>document.fonts.ready);
for(let i=1;i<=5;i++)await p.locator('#l'+i).screenshot({path:path.join(__dirname,'lettering','l'+i+'.png'),omitBackground:true});
await b.close()})();
