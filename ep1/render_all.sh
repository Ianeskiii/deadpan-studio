#!/bin/bash
cd "$(dirname "$0")"
for S in ${SHOTS:-S3 S4 S5 S6 S2 S1}; do
  python3 build.py $S frames/$S --samples 12 --pct 75 --engine cycles --step 2 > logs_$S.txt 2>&1
  echo "$S done $(date +%T)"
done
