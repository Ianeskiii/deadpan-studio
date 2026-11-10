#!/bin/bash
cd "$(dirname "$0")"
for S in ${SHOTS:-E5 E7 E8 E2 E3 E4 E6 E1 E9 E10}; do
  ST=2; [ $S = E5 ] && ST=1
  python3 build11e.py $S frames5/$S --samples 12 --pct 75 --engine cycles --step $ST > logs5_$S.txt 2>&1 || { echo "$S FAILED"; exit 1; }
  echo "$S done $(date +%T)"
done
./assemble11e.sh && echo ASSEMBLED
