#!/bin/bash
# ep19 film shots (after vo19.py, screen.py).   SKIP="A B" to skip finished parts
cd "$(dirname "$0")"
run() { case " $SKIP " in *" $1 "*) echo "$1 skipped"; return;; esac
  R=$(python3 -c "import beats as b; a,c=b.SH['$1']; print(f'{a}-{c}', b.STEP['$1'])")
  python3 build.py $1 frames/$1 --samples 12 --pct 75 --engine cycles --step ${R#* } --frames ${R% *} > logs_$1.txt 2>&1 || { echo "$1 FAILED"; exit 1; }
  echo "$1 done $(date +%T) $(ls frames/$1/*.png | wc -l)"; }
for s in A B C O D E F; do run $s; done
echo ALL_RENDERED
