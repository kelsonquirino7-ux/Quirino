#!/bin/bash
# Monta o Reels do Vitor reaproveitando os vídeos já entregues à Prefeitura (sem o bruto):
# recorta a faixa limpa y=330..1410 (sem logo, selos, lettering e legenda da Prefeitura) para a janela quadrada,
# junta com o grafismo (render-grafismo.js), trilha da Prefeitura (já paga) e a fala do prefeito sincronizada com as cenas.
# Uso: node render-grafismo.js && bash montar.sh
set -e; cd "$(dirname "$0")"
P=../../../prefeitura-santanopolis/entregas
SF=$P/2026-11-13-antes-depois-posto-queimada-grande/antes-x-agora-posto-de-saude-queimada-grande.mp4
CF=$P/2026-11-13-posto-queimada-grande-com-fala/posto-de-saude-queimada-grande-com-fala.mp4
TR=$P/2026-11-13-antes-depois-posto-queimada-grande/trilha.mp3
VIN=vinheta-sem-arroba.png
N=posto-queimada-grande-antes-e-hoje.mp4
T=42.24   # duração antes da vinheta
# fonte(0=SF 1=CF)  início  duração  velocidade   — trechos sem grafismo da Prefeitura na faixa recortada
SEG=(
"0 3.6 3.0 1"    # 0  antes: paredes
"0 7.0 2.0 1"    # 1  antes: porta e folhas
"0 10.6 2.0 1"   # 2  antes: corredor com mato
"0 13.6 2.4 1"   # 3  antes: mato e entulho
"0 32.3 4.0 1"   # 4  hoje: salas brancas (entra com cortina)
"1 6.0 2.3 1"    # 5  fala 0–2,3 "Mais investimentos… agora" (lábio sincronizado)
"0 22.7 2.8 1"   # 6  fala "é a vez… comunidade da Queimada Grande" — varanda
"0 36.3 1.2 1"   # 7  fala "posto de saúde satélite" — sala
"1 12.4 6.5 1"   # 8  fala 6,4–12,9 agradecimentos Dominique/Vadão/Júnior (sincronizado)
"0 25.5 2.8 0.75" # 9 fala "que doou vários materiais para a reforma e ampliação" — varanda em câmera lenta
"1 28.5 6.74 1"  # 10 fala 22,5–29,2 "E a Queimada Grande… deputado… equipamentos" (como no original, sincronizado)
"1 35.2 6.2 1"   # 11 fala 29,2–35,4 "Roberta Santana… governador Jerônimo… cada vez mais" (sincronizado)
)
# melhora de imagem: redução leve de ruído/compressão + nitidez, escala lanczos
Q="hqdn3d=1.2:1.2:3:3,unsharp=5:5:0.55:3:3:0"
F=""; i=0
for s in "${SEG[@]}"; do read src ss d v <<<"$s"
  F="$F[$src:v]trim=start=$ss:duration=$d,setpts=(PTS-STARTPTS)/$v,crop=1080:1080:0:330,$Q,scale=960:960:flags=lanczos,setsar=1,fps=30,format=yuv420p,settb=1/30[s$i];"; i=$((i+1)); done
F="$F[s0][s1][s2][s3]concat=n=4:v=1:a=0,settb=1/30[an];[an][s4]xfade=transition=wiperight:duration=0.6:offset=8.8[ah];"
F="$F[ah][s5][s6][s7][s8][s9][s10][s11]concat=n=8:v=1:a=0,trim=0:$T[jan];"
F="$F color=c=0x015927:s=1080x1920:r=30:d=$T[bg];[bg][jan]overlay=60:390[b1];[2:v]format=rgba[g];[b1][g]overlay=eof_action=pass,format=yuv420p[mv];"
F="$F[3:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.3[vin];[mv][vin]concat=n=2:v=1:a=0[v];"
# áudio: trilha some na fala (12,8–42,2 s) e volta na vinheta; fala = áudio da versão com fala (já traz a trilha baixa)
F="$F[4:a]volume='if(lt(t,12.4),1,if(lt(t,12.8),1-(t-12.4)/0.4,if(lt(t,41.9),0,min(1,(t-41.9)/0.5))))':eval=frame,afade=t=out:st=43.6:d=1.6,atrim=0:45.24[m];"
fa(){ echo "[1:a]atrim=$1:$2,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.04,afade=t=out:st=$(echo "$2-$1-0.06"|bc):d=0.06,adelay=$(echo "$3*1000/1"|bc):all=1[$4];"; }
F="$F$(fa 6.0 12.3 12.8 f1)$(fa 12.4 22.64 19.1 f2)$(fa 28.5 41.4 29.34 f3)"
F="$F[m][f1][f2][f3]amix=inputs=4:normalize=0:duration=first,alimiter=limit=0.95[a]"
ffmpeg -v error -y -i "$SF" -i "$CF" -framerate 30 -i grafismo/%04d.png -loop 1 -t 3 -i "$VIN" -i "$TR" \
  -filter_complex "$F" -map "[v]" -map "[a]" -r 30 -c:v libx264 -preset slow -crf 16 -profile:v high -maxrate 14M -bufsize 28M -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart -t 45.24 "$N"
echo "ok: $N"
