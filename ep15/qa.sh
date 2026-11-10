#!/bin/bash
# V2 test stills (low quality) at the beats that changed
cd "$(dirname "$0")"
q() { python3 build.py $1 qa/$1 --samples 8 --pct 40 --engine cycles "${@:2}" > qa/log_$1.txt 2>&1; echo "$1 $(ls qa/$1 | wc -l)"; }
q F --frames 390-438 --step 6
q B --frames 128-156 --step 14
q D --frames 262-308 --step 12
q H --frames 486-530 --step 22
q G --frames 470-470
q I --frames 553-563 --step 5
echo QA_DONE
