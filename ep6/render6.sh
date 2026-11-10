#!/bin/bash
cd "$(dirname "$0")"
for S in E4 E3 E7 E1 E5 E2 E6; do
  python3 build6.py $S frames/$S --samples 12 --pct 75 --engine cycles --step 2 > logs_$S.txt 2>&1 || { echo "$S FAILED"; exit 1; }
  echo "$S done $(date +%T)"
done
./assemble6.sh && echo ASSEMBLED
