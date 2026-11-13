#!/bin/bash
# Monta o Reels com a fala. Uso: bash montar.sh <pasta-do-bruto>   (clipes IMG_xxxx.mov da pasta do Drive)
# Estrutura: antes 0–6 s · fala 6–41,4 s (com cenas do posto por cima) · encerramento 41,4–43,9 s · vinheta 2,2 s.
set -e; cd "$(dirname "$0")"; B="$1"; S=$(mktemp -d); N="posto-de-saude-queimada-grande-com-fala.mp4"
A="eq=saturation=0.55:contrast=1.05:brightness=-0.02"; D="eq=saturation=1.15"; i=0
# clipe  inicio  quadros  tratamento(a=antes d=depois f=fala)  [filtro extra]
while read n ss fr g x; do i=$((i+1)); case $g in a) G=$A;; d) G=$D;; f) G="eq=saturation=1.05";; esac
  ffmpeg -v error -y -ss $ss -i "$B/$n.mov" -an -frames:v $fr -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,$G${x:+,$x},format=yuv420p" \
    -c:v libx264 -preset veryfast -crf 18 "$S/$(printf %02d $i).mp4" </dev/null; echo "file '$S/$(printf %02d $i).mp4'" >> $S/l.txt
done <<'LISTA'
IMG_0011 1 72 a
IMG_9991 2.5 54 a
IMG_0010 6 54 a fade=t=out:st=1.6:d=0.2:c=white
IMG_5325 0 69 f fade=t=in:st=0:d=0.4:c=white
IMG_5310 0.5 123 d
IMG_5325 6.4 195 f
IMG_5311 1 72 d
IMG_5314 1 72 d
IMG_5325 17.7 144 f
IMG_5322 5 54 d
IMG_5325 24.3 72 f
IMG_5315 0.5 75 d
IMG_5325 29.2 186 f
IMG_5310 3.5 75 d
LISTA
ffmpeg -v error -y -f concat -safe 0 -i $S/l.txt -c copy $S/base.mp4
ov(){ echo "[$1:v]format=rgba,setpts=PTS+$2/TB[o$1];[$4][o$1]overlay=x=0:y=$3:eof_action=pass[$5];"; }
F="[0:v]format=yuv420p[v0];$(ov 1 0.3 700 v0 v1)$(ov 2 8.4 700 v1 v2)$(ov 3 19.0 700 v2 v3)$(ov 4 41.5 700 v3 v4)$(ov 5 6.0 1430 v4 v5)"
F="$F[6:v]format=rgba,fade=t=in:st=3.3:d=0.25:alpha=1,fade=t=out:st=5.7:d=0.2:alpha=1[s1];[v5][s1]overlay=enable='between(t,3.3,5.9)'[v6];[7:v]format=rgba[lg];[v6][lg]overlay[v7];"
F="$F[8:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.3[vin];[v7][vin]concat=n=2:v=1:a=0[v];"
F="$F[9:a]atempo=0.975,volume='0.8*if(lt(t,5.7),1,if(lt(t,6.2),1-0.86*(t-5.7)/0.5,if(lt(t,41.2),0.14,if(lt(t,41.8),0.14+0.86*(t-41.2)/0.6,1))))':eval=frame,afade=t=out:st=44.6:d=1.5[m];"
F="$F[10:a]atrim=0:35.4,highpass=f=80,loudnorm=I=-15:TP=-1.5:LRA=9,adelay=6000:all=1[f];[m][f]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]"
ffmpeg -v error -y -i $S/base.mp4 -framerate 30 -i lettering/l1/%04d.png -framerate 30 -i lettering/l2/%04d.png -framerate 30 -i lettering/l3/%04d.png \
  -framerate 30 -i lettering/l4/%04d.png -framerate 30 -i lettering/cap/%04d.png -loop 1 -framerate 30 -t 43.9 -i lettering/s1/0000.png \
  -loop 1 -framerate 30 -t 43.9 -i lettering/lg/0000.png -loop 1 -t 2.2 -i vinheta-sem-arroba.png -i trilha.mp3 -i "$B/IMG_5325.mov" \
  -filter_complex "$F" -map "[v]" -map "[a]" -r 30 -c:v libx264 -preset medium -crf 21 -maxrate 8M -bufsize 16M -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart -t 46.1 "$N"; rm -rf $S
