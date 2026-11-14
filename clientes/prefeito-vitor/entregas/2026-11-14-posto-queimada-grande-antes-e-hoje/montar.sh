#!/bin/bash
# Monta o Reels do Vitor reaproveitando os vídeos já entregues à Prefeitura (sem o bruto):
# recorta a faixa limpa y=330..1410 (sem logo, selos, lettering e legenda da Prefeitura) para a janela quadrada,
# junta com o grafismo (render-grafismo.js), trilha da Prefeitura (já paga) e trechos da fala do prefeito.
# Uso: node render-grafismo.js && bash montar.sh
set -e; cd "$(dirname "$0")"
P=../../../prefeitura-santanopolis/entregas
SF=$P/2026-11-13-antes-depois-posto-queimada-grande/antes-x-agora-posto-de-saude-queimada-grande.mp4
CF=$P/2026-11-13-posto-queimada-grande-com-fala/posto-de-saude-queimada-grande-com-fala.mp4
TR=$P/2026-11-13-antes-depois-posto-queimada-grande/trilha.mp3
VIN=vinheta-sem-arroba.png
N=posto-queimada-grande-antes-e-hoje.mp4
# fonte(0=SF 1=CF)  início  duração   — todos em trechos sem grafismo da Prefeitura na faixa recortada
SEG=(
"0 3.6 3.0"   # antes: fachada/paredes
"0 7.0 2.0"   # antes: porta e folhas
"0 10.6 2.0"  # antes: corredor com mato
"0 13.6 2.4"  # antes: mato e entulho
"0 32.3 4.0"  # hoje: salas brancas (entra com transição)
"1 6.0 2.3"   # prefeito falando (sincronizado com a fala 0–2,3 s)
"0 22.7 4.0"  # hoje: varanda (fala 2,3–6,3 s)
"1 28.5 1.8"  # hoje: área externa (fala "sempre contemplada")
"0 26.7 1.6"  # hoje: varanda
"1 32.7 2.5"  # hoje: sala
"0 36.3 1.2"  # hoje: sala (congela no fim)
)
F=""; L=""; i=0
for s in "${SEG[@]}"; do read src ss d <<<"$s"
  F="$F[$src:v]trim=start=$ss:duration=$d,setpts=PTS-STARTPTS,crop=1080:1080:0:330,scale=960:960,setsar=1,fps=30,format=yuv420p[s$i];"; i=$((i+1)); done
# antes (s0..s3) com virada em cortina para o hoje (s4); depois cortes secos; congela o último quadro 2,5 s
F="$F[s0][s1][s2][s3]concat=n=4:v=1:a=0,settb=1/30[an];[s4]settb=1/30[s4t];[an][s4t]xfade=transition=wiperight:duration=0.6:offset=8.8[ah];"
F="$F[ah][s5][s6][s7][s8][s9][s10]concat=n=7:v=1:a=0,tpad=stop_mode=clone:stop_duration=2.5,trim=0:28.7[jan];"
# fundo + janela + grafismo, depois vinheta (3 s) do Vitor
F="$F color=c=0x015927:s=1080x1920:r=30:d=28.7[bg];[bg][jan]overlay=60:390[b1];[2:v]format=rgba[g];[b1][g]overlay=eof_action=pass,format=yuv420p[mv];"
F="$F[3:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.3[vin];[mv][vin]concat=n=2:v=1:a=0[v];"
# áudio: trilha sai durante a fala (12,6–21,0 s) e volta; fala = áudio da versão com fala (já tem a trilha baixa por baixo)
F="$F[4:a]volume='if(lt(t,12.4),1,if(lt(t,12.8),1-(t-12.4)/0.4,if(lt(t,20.9),0,if(lt(t,21.5),(t-20.9)/0.6,1))))':eval=frame,afade=t=out:st=29.7:d=2,atrim=0:31.7[m];"
F="$F[1:a]atrim=6.0:12.35,asetpts=PTS-STARTPTS,afade=t=out:st=6.15:d=0.2,adelay=12800:all=1[f1];"
F="$F[1:a]atrim=28.5:30.4,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.05,afade=t=out:st=1.7:d=0.2,adelay=19140:all=1[f2];"
F="$F[m][f1][f2]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[a]"
ffmpeg -v error -y -i "$SF" -i "$CF" -framerate 30 -i grafismo/%04d.png -loop 1 -t 3 -i "$VIN" -i "$TR" \
  -filter_complex "$F" -map "[v]" -map "[a]" -r 30 -c:v libx264 -preset medium -crf 20 -maxrate 8M -bufsize 16M -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart -t 31.7 "$N"
echo "ok: $N"
