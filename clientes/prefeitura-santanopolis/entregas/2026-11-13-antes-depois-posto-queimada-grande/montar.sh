#!/bin/bash
# Monta o Reels final. Uso: bash montar.sh <corte-mudo-42s.mp4>   (antes = 0–17 s, depois = 17–42 s)
# Entradas: corte 1080x1920, lettering/* (node render-lettering.js), trilha.mp3, vinheta-sem-arroba.png.
set -e; cd "$(dirname "$0")"; CORTE="$1"
T=(0.4 17.3 28.3 37.5)   # entrada de l1..l4 (duração: data-dur no HTML)
F="[0:v]split[a0][d0];[a0]trim=0:17,setpts=PTS-STARTPTS,fade=t=out:st=16.8:d=0.2:c=white[a1];[d0]trim=17:42,setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.5:c=white[d1];[a1][d1]concat=n=2:v=1:a=0,format=yuv420p[v0];"
IN=""
for i in 1 2 3 4; do a=${T[$((i-1))]}
  IN="$IN -framerate 30 -i lettering/l$i/%04d.png"
  F="$F[$i:v]format=rgba,setpts=PTS+$a/TB[l$i];[v$((i-1))][l$i]overlay=x=0:y=780:eof_action=pass[v$i];"
done
# selos de canto e logo (entradas 5,6,7)
F="$F[5:v]format=rgba,fade=t=in:st=3.6:d=0.25:alpha=1,fade=t=out:st=16.6:d=0.2:alpha=1[s1];[v4][s1]overlay=enable='between(t,3.6,16.8)'[v5];"
F="$F[6:v]format=rgba,fade=t=in:st=22.7:d=0.25:alpha=1[s2];[v5][s2]overlay=enable='gte(t,22.7)'[v6];"
F="$F[7:v]format=rgba[lg];[v6][lg]overlay[v7];"
F="$F[8:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.3[vin];[v7][vin]concat=n=2:v=1:a=0[v];[9:a]afade=t=out:st=43.5:d=1.5,atrim=0:45[a]"
ffmpeg -v error -y -i "$CORTE" $IN -loop 1 -framerate 30 -t 42 -i lettering/s1/0000.png -loop 1 -framerate 30 -t 42 -i lettering/s2/0000.png \
  -loop 1 -framerate 30 -t 42 -i lettering/lg/0000.png -loop 1 -t 3 -i vinheta-sem-arroba.png -i trilha.mp3 -filter_complex "$F" -map "[v]" -map "[a]" \
  -r 30 -c:v libx264 -preset medium -crf 21 -maxrate 8M -bufsize 16M -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t 45 video.mp4
