#!/usr/bin/env bash
# Start Deadpan Studio in local mode (inside WSL / Ubuntu). Run from anywhere:  bash ~/deadpan-studio/local/start.sh
# First run: installs system packages (asks for your Ubuntu password once), Python 3.13 and the pipeline (~10-20 min).
# Later runs start in a few seconds. Then open http://localhost:8080 in your Windows browser.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)
say() { printf '\n\033[1m%s\033[0m\n' "$*"; }

if grep -qi microsoft /proc/version 2>/dev/null && [[ "$ROOT" == /mnt/* ]]; then
  say "Note: the studio folder is on the Windows drive ($ROOT). It works, but rendering is much faster if it lives in your Ubuntu home folder (see LOCAL.md)."
fi

# 1. System packages: ffmpeg, the libraries Blender and the sticky renderer need, and tools for setup.
PKGS="ffmpeg libxi6 libxkbcommon0 libsm6 libgl1 libegl1 libgles2 curl git ca-certificates"
MISSING=$(for p in $PKGS; do dpkg -s "$p" >/dev/null 2>&1 || echo "$p"; done)
if [ -n "$MISSING" ]; then
  say "Installing system packages: $(echo $MISSING)"
  sudo apt-get update -qq && sudo apt-get install -y -qq $MISSING
fi

# 2. Python 3.13 in .venv (the Blender module bpy 5.2.3 needs exactly this version). uv fetches it if Ubuntu doesn't have it.
if [ ! -x .venv/bin/python ] || ! .venv/bin/python -c 'import sys; assert sys.version_info[:2] == (3, 13)' 2>/dev/null; then
  if ! command -v uv >/dev/null && [ ! -x "$HOME/.local/bin/uv" ]; then
    say "Installing uv (Python manager)"
    curl -LsSf https://astral.sh/uv/install.sh | sh
  fi
  UV=$(command -v uv || echo "$HOME/.local/bin/uv")
  say "Creating the Python 3.13 environment (.venv)"
  rm -rf .venv
  "$UV" venv --seed --python 3.13 .venv
fi
export VIRTUAL_ENV="$ROOT/.venv" PATH="$ROOT/.venv/bin:$HOME/.local/bin:$PATH"

# 3. The pipeline (Blender, voices, whisper, skia, model files). Re-runs only when setup.sh changes.
STAMP=.venv/.setup-$(sha1sum setup.sh | cut -c1-12)
if [ ! -f "$STAMP" ]; then
  say "Setting up the pipeline (first time takes a while)"
  bash setup.sh
  rm -f .venv/.setup-*; touch "$STAMP"
fi

# 4. A local git history (no GitHub needed): every status change is committed on this PC.
if [ ! -d .git ]; then git init -q && git add -A && git -c user.name="Deadpan Studio" -c user.email=noreply@anthropic.com commit -qm "Local studio" || true; fi

# 5. Claude Code must be installed inside Ubuntu (not only on Windows) and signed in.
if ! command -v claude >/dev/null; then
  say "Claude Code isn't installed inside Ubuntu yet. Install it and sign in once, then start the studio again:"
  echo "    curl -fsSL https://claude.ai/install.sh | bash"
  echo "    claude          # sign in with your Claude account, then type /exit"
  echo "The website still opens, but nothing is produced until Claude Code is there."
fi

say "Starting Deadpan Studio: open http://localhost:${STUDIO_PORT:-8080}"
exec python tools/local_studio.py
