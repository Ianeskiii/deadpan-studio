#!/bin/bash
# Film shots (ranges in beats.json). Step 1 for movement (walk/eating, crumb fall), 2 for holds.   SKIP="A B" skips finished shots.
cd "$(dirname "$0")"
run() { case " $SKIP " in *" $1 "*) echo "$1 skipped"; return;; esac
  python3 build.py $1 frames/$1 --samples 12 --pct 75 --engine cycles --step $2 > logs_$1.txt 2>&1 || { echo "$1 FAILED"; exit 1; }
  echo "$1 done $(date +%T) $(ls frames/$1/*.png | wc -l)"; }
run A 1; run B 2; run C 2; run D 2; run E 2; run F 1; run G 2; run H 2; run I 2
echo ALL_RENDERED
