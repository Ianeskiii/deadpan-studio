#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p parts seq
rm -rf seq/*; mkdir -p seq/S1a seq/S1b
for f in frames/S1/S1_*.png; do n=$((10#$(basename $f .png | cut -d_ -f2))); if [ $n -le 23 ]; then ln -sf ../../$f seq/S1a/; else ln -sf ../../$f seq/S1b/; fi; done
for S in S2 S3 S4 S5 S6; do ln -sfn ../frames/$S seq/$S; done
: > parts/list.txt
for S in S1b S2 S3 S4 S5 S6 S1a; do
  ffmpeg -v error -y -framerate 15 -pattern_type glob -i "seq/$S/*.png" -i caption.png \
    -filter_complex "[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay=0:0,format=yuv420p" \
    -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30 parts/tmp_$S.mp4
  mv parts/tmp_$S.mp4 parts/$S.mp4
  echo "file '$S.mp4'" >> parts/list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i parts/list.txt -c copy parts/video.mp4
ffmpeg -v error -y -i parts/video.mp4 -i ep1_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest TubeTown_Ep1_The_Microwave.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 TubeTown_Ep1_The_Microwave.mp4
