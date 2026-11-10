#!/usr/bin/env bash
# One-time setup for a fresh Claude workspace (Linux, Python 3.13). Run from the repo root:  bash setup.sh
set -euo pipefail
cd "$(dirname "$0")"
PIP="pip install -q --break-system-packages"
$PIP bpy==5.2.3 kokoro-onnx==0.6.1 "misaki[ja]==0.7.4" pyopenjtalk-plus faster-whisper numpy scipy soundfile pillow
command -v ffmpeg >/dev/null || { apt-get update -qq && apt-get install -y -qq ffmpeg; }
# Sticky Animation channel (channels/sticky): skia-python draws the frames; fonts are bundled in channels/sticky/fonts,
# timing reuses faster-whisper + whisper_small from above.
$PIP skia-python==144.1
# skia-python needs the system EGL/GL libraries (missing on GitHub's ubuntu runners and some workspaces).
ldconfig -p | grep -q 'libEGL.so.1' || { SUDO=$(command -v sudo || true); $SUDO apt-get update -qq && $SUDO apt-get install -y -qq libegl1 libgl1 libgles2 >/dev/null; }

mkdir -p .cache tts whisper_small jp_dl/dic
cd .cache
get() { # npm package -> .cache/<dir>/package
  [ -d "$2/package" ] && return; mkdir -p "$2"; (cd "$2" && npm pack -q "$1" >/dev/null && tar xzf ./*.tgz); }
get kokoro-q8-shards@1.0.0 kokoro-q8-shards
get kokoro-local-runtime@0.1.0 kokoro-local-runtime
get kokoro-js-jp@0.2.0 kokoro-js-jp
get kokoro-js@1.2.1 kokoro-js
for i in 0 1 2 3; do get @skillninja/shortmovie-telop-model-p$i@1.0.0 whisper-p$i; done
cd ..

# Kokoro TTS model (6 shards) and voices
cat .cache/kokoro-q8-shards/package/kokoro-q8.part{0,1,2,3,4,5}.bin > tts/kokoro-q8.onnx
python3 tools/make_voices.py .cache
# Whisper-small (CTranslate2) for speech checks
cp .cache/whisper-p0/package/{config.json,tokenizer.json,vocabulary.json,preprocessor_config.json} whisper_small/
cat .cache/whisper-p{0,1,2,3}/package/model.bin.part* > whisper_small/model.bin
# OpenJTalk dictionary for Japanese voices
tar xzf .cache/kokoro-js-jp/package/dist/open_jtalk_dic_utf_8-1.11.tar.gz -C jp_dl/dic

python3 -c "import bpy, kokoro_onnx, faster_whisper; print('Blender', bpy.app.version_string)"
python3 -c "import skia; print('skia-python', skia.__version__, '(sticky channel)')"
echo "Setup done."
