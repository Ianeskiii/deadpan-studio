#!/bin/bash
# The phone's front-camera view (what the screen shows), then the screen frames.
# v3: SEL only where the screen is seen up close (the B tail and the three POV inserts). The blanket cache (build.py SIM) is
# reused from v2 so the ending stays identical - run "python3 build.py SIM x" only in a fresh workspace without blanket.pc2.
cd "$(dirname "$0")"
python3 build.py QA x > /dev/null 2>&1
[ -f blanket.pc2 ] || python3 build.py SIM x | grep SIM
sel() { python3 build.py SEL frames/SEL --samples 10 --pct 50 --engine cycles --frames $1 >> logs_SEL.txt 2>&1 || { echo SEL FAILED $1; exit 1; }; }
: > logs_SEL.txt
sel 60-77; sel 151-185; sel 213-238; sel 263-282
python3 screen.py
