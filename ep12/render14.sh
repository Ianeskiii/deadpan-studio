#!/bin/bash
cd "$(dirname "$0")"
for S in ${SHOTS:-A B C D E F}; do
  ST=2; [ $S = D ] || [ $S = G ] && ST=1
  python3 build14.py $S frames3/$S --samples 12 --pct 75 --engine cycles --step $ST > logs3_$S.txt 2>&1 || { echo "$S FAILED"; exit 1; }
  echo "$S done $(date +%T) $(ls frames3/$S/*.png | wc -l)"
done
echo ALL_RENDERED
