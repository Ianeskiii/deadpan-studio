# Episode history

Finished videos (with all versions) live on the studio site. The code for each episode is in its folder here.

| Folder | Short | Versions | Notes |
|---|---|---|---|
| ep1 | The Microwave | v1, v2 | Doug and Tina |
| ep6 | Five Minutes Away | v1 | |
| ep9 | Forgot My Phone | v1, v2 | |
| ep10 | Alarm 6:59 | v1, v2 | |
| ep11 | Robbed Music | v1, v2 | Also holds `helpers_e.py`, used by later episodes |
| ep12 | When the Barista Still Gets Your Name Wrong | v1–v5 | Final = `build16.py`, `face16.py`, `cams16.py`, `timing16.py`, `audio16.py`, `assemble16.py`, `render16.sh`, `beats16.json`. Final cut 25.2 s |
| ep13 | When You Watch Anime With Subtitles | v1 | No dialogue from Doug; Japanese anime audio (jm_kumo, jf_alpha) with English subtitles. `anime.py` → `vo13.py` → `build.py` → `render.sh` → `audio.py` → `assemble.py` |
| ep14 | When You Accidentally Open the Front Camera | v1 | No dialogue. The phone screen is a real render from the phone's front camera on the same Doug model (`build.py SEL`); blanket is a baked cloth sim (`build.py SIM` → `blanket.pc2`). `build.py QA` → `selfie.sh` → `render.sh` → `audio.py` → `assemble.py`. 15.8 s |
| ep15 | When Someone Is Lying Straight to Your Face | v1–v2 | Doug + Green (Ricky model, no mask/headphones). `vo.py` → `timing.py` → `build.py QA` → `render.sh` → `overlays.py` → `audio.py` → `assemble.py`. Cake box hidden behind Green's hip, falling crumb in shot F. 9 shots, 19.0 s (v1), 20.2 s (v2: gaze-led head moves, medium-shot crumb fall, slow-blink ending) |

Add a row here every time a short or revision is finished.

## Sticky Animation

Code for each sticky short is in `channels/sticky/episodes/<id>/` (the first four, made by hand before the channel joined the studio, are in `channels/sticky/examples/`).

| Folder | Short | Versions | Notes |
|---|---|---|---|
| examples/virginia-hall | A Spy With a Prosthetic Leg Became One of the Nazis' Most Wanted Enemies | v1 | 41 shots, 105.8 s |
| examples/kara-robinson | A Kidnapped Teenager Memorized Her Captor's Apartment… Then Escaped | v1 | 40 shots, 91.2 s |
| examples/james-howells-bitcoin | The Man Who Accidentally Threw Away $800 Million in Bitcoin | v1 | 34 shots, 91.0 s |
| examples/coughing-major | The Man Who Cheated His Way to a Million With a Cough | v1 | 33 shots, 84.2 s |
| episodes/his-climbing-partner-cut-the-rope-but-he-survive | His Climbing Partner Cut the Rope… But He Survived — Joe Simpson | v1, v2 | 38 shots, 76.8 s. v2: re-timed to the voice after the new alignment (SYNC OK); `timeline.py` tidy now moves words whisper stretches across a pause. Adds climbing assets to `lib.py` (helmets, peak, rope, ice walls, crevasse, tent, x-ray bone, Peru map, moraine, crawler) |
