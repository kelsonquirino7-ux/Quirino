#!/usr/bin/env bash
# Monta o vídeo final: filmagem original + zoom suave nos cortes + grafismos (render.js) + trilha e efeitos.
# Uso: bash montar.sh bruto.mp4 pasta-dos-quadros
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"; IN=$1; Q=$2; TMP=${TMPDIR_MONTAR:-$(mktemp -d)}; mkdir -p "$TMP"
DUR=64.067   # 60,467 s de filmagem (sem os 6 quadros pretos do fim) + 3,6 s de encerramento com o logo

# Cortes da filmagem que ganham um "assentamento" de câmera (zoom 4% → 100%); os demais cortes têm transição gráfica.
CORTES="2.1 4.5 5.733 7.267 9.033 15.5 17.9 19.233 20.767 22.133 27.467 29.167 31.1 33.167 34.867 38.033 40.4 43.7 44.967 47.267 50.733 52.3 53.667 55 57 58.6"
Z="1"; for T in $CORTES; do Z+="+0.045*gte(t\,$T)*pow(clip(1-(t-$T)/0.6\,0\,1)\,2)"; done

# Efeitos sonoros sintetizados (sem custo)
sfx() { ffmpeg -v error -y -f lavfi -i "$1" -t "$2" -ar 44100 -ac 2 "$TMP/$3.wav"; }
sfx "aevalsrc='0.8*sin(2*PI*(500+2600*t)*t)*exp(-28*t)'" 0.18 pop
sfx "aevalsrc='0.8*sin(2*PI*(220+1600*t*t)*t)*exp(-9*t)'" 0.45 boing
sfx "anoisesrc=color=pink:amplitude=0.9,bandpass=f=1800:w=2500,afade=t=in:d=0.3:curve=qsin,afade=t=out:st=0.3:d=0.35" 0.65 whoosh
sfx "aevalsrc='0.35*(sin(2*PI*1318*t)+sin(2*PI*1760*t)+0.6*sin(2*PI*2637*t))*exp(-3.5*t)'" 1.4 brilho

# Trilha (30,8 s) em loop com fusão de 1,5 s
M="$AQUI/trilha-magnific.mp3"
AF="[1:a][2:a]acrossfade=d=1.5[m12];[m12][3:a]acrossfade=d=1.5,atrim=0:$DUR,afade=t=in:d=0.3,afade=t=out:st=$(echo "$DUR-2" | bc):d=2,volume=0.85[mus];"
# Efeitos: [arquivo instante volume]
EF=(pop 0.35 .5  pop 0.6 .3  pop 0.85 .3  boing 1.0 .6  whoosh 1.25 .45  pop 1.55 .45  pop 1.85 .35  brilho 2.05 .5
    whoosh 10.92 .7  whoosh 23.35 .7  whoosh 36.05 .7  whoosh 48.75 .7  brilho 44.97 .5  whoosh 60.12 .8  pop 60.8 .6  brilho 60.9 .8)
ENT=(); MIX="[mus]"; k=4; n=1
for ((i=0;i<${#EF[@]};i+=3)); do
  ENT+=(-i "$TMP/${EF[i]}.wav"); ms=$(echo "${EF[i+1]}*1000/1" | bc)
  AF+="[$k:a]adelay=$ms|$ms,volume=${EF[i+2]}[e$n];"; MIX+="[e$n]"; k=$((k+1)); n=$((n+1))
done
AF+="${MIX}amix=inputs=$n:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[aout]"

# Vídeo: trecho 11,27–15,47 s tem barras pretas no original → preenchidas com o próprio quadro desfocado
VF="[0:v]fps=30,setsar=1,split[o][b];"
VF+="[b]crop=864:1920:108:0,split[b1][b2];[b1]scale=1080:2400,crop=1080:1920,gblur=sigma=45[bb];[bb][b2]overlay=108:0[pb];"
VF+="[o][pb]overlay=0:0:enable='between(t,11.25,15.49)'[v1];"
VF+="[v1]scale=w='2*trunc(540*($Z))':h='2*trunc(960*($Z))':eval=frame:flags=bicubic,crop=1080:1920:x='540*(iw/1080-1)':y='240*(ih/1920-1)',setsar=1,trim=end_frame=1814,format=yuv420p[fv];color=c=0xFF291E:s=1080x1920:r=30:d=3.6,format=yuv420p,setsar=1[cor];[fv][cor]concat=n=2:v=1:a=0[vout]"

# 1) áudio
ffmpeg -v error -y -i "$IN" -i "$M" -i "$M" -i "$M" "${ENT[@]}" -filter_complex "$AF" -map "[aout]" -t $DUR -ar 48000 "$TMP/audio.wav"
# 2) filmagem tratada (intermediário quase sem perdas)
ffmpeg -v error -stats -y -i "$IN" -filter_complex "$VF" -map "[vout]" -an -c:v libx264 -preset veryfast -crf 10 "$TMP/filmagem.mp4"
# 3) grafismos por cima + encerramento + áudio (tudo quadro a quadro, 30 fps)
ffmpeg -v error -stats -y -i "$TMP/filmagem.mp4" -framerate 30 -i "$Q/%05d.png" -i "$TMP/audio.wav" \
  -filter_complex "[0:v][1:v]overlay=0:0,format=yuv420p[vout]" \
  -map "[vout]" -map 2:a -t $DUR \
  -c:v libx264 -preset slow -crf 20 -maxrate 9M -bufsize 18M -profile:v high -level 4.2 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart "$AQUI/empresa-x-confraternizacao.mp4"
ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$TMP/filmagem.mp4"; rm -rf "$TMP"; echo "Pronto: $AQUI/empresa-x-confraternizacao.mp4"
