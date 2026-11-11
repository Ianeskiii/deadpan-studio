#!/bin/bash
# v2 film shots (run after vo16.py, build.py QA and tv.py).   SKIP="A C" to skip finished parts
cd "$(dirname "$0")"
run() { case " $SKIP " in *" $2 "*) echo "$2 skipped"; return;; esac
  python3 build.py $1 frames/$2 --samples 12 --pct 75 --engine cycles --step $3 --frames $4 > logs_$2.txt 2>&1 || { echo "$2 FAILED"; exit 1; }
  echo "$2 done $(date +%T) $(ls frames/$2/*.png | wc -l)"; }
run A A 1 1-66
run C C 1 67-96
run E E 2 115-204
run G G 2 205-345
echo ALL_RENDERED
