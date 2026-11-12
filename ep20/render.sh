#!/bin/bash
# ep20: one continuous 300-frame shot. Every frame (step 1) so the slow smile reads smoothly; 8 samples + OIDN.
cd "$(dirname "$0")"
python3 build.py S frames/S --samples ${SAMPLES:-8} --pct 75 --engine cycles --step 1 ${FR:+--frames $FR} > logs_S.txt 2>&1 || { echo "S FAILED"; exit 1; }
echo "S done $(date +%T)"
