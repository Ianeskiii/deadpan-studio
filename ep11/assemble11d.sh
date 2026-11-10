#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p parts4; : > parts4/list.txt
while read S FPS DUR; do
  ffmpeg -v error -y -framerate $FPS -pattern_type glob -i "frames4/$S/*.png" -i caption.png \
    -filter_complex "[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay,format=yuv420p" \
    -t $DUR -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30 parts4/tmp_$S.mp4 < /dev/null
  mv parts4/tmp_$S.mp4 parts4/$S.mp4; echo "file '$S.mp4'" >> parts4/list.txt
done < edit_list.txt
ffmpeg -v error -y -f concat -safe 0 -i parts4/list.txt -c copy parts4/video.mp4
python3 audio11d.py
ffmpeg -v error -y -i parts4/video.mp4 -i ep11d_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest TubeTown_Robbed_Music_v4.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 TubeTown_Robbed_Music_v4.mp4
