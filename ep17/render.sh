#!/bin/bash
# ep17 film shots (after vo17.py, screen.py, build.py QA).   SKIP="A B" to skip finished parts
cd "$(dirname "$0")"
run() { case " $SKIP " in *" $2 "*) echo "$2 skipped"; return;; esac
  python3 build.py $1 frames/$2 --samples 12 --pct 75 --engine cycles --step $3 --frames $4 > logs_$2.txt 2>&1 || { echo "$2 FAILED"; exit 1; }
  echo "$2 done $(date +%T) $(ls frames/$2/*.png | wc -l)"; }
run A A 1 1-25
run I I 2 26-40
run B B 1 41-110
run S S 2 111-165
run C C 2 166-255
run D D 2 256-360
run E E 2 361-432
echo ALL_RENDERED
