#!/bin/bash
cd "$(dirname "$0")"
for S in ${SHOTS:-S4 S5 S6 S3 S1 S7 S8 S9 S10}; do
  ST=2; [ $S = S4 ] && ST=1
  python3 build11b.py $S frames2/$S --samples 12 --pct 75 --engine cycles --step $ST > logs2_$S.txt 2>&1 || { echo "$S FAILED"; exit 1; }
  echo "$S done $(date +%T)"
done
./assemble11b.sh && echo ASSEMBLED
