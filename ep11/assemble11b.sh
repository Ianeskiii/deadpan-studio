#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p parts2; : > parts2/list.txt
declare -A DUR=( [S1]=2.5 [S3]=0.9 [S4]=2.9 [S5]=2.8 [S6]=2.2 [S7]=0.8 [S8]=1.4 [S9]=1.5 [S10]=1.0 )
for S in S1 S3 S4 S5 S6 S7 S8 S9 S10; do
  FPS=15; [ $S = S4 ] && FPS=30
  ffmpeg -v error -y -framerate $FPS -pattern_type glob -i "frames2/$S/*.png" -i caption.png \
    -filter_complex "[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay,format=yuv420p" \
    -t ${DUR[$S]} -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30 parts2/tmp_$S.mp4
  mv parts2/tmp_$S.mp4 parts2/$S.mp4; echo "file '$S.mp4'" >> parts2/list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i parts2/list.txt -c copy parts2/video.mp4
python3 audio11b.py
ffmpeg -v error -y -i parts2/video.mp4 -i ep11b_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest TubeTown_Robbed_Music_v2.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 TubeTown_Robbed_Music_v2.mp4
