// Gera PNG transparente da bandeira do Brasil tremulando (3D/WebGL, sem custo de créditos).
// Uso: node ferramentas/bandeira.js saida.png '{"w":1600,"h":1400,"rotY":-0.35,"poste":1,"seed":3}'
// Opções: amp, freq, rotX/rotY/rotZ, scale, tx/ty, seed, poste (0 = sem mastro), raioPoste, extPoste,
//   espelho (1 = tremula para a esquerda, mastro à direita, texto continua legível),
//   queda (1 = normal; maior = ponta mais caída), cor ("#002F67" = tecido liso), textura ("arquivo.png" = tecido com essa imagem), semBainha.
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
(async()=>{
  const [out,json='{}']=process.argv.slice(2);const P=JSON.parse(json);
  if(P.textura)P.textura='file://'+path.resolve(P.textura);
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--allow-file-access-from-files']});
  const p=await b.newPage();
  await p.goto('file://'+path.resolve(__dirname,'bandeira.html')+'#'+encodeURIComponent(JSON.stringify(P)));
  await p.waitForFunction(()=>window.PRONTO,null,{timeout:120000});
  const data=await p.evaluate((P)=>{
    const gl=document.getElementById('gl'),c=document.createElement('canvas');c.width=gl.width;c.height=gl.height;const g=c.getContext('2d');
    if(P.espelho){g.translate(c.width,0);g.scale(-1,1);}
    if(P.poste!==0&&!P.cor&&!P.textura){const [a,,z]=window.TRALHA;const ang=Math.atan2(z[1]-a[1],z[0]-a[0]),L=Math.hypot(z[0]-a[0],z[1]-a[1])+(P.extPoste??400),r=(P.raioPoste||14);
      g.save();g.translate(a[0],a[1]);g.rotate(ang);const gr=g.createLinearGradient(0,-r,0,r);
      gr.addColorStop(0,'#5d6166');gr.addColorStop(.3,'#e9ecef');gr.addColorStop(.5,'#b7bcc2');gr.addColorStop(1,'#3d4045');
      g.fillStyle=gr;g.fillRect(-r*2.2,-r,L,2*r);g.fillStyle='#d9dde1';g.beginPath();g.arc(-r*2.2,0,r*1.25,0,7);g.fill();g.restore();}
    g.drawImage(gl,0,0);return c.toDataURL('image/png');},P);
  fs.writeFileSync(out,Buffer.from(data.split(',')[1],'base64'));console.log(out);await b.close();
})();
