#!/bin/bash
cd "$(dirname "$0")"
for S in ${SHOTS:-N1 N2 N3a N3b N4 N5 N6a N6b N7 C5 C6 C7 C8 C9 C10 C3 C4 C1 C2 C11 C12 C13 C14}; do
  ST=2; { [ $S = C5 ] || [ $S = C6 ]; } && ST=1
  python3 build11d.py $S frames4/$S --samples 12 --pct 75 --engine cycles --step $ST > logs4_$S.txt 2>&1 || { echo "$S FAILED"; exit 1; }
  echo "$S done $(date +%T)"
done
./assemble11d.sh && echo ASSEMBLED
