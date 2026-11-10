# STICKY ANIMATION — playbook

Stick-figure true-story Shorts: stick figures with white heads, semi-3D lit environments, one-word pop captions, a hook and a twist, and a seamless loop. Every short is made in two stages, and the owner generates the voice in ElevenLabs between them.

## The owner's workflow (word for word)

STAGE 1: NARRATION (automatic)
- I queue a sticky short with only a title, for example:
  "Thieves Broke Into a Diamond Vault Thought to Be Impenetrable — Antwerp diamond heist, 2003"
- Claude writes the narration using this exact instruction, which is my standard narration prompt:
  "Give me narration first with a strong hook and fast pacing and it should be loopable. It should be interesting to watch and viewers will finish it till the end. Don't create video yet, just give me narration as plain text."
- Research the facts first so the story is accurate.
- Save the narration as plain text in shorts/<id>/narration.txt, then set the short to a new status "needs-audio".

BETWEEN STAGES (me, outside the tool)
- On the website, a "needs-audio" sticky card shows the narration with a Copy button. I paste it into ElevenLabs and generate the MP3 myself.
- The card has an "Upload narration audio" button that opens https://github.com/Ianeskiii/deadpan-studio/upload/main/shorts/<id> so I can drop the MP3 into that short's folder (accept any .mp3 there).
- The card also has "Rewrite narration": I type what to change, and it becomes a revision request that sends the short back to Stage 1.

STAGE 2: VIDEO (automatic once the MP3 is in the folder)
- Committing an .mp3 under shorts/ must trigger the queue workflow.
- Claude makes the video to fit my audio using this exact instruction, which is my standard video prompt:
  "Make the video loopable so it will gain high retention. Make the video interesting and not boring with repetitive frames, avoid that. Make sure it is produced at a professional video editor level. Make sure the video will not appear as low effort, inauthentic, mass produced or repetitive as per YouTube policy."
- Style: use the exact sticky pipeline, style and settings you have been using in THIS session for my sticky videos. Don't redesign anything. Sync the visuals to the narration timing.
- Publish the finished video as a version, the same way Deadpan shorts do (tools/studio.py version). Video revisions re-run Stage 2 only.

## Which stage a sticky short needs

`python3 tools/studio.py queue` prints it for every sticky short:

| Short | Stage to run |
|---|---|
| `queued`, or an open revision with `kind: "narration"` | **Stage 1** (write or rewrite the narration) |
| `needs-audio` with no `.mp3` in `shorts/<id>/` | nothing: waiting for the owner (the queue and the workflow skip it) |
| `needs-audio` with an `.mp3`, or an open revision with `kind: "video"` (or no kind) on a short that already has narration and audio | **Stage 2** (make the video from the newest `.mp3`) |
| `working` | resume the stage shown by `stageIndex` (1 = narration, 3+ = video) |

Sticky stages (`stageIndex`): 0 Queued · 1 Writing narration · 2 Needs audio · 3 Timing · 4 Scenes · 5 Test frames · 6 Rendering · 7 Sound & edit · 8 Final check · 9 Ready.

## Stage 1: narration, step by step

1. `python3 tools/studio.py stage <id> 1 10 "Researching and writing the narration"`.
2. Research the story with WebSearch / WebFetch before writing: names, dates, numbers, how it ended. Use the title and the short's `description` (the owner's extra notes) as the brief. For a rewrite, apply the open narration revision text to the current `shorts/<id>/narration.txt`.
3. Write the narration exactly as the standard narration prompt asks, in the house style used for every sticky short so far:
   - A one-sentence hook that states the most shocking fact, then fast, punchy lines: short sentences, ellipses (…) for dramatic pauses, numbers and names said out loud.
   - About 150–200 words (roughly 85–105 seconds of ElevenLabs voice). Shorts are normally at least 1 minute, unless the owner's notes ask for another length.
   - 15–18 lines, **one narration line per row** of plain text, no headings, no quotes around it, no stage directions, no emoji.
   - Loopable: the last line is an unfinished lead-in ("And it all happened because…", "But it all came down to…") that runs straight back into the first line.
   - True and non-graphic: no gore, deaths only stated plainly, nothing sexual. Don't put words in real people's mouths.
4. Save it as `/tmp/narration.txt` (or anywhere) and run `python3 tools/studio.py narration <id> /tmp/narration.txt "<fact-check notes>"`. This writes `shorts/<id>/narration.txt`, deletes any older `.mp3` (it no longer matches the words), marks open narration revisions done, sets `status: "needs-audio"` and pushes. Put the fact-check flags you would have told the owner (title errors, disputed numbers, wording you softened) in the notes; the card shows them.

## Stage 2: video, step by step

The pipeline lives in `channels/sticky/` (skia-python at 1080x1920, 30 fps, libx264 veryfast CRF 18, numpy sound). `setup.sh` installs everything it needs. Work in `channels/sticky/episodes/<id>/`.

1. `python3 tools/studio.py stage <id> 3 60 "Timing the narration"`, then `python3 channels/sticky/sticky.py prep <id>`. It converts the newest `shorts/<id>/*.mp3`, trims trailing silence, aligns every narration word to the audio (faster-whisper word timestamps + the exact script words) and writes `timeline.json`. It prints every line with word times. If the audio doesn't match the narration text, follow the audio (edit `lines.txt`/timeline only if words were changed in ElevenLabs) and say so in the notes. It also copies `template/scenes.py` and `template/audio.py` into the episode folder if they aren't there yet.
2. `stage <id> 4 50 "Building the shots"`. Write the episode's `scenes.py` like the delivered examples in `channels/sticky/examples/` (Virginia Hall, Kara Robinson, James Howells, the Coughing Major), with `from core import *`:
   - **30–40 distinct, hand-built shots**, about one per 2–3 seconds, each starting on the narration beat it illustrates (`lt0(i)`, `wt(i, 'word')`). Never repeat a layout back to back. Recurring story motifs are good (they make it one story), identical frames are not.
   - Add any new props, sets or characters to `channels/sticky/lib.py` (it's cumulative: `CHARS.update({...})`, new draw functions; new hair kinds by wrapping `hair`). Check what exists first (`grep -n "^def " lib.py`).
   - **Hook** = `scenes()[0]`, camera A exactly `(1.0, 540, 960)`, and `shot_hook(cv, T, frozen=False)` must draw a clean frame when `frozen=True`. render.py blends the last 0.75 s into that frozen frame, so the video loops.
   - **Transitions:** give every shot one of `'cut' 'fade' 'whip' 'zoom' 'wipe' 'flash'`. Mix them and match them to the beat (flash for impacts, whip for time jumps, zoom for reveals).
   - **Camera:** a slow push or pan on every shot (camA → camB). render.py adds the handheld drift.
   - **Grade:** `ACTS = [(t, tint, strength), ...]`, one tint per act, ending on the first act's tint. Then `def overlay(cv, T): grade(cv, T, ACTS)` (adds grain and vignette).
   - **Text:** one-word captions are burned in automatically at y≈1395, so keep pop tags (`tag()`) and other text at y 180–620 or 1600–1850. Use name cards for real people, calendars for dates, maps with pins/arrows for places, stamps for verdicts and counters for numbers.
   - **House rules:** non-graphic (deaths only through candles, silhouettes or empty scenes; no blood or wounds; no weapon aimed at a child); no real brand logos or show logos/sets; no likeness of real public figures (silhouettes or plain stick figures with name cards only); no Nazi or other hate symbols; no copyrighted characters.
3. `stage <id> 5 40 "Test frames"`, then `python3 channels/sticky/sticky.py stills <id>`. Open every `stills/sheet*.jpg` with Read and fix the problems you see before rendering:
   - text cut off by the camera zoom or covered by the caption;
   - characters standing on tables (draw the person first, then the table, with feet lower) or hidden behind props;
   - tags overlapping each other;
   - empty or black areas, crown-looking spiky yellow hair (use cowlick or spiky_dark), anything graphic.
   Re-run stills for the shots you changed (`sticky.py stills <id> 12.5 40.1`).
4. `stage <id> 6 30 "Rendering"`. Write `audio.py` like `template/audio.py` (`from sfx import *`):
   - pick a music bed (`MINOR`, `NOIR`, or your own progression) with `calm`/`bright`/`hero` sections that follow the story;
   - add `transition_sfx()`;
   - add effects on the story beats (`thud`, `boom`, `cough`, `heart`, `siren`, `cash`, `wind`, `beep`, `type_`, `chime`, `sting`, `applause`, …).
   Then run `python3 channels/sticky/sticky.py render <id>`. It renders the scene files in parallel, mixes the sound with the music ducked under the voice, joins everything, adds the audio, and writes `final.mp4` and `poster.jpg`. It also prints the loop difference between the first and last frame.
5. `stage <id> 8 5 "Final check"`.
   - The loop difference should be under about 5. If it isn't, the hook's frozen frame doesn't match its first frame, so fix `shot_hook`.
   - Check that the length matches the timeline.
   - Look at a few frames of `final.mp4` around transitions.
6. Publish: `python3 tools/studio.py version <id> channels/sticky/episodes/<id>/final.mp4 channels/sticky/episodes/<id>/poster.jpg <seconds> "<what it shows / what changed>"`.
7. Commit and push the episode code (`channels/sticky/episodes/<id>/scenes.py`, `audio.py`, `lines.txt`, `timeline.json`, `source.json`) and any `lib.py` additions. Render outputs are git-ignored. Add a row to the "Sticky Animation" table in `EPISODES.md`.

**Video revisions** (`kind: "video"`): re-run Stage 2 only. Edit the existing `episodes/<id>/scenes.py` / `audio.py` (re-run `prep` first if a new `.mp3` was uploaded), render, and publish a new version. Don't touch the narration.

**Rewrite narration** (`kind: "narration"`): back to Stage 1. `studio.py narration` removes the old audio, and the owner uploads a new MP3.
