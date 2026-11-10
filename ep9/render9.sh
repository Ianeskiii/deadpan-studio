#!/bin/bash
cd "$(dirname "$0")"
for S in ${SHOTS:-T5 T6 T1 T2 T3 T4}; do
  python3 build9.py $S frames/$S --samples 12 --pct 75 --engine cycles --step 2 > logs_$S.txt 2>&1 || { echo "$S FAILED"; exit 1; }
  echo "$S done $(date +%T)"
done
./assemble9.sh && echo ASSEMBLED
