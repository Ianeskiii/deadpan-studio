#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p parts; : > parts/list.txt
for S in B1 B2 A3 A4 A5; do
  ffmpeg -v error -y -framerate 15 -pattern_type glob -i "frames/$S/*.png" -i caption.png \
    -filter_complex "[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay,format=yuv420p" \
    -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30 parts/tmp_$S.mp4
  mv parts/tmp_$S.mp4 parts/$S.mp4; echo "file '$S.mp4'" >> parts/list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i parts/list.txt -c copy parts/video.mp4
python3 audio10.py
ffmpeg -v error -y -i parts/video.mp4 -i ep10_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest TubeTown_Alarm_v2.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 TubeTown_Alarm_v2.mp4
