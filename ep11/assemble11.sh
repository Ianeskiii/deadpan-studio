#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p parts; : > parts/list.txt
declare -A DUR=( [R1]=3.0 [R2]=2.0 [R3]=2.0 [R4]=3.0 [R5]=2.5 [R6]=1.5 [R7]=2.0 )
for S in R1 R2 R3 R4 R5 R6 R7; do
  ffmpeg -v error -y -framerate 15 -pattern_type glob -i "frames/$S/*.png" -i caption.png \
    -filter_complex "[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay,format=yuv420p" \
    -t ${DUR[$S]} -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30 parts/tmp_$S.mp4
  mv parts/tmp_$S.mp4 parts/$S.mp4; echo "file '$S.mp4'" >> parts/list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i parts/list.txt -c copy parts/video.mp4
python3 audio11.py
ffmpeg -v error -y -i parts/video.mp4 -i ep11_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest TubeTown_Robbed_Music.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 TubeTown_Robbed_Music.mp4
