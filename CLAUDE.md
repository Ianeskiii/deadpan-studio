# Deadpan Studio — instructions for Claude

This repo is the production pipeline for **Tube Town / Deadpan Doug**, an animated YouTube Shorts series (English, US audience, 9:16, deadpan comedy in the spirit of Nobody Sausage). The owner uses several of their own Claude accounts. Any of them may open this repo and run production. Treat every account as the same owner.

## Channels

The studio runs two channels. Each short's `short.json` has a `channel` field; a short without one is `"deadpan-doug"`.

- **`deadpan-doug`**: Tube Town / Deadpan Doug, 3D in Blender. Everything below this section is for this channel and is unchanged.
- **`sticky`**: STICKY ANIMATION, stick-figure true-story shorts made in two stages with the owner's ElevenLabs voice in between. The pipeline lives in `channels/sticky/`, and **`channels/sticky/PLAYBOOK.md` is its instruction book**: the owner's two standard prompts word for word, the stages and every command. Sticky shorts use one extra status, `needs-audio` (narration written, waiting for the owner's MP3), plus `narration.txt` and the owner's `.mp3` in `shorts/<id>/`. Their revisions have `kind: "narration"` (back to Stage 1) or `kind: "video"` (Stage 2 only).

## The studio (queue and history live in this repo)

Everything is plain files in this repo, so any of the owner's Claude accounts can run production with only the repo attached. Don't use the old claude.ai artifact studio (`studio/deadpan-studio.html`): other accounts can't read its data.

- **Website:** GitHub Pages serves `index.html` + `studio.js` from `main` at https://ianeskiii.github.io/deadpan-studio/. It reads the files below. New requests from the site arrive as new files committed by the owner on GitHub.
- **Shorts:** `shorts/<id>/short.json`, with the finished versions next to it as `v<N>.mp4` and `v<N>.jpg`. Fields:
  - `id`, `title`, `description` (the brief), `durationMin`, `durationMax`
  - `characters` (library ids; empty means Doug), `newCharacters`, `scene` (library id), `newScene`, `reference` (optional link)
  - `status` (`queued` | `working` | `revision` | `ready` | `failed`), `stage`, `stageIndex`, `progress`, `etaMinutes`, `note`, `episode` (the `epNN` folder)
  - `versions` (`{v, video, poster, seconds, notes}`), `revisions` (`{text, at, done, doneIn}`), `createdAt`, `updatedAt`
- **Revision requests** arrive as `shorts/<id>/revision-<ms>.json`.
- **Libraries:** `library/characters.json` and `library/scenes.json`, with images in `library/img/`. Requests for new ones arrive as `library/requests/<kind>-<slug>.json`.
- **Helper:** `tools/studio.py` does the bookkeeping. Every write command commits and pushes, so the website updates as you work.

STAGES = `["Queued", "Script & timing", "Voices", "Set & cast", "Animation", "Test frames", "Rendering", "Sound & edit", "Final check", "Ready"]`

## "Run the queue"

This usually runs by itself: `.github/workflows/run-queue.yml` starts Claude in GitHub Actions whenever a short, revision or library request is committed, every 3 hours to resume unfinished work, or by hand from the Actions tab. It uses the repo secrets `CLAUDE_TOKEN_1`, `CLAUDE_TOKEN_2` and `CLAUDE_TOKEN_3` (one per Claude account, made with `claude setup-token`). When one account hits its limit, the next one continues. One run lasts at most about 6 hours. A chat session saying "run the queue" does the same work by hand.


### Local mode (the owner's PC, no GitHub)

The owner can also run everything on their Windows PC inside WSL (`LOCAL.md`). `local/start.sh` sets up `.venv` (Python 3.13) and runs `setup.sh`, then `tools/local_studio.py` serves the website at http://localhost:8080, saves new shorts, revisions, library requests and MP3 uploads straight into this folder, and starts `claude -p` with `STUDIO_LOCAL=1` whenever there is work. In local mode:
- `tools/studio.py` commits on the PC only: it never pulls or pushes. Don't use `git pull`, `git push` or `gh`; skip the "push" parts of the steps below.
- Use the `.venv` Python (it is first on PATH). Everything else, including the sticky playbook and its sync checks, is the same.

1. Run `python3 tools/studio.py queue`. It pulls, folds revision files into their short, and lists what's waiting, oldest first, plus library requests. It also lists anything stuck at `working` from an account that ran out of usage: resume those.
   For each **sticky** short, `queue` prints which stage it needs ("STAGE 1 narration" or "STAGE 2 video"). Do that stage exactly as `channels/sticky/PLAYBOOK.md` says instead of steps 2–5 below. Sticky shorts waiting in `needs-audio` with no `.mp3` are skipped, so don't touch them. Everything else in this list is for Deadpan Doug shorts.
2. For each short:
   - Run `python3 tools/studio.py stage <id> <stageIndex> [etaMinutes] ["note"]` at every stage (1 = Script & timing … 8 = Final check).
   - Build it as a new `epNN/` folder, the next free number, modelled on `ep12/` (dialogue) or `ep13/` (no dialogue). Set `"episode": "epNN"` in its short.json.
   - For a revision, read the open revisions, edit that short's existing `epNN/` scripts and re-render.
3. When the video passes its checks, run `python3 tools/studio.py version <id> <final.mp4> <poster.jpg> <seconds> "<what changed>"`. This adds `v<N>`, marks open revisions done and sets the short to ready.
4. For library requests, and new characters or scenes a short needed:
   - Add an entry to `library/characters.json` or `library/scenes.json`: `id`, `name`, `description`, `status: "ready"`, `image: "library/img/<id>.jpg"` (a 600 px crop from a render), `order`; for characters also `role`, `voice`, `color`.
   - Delete the request file.
5. Commit and push the `epNN/` code plus a new row in `EPISODES.md`.
6. If a short can't be made, run `python3 tools/studio.py fail <id> "<reason>"`.

Commit and push often. If this account runs out of usage mid-render, the next account continues from the repo: its scripts, and `stageIndex` in short.json, show where things stopped. Rendered frames are not committed, so they are re-rendered.

## Setup in a fresh workspace

Run `bash setup.sh` (about a minute). It installs Blender (bpy 5.2.3), Kokoro TTS, misaki and pyopenjtalk for Japanese, faster-whisper and ffmpeg. It also rebuilds the model files, which are not committed: `tts/kokoro-q8.onnx`, `tts/voices.bin`, `tts/voices_jp.bin`, `whisper_small/` and `jp_dl/dic/`.
For the sticky channel it also installs skia-python. The sticky fonts are committed in `channels/sticky/fonts/`, and its timing step reuses faster-whisper and `whisper_small/`.

## How an episode is built (see `ep12/` and `ep13/`)

### Folder layout

Keep the top-level layout. Scripts use relative paths such as `../tubetown`, `../tts`, `../ep11/helpers_e.py` and `../jp_dl`.

### Core pieces

- `tubetown/lib.py` holds materials, the Doug rig, walk and lip-sync. Episode scenes `exec` it, so run each scene with `cd epNN && python3 build.py SHOT OUTDIR [...]`.
- `ep12/rig.py` is the rubber-hose rig. `ep11/helpers_e.py` holds shared helpers.

### Voices

- Kokoro via kokoro_onnx: Doug = `am_fenrir`, barista = `af_heart`, Ricky = `am_michael`.
- Use `is_phonemes=True` for words TTS gets wrong. Doug's name is `dˈʌɡ`; "Dog" is `dˈɔːɡ`.
- Japanese uses `ep13/jtts.py` (misaki ja + OpenJTalk), voices `jm_kumo` and `jf_alpha`.

### Rendering

- Cycles: samples 12, resolution pct 75, OIDN denoise, frame step 2 for holds and 1 for fast action.
- One encoded mp4 per shot. Join them with the ffmpeg concat demuxer and `-c copy`, then mux the audio.

### Faces

- Eyelid rotation: about 22–24 is Doug's deadpan, about −22 to −40 is wide open, 90+ is shut.
- Use `aim()` to point the eyes.

### Checks before delivery

- Speech: `python3 asr.py whisper_small file.wav` (English) or `asr_ja.py` (Japanese). Whisper biases "Dog" toward "Doug" in full-video context, so check single lines.
- Mouth visibility: `ep12/qa12.py`. Gaze order: `ep12/qa_gaze15.py`.
- Look at full-size frames at the busiest moments before the final render.

### Style

- Doug never overreacts. Copy his look from the existing rigs; don't redesign him.
- Comedy comes from timing, stillness and eye movement.
- Captions are burned in, in the Permanent Marker font (`ep12/marker.ttf`).
