#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p parts; : > parts/list.txt
for S in T1 T2 TC TB T3 T4 T5 T6; do
  case $S in
    T4) EXTRA=(); FC="[0]scale=1080:1920:flags=lanczos,fps=30,format=yuv420p"; CAP=();;
    T5) CAP=(-i caption.png); EXTRA=(-i sub1.png); FC="[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay[c];[c][2]overlay=enable='between(t,0.35,3.1)',format=yuv420p";;
    T6) CAP=(-i caption.png); EXTRA=(-i sub2.png); FC="[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay[c];[c][2]overlay=enable='gte(t,0.55)',format=yuv420p";;
    *)  CAP=(-i caption.png); EXTRA=(); FC="[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay,format=yuv420p";;
  esac
  ffmpeg -v error -y -framerate 15 -pattern_type glob -i "frames/$S/*.png" "${CAP[@]}" "${EXTRA[@]}" -filter_complex "$FC" \
    -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30 parts/tmp_$S.mp4
  mv parts/tmp_$S.mp4 parts/$S.mp4; echo "file '$S.mp4'" >> parts/list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i parts/list.txt -c copy parts/video.mp4
python3 audio9.py
ffmpeg -v error -y -i parts/video.mp4 -i ep9_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest TubeTown_Forgot_My_Phone_v2.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 TubeTown_Forgot_My_Phone_v2.mp4
