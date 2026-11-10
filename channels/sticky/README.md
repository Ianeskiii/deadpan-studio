# STICKY ANIMATION channel

Stick-figure true-story Shorts, made in two stages: Claude writes the narration, the owner voices it in ElevenLabs and uploads the MP3, then Claude makes the video to fit that audio. **Read [PLAYBOOK.md](PLAYBOOK.md) first.** It has the owner's standard prompts word for word and every step.

| File | What it is |
|---|---|
| `lib.py` | Every drawing asset: stick-figure characters (`CHARS`, hair kinds, expressions, poses), props, sets, maps, skies and effects. It's cumulative, so add new assets here. Fonts are pinned to `fonts/`. |
| `core.py` | Episode helpers: timeline access (`lt0`, `wt`), pop tags, bubbles, brackets, checks, the colour grade, grain and vignette (`grade`). |
| `render.py` | Frame renderer: camera moves and handheld drift, six transition types, one-word captions, the loop blend into the hook. One mp4 per scene. |
| `sfx.py` | Music bed, sound effects and the final mix (music ducked under the voice). |
| `timeline.py` | MP3 + narration → `voice.wav` + `timeline.json` with word times. |
| `sticky.py` | `prep` / `stills` / `render` / `audio` commands that wrap all of the above. |
| `template/` | Starter `scenes.py` / `audio.py` for a new episode. |
| `examples/` | The four sticky shorts delivered so far (Virginia Hall, Kara Robinson, James Howells, the Coughing Major), as reference. |
| `episodes/<id>/` | One folder per sticky short, with `scenes.py`, `audio.py`, `lines.txt`, `timeline.json` and `source.json`. Render outputs are git-ignored. |

Output: 1080x1920, 30 fps, H.264 (veryfast, CRF 18) + AAC 192k, loopable.
