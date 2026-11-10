#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p parts2 seq2
rm -rf seq2/*; mkdir -p seq2/S1a seq2/S1b
for f in frames/S1/S1_*.png; do n=$((10#$(basename $f .png | cut -d_ -f2))); if [ $n -le 23 ]; then ln -sf ../../$f seq2/S1a/; else ln -sf ../../$f seq2/S1b/; fi; done
for S in S2 S3 S4 S5 S6 S7 S8; do ln -sfn ../frames/$S seq2/$S; done
declare -A FPS=( [S1a]=15 [S1b]=15 [S2]=15 [S3]=15 [S4]=30 [S5]=15 [S6]=15 [S7]=15 [S8]=30 )
declare -A SUB=( [S6]=sub_tina.png [S7]=sub_doug.png )
: > parts2/list.txt
for S in S1b S2 S3 S4 S5 S6 S7 S8 S1a; do
  if [ -n "${SUB[$S]}" ]; then
    FC="[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay=0:0[c];[c][2]overlay=0:0:enable='gte(t,0.5)',format=yuv420p"
    IN=(-i caption.png -i ${SUB[$S]})
  else
    FC="[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay=0:0,format=yuv420p"; IN=(-i caption.png)
  fi
  ffmpeg -v error -y -framerate ${FPS[$S]} -pattern_type glob -i "seq2/$S/*.png" "${IN[@]}" -filter_complex "$FC" \
    -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30 parts2/tmp_$S.mp4
  mv parts2/tmp_$S.mp4 parts2/$S.mp4
  echo "file '$S.mp4'" >> parts2/list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i parts2/list.txt -c copy parts2/video.mp4
python3 audio2.py
ffmpeg -v error -y -i parts2/video.mp4 -i ep1_audio_v2.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest TubeTown_Ep1_The_Microwave_v2.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 TubeTown_Ep1_The_Microwave_v2.mp4
