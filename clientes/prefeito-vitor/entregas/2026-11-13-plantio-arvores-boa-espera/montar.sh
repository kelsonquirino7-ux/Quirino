#!/bin/bash
# Monta o Reels final. Uso: bash montar.sh <corte-mudo-42s.mp4>
# Entradas: corte 1080x1920 (42 s), lettering/l1..l5.png, trilha.mp3, vinheta do cliente.
set -e; cd "$(dirname "$0")"; CORTE="$1"; V=../../modelos/vinheta-9x16.png
# lettering: inicio fim
T=(0.5:4.0 25.8:31.2 31.8:35.2 35.8:39.2 39.7:42.0)
F="[0:v]format=yuv420p[v0];"; IN=""
for i in 1 2 3 4 5; do a=${T[$((i-1))]%%:*}; b=${T[$((i-1))]##*:}
  IN="$IN -loop 1 -t 42 -i lettering/l$i.png"
  F="$F[$i:v]format=rgba,fade=t=in:st=$a:d=0.15:alpha=1,fade=t=out:st=$(echo "$b-0.2"|bc):d=0.2:alpha=1[l$i];"
  F="$F[v$((i-1))][l$i]overlay=x=0:y='90*exp(-7*(t-$a))*cos(16*(t-$a))':enable='between(t,$a,$b)'[v$i];"
done
F="$F[6:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.3[vin];[v5][vin]concat=n=2:v=1:a=0[v];[7:a]afade=t=out:st=43.5:d=1.5,atrim=0:45[a]"
ffmpeg -v error -y -i "$CORTE" $IN -loop 1 -t 3 -i $V -i trilha.mp3 -filter_complex "$F" -map "[v]" -map "[a]" \
  -r 30 -c:v libx264 -preset medium -crf 21 -maxrate 8M -bufsize 16M -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t 45 video.mp4
