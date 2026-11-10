#!/bin/bash
cd "$(dirname "$0")"
for S in ${SHOTS:-C B D E A}; do
  ST=2; [ $S = C ] && ST=1
  python3 build11f.py $S frames6/$S --samples 12 --pct 75 --engine cycles --step $ST > logs6_$S.txt 2>&1 || { echo "$S FAILED"; exit 1; }
  echo "$S done $(date +%T)"
done
./assemble11f.sh && echo ASSEMBLED
