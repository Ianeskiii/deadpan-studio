#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p parts3; : > parts3/list.txt
declare -A DUR=( [C1]=1.5 [C2]=1.0 [C3]=0.5 [C4]=0.4 [C5]=1.6 [C6]=1.3 [C7]=1.4 [C8]=1.4 [C9]=1.1 [C10]=1.1 [C11]=0.8 [C12]=1.4 [C13]=1.5 [C14]=1.0 )
for S in C1 C2 C3 C4 C5 C6 C7 C8 C9 C10 C11 C12 C13 C14; do
  FPS=15; { [ $S = C5 ] || [ $S = C6 ]; } && FPS=30
  ffmpeg -v error -y -framerate $FPS -pattern_type glob -i "frames3/$S/*.png" -i caption.png \
    -filter_complex "[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay,format=yuv420p" \
    -t ${DUR[$S]} -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30 parts3/tmp_$S.mp4
  mv parts3/tmp_$S.mp4 parts3/$S.mp4; echo "file '$S.mp4'" >> parts3/list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i parts3/list.txt -c copy parts3/video.mp4
[ -f ep11b_audio.wav ] || python3 audio11b.py
ffmpeg -v error -y -i parts3/video.mp4 -i ep11b_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest TubeTown_Robbed_Music_v3.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 TubeTown_Robbed_Music_v3.mp4
