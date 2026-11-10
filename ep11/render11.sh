#!/bin/bash
cd "$(dirname "$0")"
for S in ${SHOTS:-R3 R4 R5 R2 R1 R6 R7}; do
  python3 build11.py $S frames/$S --samples 12 --pct 75 --engine cycles --step 2 > logs_$S.txt 2>&1 || { echo "$S FAILED"; exit 1; }
  echo "$S done $(date +%T)"
done
./assemble11.sh && echo ASSEMBLED
