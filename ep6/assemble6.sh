#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p parts seq; rm -rf seq/*; mkdir -p seq/E1a seq/E1b
for f in frames/E1/E1_*.png; do n=$((10#$(basename $f .png | cut -d_ -f2))); if [ $n -le 23 ]; then ln -sf ../../$f seq/E1a/; else ln -sf ../../$f seq/E1b/; fi; done
for S in E2 E3 E4 E5 E6 E7; do ln -sfn ../frames/$S seq/$S; done
: > parts/list.txt
for S in E1b E2 E3 E4 E5 E6 E7 E1a; do
  case $S in
    E4) EXTRA=(-i sub_tina.png); FC="[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay[c];[c][2]overlay=enable='between(t,0.35,1.9)',format=yuv420p";;
    E5) EXTRA=(-i card_3h.png); FC="[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay[c];[c][2]overlay=enable='lt(t,1.6)',format=yuv420p";;
    *)  EXTRA=(); FC="[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay,format=yuv420p";;
  esac
  ffmpeg -v error -y -framerate 15 -pattern_type glob -i "seq/$S/*.png" -i caption.png "${EXTRA[@]}" -filter_complex "$FC" \
    -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30 parts/tmp_$S.mp4
  mv parts/tmp_$S.mp4 parts/$S.mp4; echo "file '$S.mp4'" >> parts/list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i parts/list.txt -c copy parts/video.mp4
python3 audio6.py
ffmpeg -v error -y -i parts/video.mp4 -i ep6_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest TubeTown_Ep6_Five_Minutes_Away.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 TubeTown_Ep6_Five_Minutes_Away.mp4
