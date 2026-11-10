// Renderiza cena-3d.html → letreiro-3d.png (2160x2700, fundo transparente).
// Uso (na raiz do repositório): THREE_DIR=/caminho/node_modules/three node clientes/itamar-supermercado/entregas/2026-11-10-black-friday-eletro/render-3d.js
// (three.js não fica no repositório: `npm i three@0.170.0 clipper-lib@6.4.2` em qualquer pasta, copie
//  node_modules/clipper-lib/clipper.js para dentro de node_modules/three/ e aponte THREE_DIR para node_modules/three.)
const {chromium}=require('playwright'),http=require('http'),fs=require('fs'),path=require('path');
const raiz=process.cwd(),three=process.env.THREE_DIR,aqui=path.relative(raiz,__dirname);
const tipos={'.html':'text/html','.js':'text/javascript','.ttf':'font/ttf'};
const srv=http.createServer((q,s)=>{const u=decodeURIComponent(q.url.split('?')[0]);
  const f=u.startsWith('/three/')?path.join(three,u.slice(7)):path.join(raiz,u);
  fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end();}s.writeHead(200,{'content-type':tipos[path.extname(f)]||'application/octet-stream'});s.end(d);});});
srv.listen(0,async()=>{
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:2});
  p.on('console',m=>m.type()==='error'&&console.log('ERRO:',m.text()));p.on('pageerror',e=>console.log('ERRO:',e.message));
  await p.goto(`http://localhost:${srv.address().port}/${aqui}/cena-3d.html`);
  await p.waitForFunction('window.pronto',null,{timeout:120000});
  const out=path.join(__dirname,'letreiro-3d.png');await p.screenshot({path:out,omitBackground:true});console.log(out);
  await b.close();srv.close();
});
