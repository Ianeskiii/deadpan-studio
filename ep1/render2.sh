#!/bin/bash
cd "$(dirname "$0")"
rm -rf frames/S4 frames/S6
for spec in S6:2 S7:2 S4:1 S8:1; do S=${spec%%:*}; st=${spec##*:}
  python3 build.py $S frames/$S --samples 12 --pct 75 --engine cycles --step $st > logs_$S.txt 2>&1 || { echo "$S FAILED"; exit 1; }
  echo "$S done $(date +%T)"
done
./assemble2.sh && echo ASSEMBLED
