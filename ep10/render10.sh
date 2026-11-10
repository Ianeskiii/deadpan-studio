#!/bin/bash
cd "$(dirname "$0")"
for S in ${SHOTS:-A5 A3 A1 A2 A4}; do
  python3 build10.py $S frames/$S --samples 12 --pct 75 --engine cycles --step 2 > logs_$S.txt 2>&1 || { echo "$S FAILED"; exit 1; }
  echo "$S done $(date +%T)"
done
./assemble10.sh && echo ASSEMBLED
