#!/bin/bash
# Film shots. Run after: build.py QA, build.py SIM, SEL render, screen.py.   (SKIP="A B" to skip finished parts)
cd "$(dirname "$0")"
run() { case " $SKIP " in *" $2 "*) echo "$2 skipped"; return;; esac
  python3 build.py $1 frames/$2 --samples 12 --pct 75 --engine cycles --step $3 --frames $4 > logs_$2.txt 2>&1 || { echo "$2 FAILED"; exit 1; }
  echo "$2 done $(date +%T) $(ls frames/$2/*.png | wc -l)"; }
run A A 2 1-40
run B B 1 41-110
run C C 2 111-180
run D D 1 181-216
run DP DP 1 217-300
run E E 2 301-335
run F F1 2 336-397
run F F2 1 398-440
run F F3 2 441-465
echo ALL_RENDERED
