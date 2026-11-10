#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p parts5; : > parts5/list.txt
for spec in E1:15:3.0 E2:15:1.5 E3:15:1.0 E4:15:1.0 E5:30:3.0 E6:15:0.5 E7:15:2.0 E8:15:2.0 E9:15:1.0 E10:15:1.0; do
  IFS=: read S FPS DUR <<< "$spec"
  case $S in
    E2) EX=(-i sub_demand.png); FC="[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay[c];[c][2]overlay=enable='between(t,0.3,1.45)',format=yuv420p";;
    E9) EX=(-i sub_giveup.png); FC="[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay[c];[c][2]overlay=enable='gte(t,0.05)',format=yuv420p";;
    *)  EX=(); FC="[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay,format=yuv420p";;
  esac
  ffmpeg -v error -y -framerate $FPS -pattern_type glob -i "frames5/$S/*.png" -i caption.png "${EX[@]}" -filter_complex "$FC" \
    -t $DUR -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30 parts5/tmp_$S.mp4
  mv parts5/tmp_$S.mp4 parts5/$S.mp4; echo "file '$S.mp4'" >> parts5/list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i parts5/list.txt -c copy parts5/video.mp4
python3 audio11e.py
ffmpeg -v error -y -i parts5/video.mp4 -i ep11e_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest TubeTown_Robbed_Music_v5.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 TubeTown_Robbed_Music_v5.mp4
