#!/bin/bash
cd "$(dirname "$0")"
for S in ${SHOTS:-A B C D E F}; do
  ST=2; [ $S = D ] || [ $S = J ] || [ $S = FC ] && ST=1
  python3 build16.py $S frames5/$S --samples 12 --pct 75 --engine cycles --step $ST > logs5_$S.txt 2>&1 || { echo "$S FAILED"; exit 1; }
  echo "$S done $(date +%T) $(ls frames5/$S/*.png | wc -l)"
done
echo ALL_RENDERED
