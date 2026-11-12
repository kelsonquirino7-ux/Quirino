// Desenha os cartões animados quadro a quadro (PNG transparente, 30 fps).
// Uso: node cartoes.js <tempos.json> <pasta-de-saida>      (montar.py chama sozinho)
//   tempos.json: {"pipa": {"dur": 2.2, "marcas": []}, ...}  → saida/<nome>/0000.png ...
// Também gera cartoes/marca.png (marca-d'água do canto) e cartoes/previa-<nome>.png (quadro de conferência).
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
(async()=>{
  const tempos=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const saida=process.argv[3];
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+path.resolve(__dirname,'cartoes.html'));await p.evaluate(()=>document.fonts.ready);
  fs.mkdirSync(path.join(__dirname,'cartoes'),{recursive:true});
  for(const [nome,{dur,marcas}] of Object.entries(tempos)){
    const el=await p.$('#'+nome);const dir=path.join(saida,nome);fs.mkdirSync(dir,{recursive:true});
    const n=Math.round(dur*30);
    for(let f=0;f<n;f++){
      await p.evaluate(([nome,t,dur,marcas])=>draw(nome,t,dur,marcas),[nome,f/30,dur,marcas]);
      await el.screenshot({path:path.join(dir,String(f).padStart(4,'0')+'.png'),omitBackground:true});
    }
    const meio=String(Math.round(n*0.72)).padStart(4,'0')+'.png';
    fs.copyFileSync(path.join(dir,meio),path.join(__dirname,'cartoes','previa-'+nome+'.png'));
    console.log(nome,n,'quadros');
  }
  await b.close()})();
