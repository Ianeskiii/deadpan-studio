#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p parts6; : > parts6/list.txt
# shot:fps:dur:[sub:start:end ...] (times relative to shot start)
for spec in "A:15:2.0" "B:15:4.0:s_g1:0.1:2.85" "C:30:5.6666667:s_g2:2.55:3.45:s_g3:3.55:4.95" "D:15:2.5666667:s_g4:0.2:2.7" "E:15:1.7666667:s_d1:0.3:1.25"; do
  IFS=: read -r S FPS DUR REST <<< "$spec"
  IN=(-framerate $FPS -pattern_type glob -i "frames6/$S/*.png" -i caption.png); FC="[0]scale=1080:1920:flags=lanczos,fps=30[v0];[v0][1]overlay[v1]"; n=2; last=v1
  if [ -n "$REST" ]; then
    IFS=: read -ra P <<< "$REST"
    for ((i=0; i<${#P[@]}; i+=3)); do
      IN+=(-i "${P[i]}.png"); FC="$FC;[$last][$n]overlay=enable='between(t,${P[i+1]},${P[i+2]})'[v$n]"; last=v$n; n=$((n+1))
    done
  fi
  FC="$FC;[$last]format=yuv420p[out]"
  ffmpeg -v error -y "${IN[@]}" -filter_complex "$FC" -map "[out]" -t $DUR -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30 parts6/tmp_$S.mp4
  mv parts6/tmp_$S.mp4 parts6/$S.mp4; echo "file '$S.mp4'" >> parts6/list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i parts6/list.txt -c copy parts6/video.mp4
python3 audio11f.py
ffmpeg -v error -y -i parts6/video.mp4 -i ep11f_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest TubeTown_Robbed_Music_v6.mp4
ffprobe -v error -show_entries format=duration:stream=width,height -of compact TubeTown_Robbed_Music_v6.mp4
