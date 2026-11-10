#!/bin/bash
# The phone's front-camera view (what the screen shows), then the screen frames.
cd "$(dirname "$0")"
python3 build.py QA x > /dev/null 2>&1 && python3 build.py SIM x | grep SIM
python3 build.py SEL frames/SEL --samples 10 --pct 50 --engine cycles --frames 60-112 > logs_SEL.txt 2>&1 && python3 build.py SEL frames/SEL --samples 10 --pct 50 --engine cycles --frames 180-301 >> logs_SEL.txt 2>&1 || { echo SEL FAILED; exit 1; }   # screen only seen in shots B and D
python3 screen.py
