#!/bin/bash
# Monta o Reels do plantio com a fala. Uso: bash montar.sh <pasta-do-bruto>   (clipes IMG_xxxx.mov do Drive)
# Estrutura: abertura 0–3 s · fala 3–47,1 s (cenas do plantio por cima) · encerramento 47,1–49,3 s · vinheta 2,2 s.
set -e; cd "$(dirname "$0")"; B="$1"; S=$(mktemp -d); N="plantio-de-arvores-boa-espera-com-fala.mp4"; i=0
# clipe  inicio  quadros  [filtro extra]      (IMG_5306 = fala)
while read n ss fr x; do i=$((i+1))
  ffmpeg -v error -y -ss $ss -i "$B/$n.mov" -an -frames:v $fr -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30${x:+,$x},format=yuv420p" \
    -c:v libx264 -preset veryfast -crf 18 "$S/$(printf %02d $i).mp4" </dev/null; echo "file '$S/$(printf %02d $i).mp4'" >> $S/l.txt
done <<'LISTA'
IMG_5263 1 90
IMG_5306 2.7 171
IMG_5262 3 66
IMG_5250 1 75
IMG_5306 13.1 141
IMG_5269 0.5 69
IMG_5306 20.1 189
IMG_5241 1 90
IMG_5306 29.4 108
IMG_5261 2 72
IMG_5306 35.4 258
IMG_5270 10.5 84
IMG_5262 8 66
LISTA
ffmpeg -v error -y -f concat -safe 0 -i $S/l.txt -c copy $S/base.mp4
ov(){ echo "[$1:v]format=rgba,setpts=PTS+$2/TB[o$1];[$4][o$1]overlay=x=0:y=$3:eof_action=pass[$5];"; }
F="[0:v]format=yuv420p[v0];$(ov 1 0.2 780 v0 v1)$(ov 2 8.8 660 v1 v2)$(ov 3 26.8 660 v2 v3)$(ov 4 47.2 780 v3 v4)$(ov 5 3.0 1430 v4 v5)"
F="$F[6:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.3[vin];[v5][vin]concat=n=2:v=1:a=0[v];"
F="$F[7:a][8:a]acrossfade=d=2,volume='0.8*if(lt(t,2.7),1,if(lt(t,3.2),1-0.87*(t-2.7)/0.5,if(lt(t,46.9),0.13,if(lt(t,47.5),0.13+0.87*(t-46.9)/0.6,1))))':eval=frame,afade=t=out:st=50:d=1.5[m];"
F="$F[9:a]atrim=2.7:46.8,asetpts=PTS-STARTPTS,highpass=f=80,loudnorm=I=-15:TP=-1.5:LRA=9,adelay=3000:all=1[f];[m][f]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]"
ffmpeg -v error -y -i $S/base.mp4 -framerate 30 -i lettering/l1/%04d.png -framerate 30 -i lettering/l2/%04d.png -framerate 30 -i lettering/l6/%04d.png \
  -framerate 30 -i lettering/l5/%04d.png -framerate 30 -i lettering/cap/%04d.png -loop 1 -t 2.2 -i vinheta-sem-arroba.png -i trilha.mp3 -i trilha.mp3 -i "$B/IMG_5306.mov" \
  -filter_complex "$F" -map "[v]" -map "[a]" -r 30 -c:v libx264 -preset medium -crf 21 -maxrate 8M -bufsize 16M -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart -t 51.5 "$N"; rm -rf $S
