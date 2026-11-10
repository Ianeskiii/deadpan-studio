# Deadpan Studio — instructions for Claude

This repo is the production pipeline for **Tube Town / Deadpan Doug**, an animated YouTube Shorts series (English, US audience, 9:16, deadpan comedy in the spirit of Nobody Sausage). The owner uses several of their own Claude accounts. Any of them may open this repo and run production. Treat every account as the same owner.

## The studio website (shared queue and history)

- URL: https://claude.ai/artifact/LjaCXL7X6qtSUCa2RfoV7L
- Source: `studio/deadpan-studio.html`. Capabilities: `{"db": {}, "assets": {}, "downloads": true, "user": {}}`.
- The account running production must be an **Editor** on the studio (invited by email). Read and write its database with the ArtifactData tool, using the URL above. Upload videos and posters as assets with the Artifact tool (`asset: true`) and store the returned asset id.
- Before any publish to the studio page, read it first (`action: "read"`). Never publish without that read, and never drop the db, assets, downloads or user capabilities.

### Database

`shorts/<id>`:
- `title`, `description` (the act/brief), `durationMin`, `durationMax` (seconds)
- `characters` (ids from the library; empty means Doug), `newCharacters` (free text: build these), `scene` (scene id), `newScene` (free text)
- `refAsset` (asset id of the reference video, or empty), `refNote`
- `status`: `queued` | `working` | `revision` | `ready` | `failed`
- `stage`, `stageIndex` (index into STAGES below), `progress` (0–100), `etaMinutes` (minutes from `updatedAt`), `note` (short status line)
- `versions`: list of `{v, video, poster, seconds, notes}`; `video` and `poster` are asset ids
- `revisions`: list of `{text, at, done, doneIn}`
- `createdAt`, `updatedAt` (ms epoch)

STAGES = `["Queued", "Script & timing", "Voices", "Set & cast", "Animation", "Test frames", "Rendering", "Sound & edit", "Final check", "Ready"]`

`characters/<id>` and `scenes/<id>`:
- `name`, `description`, `status` (`requested` | `ready`), `image` (asset id), `order`
- Characters only: `role`, `voice` (Kokoro voice id), `color` (#hex)

## "Run the queue"

1. Read `shorts` where status is `queued` or `revision`, oldest first. Also read `characters` and `scenes` where status is `requested`.
2. For each short:
   - Set `status: "working"` and update `stage`, `stageIndex`, `progress`, `etaMinutes` and `updatedAt` at every stage.
   - Build it as a new `epNN/` folder modelled on `ep12/` (dialogue) or `ep13/` (no dialogue).
3. When the video passes its checks:
   - Upload the mp4 and a poster frame as assets.
   - Append to `versions`. Set `status: "ready"`, `stage: "Ready"`, `stageIndex: 9`, `progress: 100`.
   - For a revision, mark the open revisions `done: true, doneIn: <v>`.
4. Add new characters and scenes to the library: set `status: "ready"`, upload a portrait or still as `image`, and pick a voice for characters.
5. Commit the new `epNN/` code and update `EPISODES.md`, then push. The repo is the shared history between accounts.

If a short can't be made, set `status: "failed"` and put the reason in `note`.

## Setup in a fresh workspace

Run `bash setup.sh` (about a minute). It installs Blender (bpy 5.2.3), Kokoro TTS, misaki and pyopenjtalk for Japanese, faster-whisper and ffmpeg. It also rebuilds the model files, which are not committed: `tts/kokoro-q8.onnx`, `tts/voices.bin`, `tts/voices_jp.bin`, `whisper_small/` and `jp_dl/dic/`.

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
