#!/usr/bin/env bash
# Passo final: queima o lettering, funde com a vinheta e mixa o áudio.
# Uso: bash mixagem.sh base.mp4 trilha-calma.mp3 trilha-animada.mp3 voz.wav saida.mp4
# Trilha calma até a água (21,33 s); trilha animada entra no 1º tempo do compasso, casada na batida,
# com 1 compasso de percussão aguda antes. Na fala (31,3–36 s) a música cai para 16% do volume.
set -euo pipefail
E="$(cd "$(dirname "$0")" && pwd)"; R="$E/../../../.."; D=42.3333
ffmpeg -v error -y -i "$1" -loop 1 -t 3 -i "$E/vinheta.png" -ss 10.67 -i "$2" -ss 77.343 -i "$3" -ss 80.01 -i "$3" -i "$4" -filter_complex "
[0:v]ass='$E/video-efeitos.ass':fontsdir='$R/ferramentas/fontes/ttf',settb=AVTB[a];
[1:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p,settb=AVTB[b];
[a][b]xfade=transition=fade:duration=0.5:offset=39.3333[v];
[2:a]atrim=0:21.6,volume='0.55*(1-clip((t-21.25)/0.1,0,1))':eval=frame,afade=t=in:d=0.4[calma];
[3:a]atrim=0:2.72,highpass=f=2500,volume='0.75*pow(clip(t/2.667,0,1),1.5)*(1-clip((t-2.667)/0.04,0,1))':eval=frame,adelay=18667:all=1[prep];
[4:a]atrim=0:21.2,afade=t=in:d=0.015,adelay=21333:all=1,volume='1.0*(1-0.84*clip((t-30.9)/0.45,0,1)*clip((36.3-t)/0.5,0,1))':eval=frame,afade=t=out:st=41.3:d=1.0[forte];
[calma][prep][forte]amix=inputs=3:normalize=0[m];
[5:a]highpass=f=90,afade=t=in:d=0.05,afade=t=out:st=4.45:d=0.14,adelay=31333:all=1,volume=2.2[vz];
[m][vz]amix=inputs=2:normalize=0,volume=0.8,alimiter=limit=0.8:attack=5:release=80,aresample=48000[au]" \
 -map "[v]" -map "[au]" -c:v libx264 -preset medium -crf 22 -maxrate 9M -bufsize 18M -pix_fmt yuv420p -c:a aac -b:a 192k -t $D -movflags +faststart "$5"
