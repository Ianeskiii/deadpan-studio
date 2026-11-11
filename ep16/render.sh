#!/bin/bash
# Film shots (run after build.py QA and tv.py).   SKIP="A B" to skip finished parts
cd "$(dirname "$0")"
run() { case " $SKIP " in *" $2 "*) echo "$2 skipped"; return;; esac
  python3 build.py $1 frames/$2 --samples 12 --pct 75 --engine cycles --step $3 --frames $4 > logs_$2.txt 2>&1 || { echo "$2 FAILED"; exit 1; }
  echo "$2 done $(date +%T) $(ls frames/$2/*.png | wc -l)"; }
run A A 1 1-112
run B B 1 113-205
run C C 2 206-258
run E E 2 291-420
run F F 2 421-510
run G G 2 511-640
echo ALL_RENDERED
