#!/usr/bin/env bash
# Finaliza um vídeo de cliente: ajusta formato, legenda opcional, logo no canto e vinheta final.
#
# Uso:
#   bash ferramentas/video.sh -c <cliente> -i entrada.mp4 -o saida.mp4 [-f 9x16|16x9] [-l legenda.srt [-a]] [-d destaques.txt] [-z 2.5,8] [-m] [-q]
#     -c  pasta do cliente em clientes/ (ex.: itamar-supermercado)
#     -f  formato final (padrão 9x16 = Reels/Stories; 16x9 = YouTube/TV)
#     -l  arquivo .srt para queimar a legenda no vídeo
#     -m  coloca o logo do cliente pequeno no canto superior
#     -q  coloca o crédito "PRODUÇÃO quirino" nos 4 primeiros segundos
#     -v  duração da vinheta final em segundos (padrão 3; 0 = sem vinheta)
#     -a  legenda animada estilo Reels (usa o .srt do -l; palavra da vez em caixa na cor do cliente)
#     -d  arquivo de textos de destaque, uma linha por texto:  0:03-0:06 OBRA ENTREGUE
#     -z  zoom de impacto nos segundos indicados, separados por vírgula (ex.: -z 2.5,8,14)
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
FMT=9x16; LEG=""; MARCA=0; CRED=0; VDUR=3; ANIM=0; DEST=""; ZOOM=""
while getopts "c:i:o:f:l:mqv:ad:z:" o; do case $o in
  a) ANIM=1;; d) DEST=$OPTARG;; z) ZOOM=$OPTARG;;
  c) CLI=$OPTARG;; i) IN=$OPTARG;; o) OUT=$OPTARG;; f) FMT=$OPTARG;; l) LEG=$OPTARG;;
  m) MARCA=1;; q) CRED=1;; v) VDUR=$OPTARG;; *) sed -n '2,15p' "$0"; exit 1;; esac; done
: "${CLI:?falta -c cliente}" "${IN:?falta -i entrada}" "${OUT:?falta -o saida}"
D="$RAIZ/clientes/$CLI"; [ -d "$D" ] || { echo "Cliente não encontrado: $D"; exit 1; }
if [ "$FMT" = 9x16 ]; then W=1080; H=1920; else W=1920; H=1080; fi
VIN="$D/modelos/vinheta-$FMT.png"
[ -f "$VIN" ] || node "$RAIZ/ferramentas/render.js" "$D/modelos/vinheta-$FMT.html" >/dev/null

LOGO=$(ls "$D"/identidade/*branco*.png 2>/dev/null | head -1 || true)
[ -n "$LOGO" ] || LOGO=$(ls "$D"/identidade/*transparente*.png "$D"/identidade/*.png 2>/dev/null | head -1)
CREDITO="$RAIZ/aplicacoes/video/credito-producao.png"

TEM_AUDIO=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$IN" | head -1)
# 1) enquadra: vídeo inteiro no centro, fundo = o próprio vídeo ampliado e desfocado
F="[0:v]split[a][b];[a]scale=$W:$H:force_original_aspect_ratio=increase,crop=$W:$H,gblur=sigma=40,eq=brightness=-0.08[bg];"
F+="[b]scale=$W:$H:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p[v0];"
ENTR=(-i "$IN"); N=1; ATUAL=v0
if [ -n "$ZOOM" ]; then
  # zoom rápido de 18% (entra em 0,15 s, segura 0,5 s, volta em 0,3 s) em cada instante pedido
  Z="1"; for T in ${ZOOM//,/ }; do Z+="+0.18*clip((it-$T)/0.15,0,1)*clip(($T+0.95-it)/0.3,0,1)"; done
  F+="[$ATUAL]zoompan=z='$Z':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=${W}x$H:fps=30,setsar=1[vz];"; ATUAL=vz
fi
if [ $ANIM = 1 ] || [ -n "$DEST" ]; then
  # legenda animada e/ou destaques: gera o .ass editável ao lado do vídeo final
  python3 -c "import fontTools" 2>/dev/null || pip install -q fonttools 2>/dev/null
  ASS="${OUT%.*}-efeitos.ass"; mkdir -p "$(dirname "$OUT")"
  python3 "$RAIZ/ferramentas/efeitos.py" -c "$CLI" -f "$FMT" -o "$ASS" \
    $([ $ANIM = 1 ] && [ -n "$LEG" ] && echo "-l $LEG") $([ -n "$DEST" ] && echo "-d $DEST") >/dev/null
  F+="[$ATUAL]ass='$(realpath "$ASS")':fontsdir='$RAIZ/ferramentas/fontes/ttf'[va];"; ATUAL=va
  [ $ANIM = 1 ] && LEG=""   # já está no .ass
fi
if [ -n "$LEG" ]; then
  ESTILO="FontName=Inter,Bold=1,FontSize=$([ $FMT = 9x16 ] && echo 13 || echo 18),PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,MarginV=$([ $FMT = 9x16 ] && echo 70 || echo 40)"
  F+="[$ATUAL]subtitles='$(realpath "$LEG")':force_style='$ESTILO'[v1];"; ATUAL=v1
fi
if [ $MARCA = 1 ] && [ -n "$LOGO" ]; then
  ENTR+=(-i "$LOGO"); LW=$((W/4))
  F+="[$N:v]scale=$LW:-1,format=rgba,colorchannelmixer=aa=0.9[lg];[$ATUAL][lg]overlay=W-w-48:60[v2];"; ATUAL=v2; N=$((N+1))
fi
if [ $CRED = 1 ]; then
  ENTR+=(-i "$CREDITO"); CW=$((W/4))
  F+="[$N:v]scale=$CW:-1[cr];[$ATUAL][cr]overlay=W-w-40:H-h-$([ $FMT = 9x16 ] && echo 240 || echo 60):enable='lt(t,4)'[v3];"; ATUAL=v3; N=$((N+1))
fi
if [ -n "$TEM_AUDIO" ]; then F+="[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];"
else DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
  ENTR+=(-f lavfi -t "$DUR" -i anullsrc=r=48000:cl=stereo); F+="[$N:a]anull[a0];"; N=$((N+1)); fi
if [ "$VDUR" != 0 ]; then
  ENTR+=(-loop 1 -t "$VDUR" -i "$VIN" -f lavfi -t "$VDUR" -i anullsrc=r=48000:cl=stereo)
  F+="[$N:v]scale=$W:$H,setsar=1,fps=30,format=yuv420p,fade=t=in:st=0:d=0.4[vf];"
  F+="[$ATUAL][a0][vf][$((N+1)):a]concat=n=2:v=1:a=1[vout][aout]"
else F+="[$ATUAL]null[vout];[a0]anull[aout]"; fi
mkdir -p "$(dirname "$OUT")"
ffmpeg -hide_banner -loglevel error -y "${ENTR[@]}" -filter_complex "$F" -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 160k -movflags +faststart "$OUT"
echo "Pronto: $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" | cut -d. -f1)s, ${W}x${H})"
