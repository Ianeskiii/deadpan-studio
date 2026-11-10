#!/bin/bash
cd "$(dirname "$0")"
FP=$(python3 -c "import json;T=json.load(open('vo/timing.json'));print(int(round(T['lines'][4]['t']*30))+1)")
run() { python3 build.py $1 frames/$2 --samples 12 --pct 75 --engine cycles --step $3 --frames $4 > logs_$2.txt 2>&1 || { echo "$2 FAILED"; exit 1; }; echo "$2 done $(date +%T) $(ls frames/$2/*.png | wc -l)"; }
XS=$(python3 -c "import json;print(json.load(open('beats.json'))['SHOTS']['X'][0])"); XE=$(python3 -c "import json;print(json.load(open('beats.json'))['SHOTS']['X'][1])")
[ -z "$SKIPWO" ] && run W W 2 1-20
[ -z "$SKIPWO" ] && run O O 2 21-45
run M M1 2 46-$((FP-1))
run M M2 1 $FP-$((XS-1))
run X X 1 $XS-$XE
echo ALL_RENDERED
