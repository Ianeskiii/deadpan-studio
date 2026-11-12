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
| ep14 | When You Accidentally Open the Front Camera | v1–v3 | No dialogue. v3: FAHHH (`sfx/fahhh_src.wav`, owner-supplied) at `REVEALS` 73/213/263 - low, too close (`CLOSE`), worst belly cam (`WORST`) - with `STARTLES` head recoils and a 0.55 s dead silence; shots A and F reused unchanged. v2: real seated legs (`KNEE_L`/`FOOT_L`), one raise-to-eye-level and lower comparison (D medium + DP POV, screen keyed to `RAISE`/`LOWER` in beats.json), tap ripple and zoom-open, Barista/Bathroom title type. The phone screen is a real render from the phone's front camera on the same Doug model (`build.py SEL`); blanket is a baked cloth sim (`build.py SIM` → `blanket.pc2`). `build.py QA` → `selfie.sh` → `render.sh` → `audio.py` → `assemble.py`. 15.8 s |
| ep15 | When Someone Is Lying Straight to Your Face | v1–v2 | Doug + Green (Ricky model, no mask/headphones). `vo.py` → `timing.py` → `build.py QA` → `render.sh` → `overlays.py` → `audio.py` → `assemble.py`. Cake box hidden behind Green's hip, falling crumb in shot F. 9 shots, 19.0 s (v1), 20.2 s (v2: gaze-led head moves, medium-shot crumb fall, slow-blink ending) |
| ep16 | When You Finally Have Free Time to Play Games | v1–v2 | v2 (11.5 s): seated from frame 1; Doug's one word "Finally!" (`vo16.py` take c: happy inhale + breathy exhale + am_fenrir, mouth from the take in `MOUTH_O`); caption POV: GAMING IN YOUR 30s (62 px, one line); OTS re-grip/thumb (`REGRIP`/`THUMB`); hard-cut 3 MINUTES LATER card; sleep sequence `HEAVY`→`CLOSE` in one MCU; owner-supplied Vine Boom (`sfx/vine_boom_src.wav`) with its attack on `REVEAL`=205, snoring from `SNORE0`=247. v1 (21.7 s, walk-in, FAHHH) is in git history. `vo16.py` → `build.py QA` → `tv.py` → `render.sh` → `overlays.py` → `audio.py` → `assemble.py`. Original console (NOVA), game menu (LANTERN HOLLOW), TV angled 22° |
| ep17 | When You Finish Work at 4:59 PM (Mamba Out) | v1 | 14.7 s, 7 shots + black: A/B medium (typing, headset off, pen up, "Mamba out.", gravity mic-drop at `PEN_LAND`=105), I clock insert (4:59 PM, same framing as S), S screen close-up 4:59:59 + original "Work Chat" BOSS call card (`screen.py`), C MCU freeze/screen-pen-screen, D headset back on + UNMAMBA. + "...Alright.", E webcam stare (`LID_E`/`GZ_E` env, defaults 12 / −0.3), hard cut at `BLACK`=433. Voices `vo17.py` (am_fenrir + pyworld F0 shaping, takes m1/a2). Original mallet ringtone ducked −9 dB under "Alright". New scene `home-office`. `vo17.py` → `screen.py` → `build.py QA` → `render.sh` → `overlays.py` → `audio.py` → `assemble.py` |
| ep19 | Mama mong mahilig maniwala sa fake news (Tagalog; owner's 5 MP3s; new character Mom; Filipino living room) | v1 | 7 shots, 18.4 s. Built in chat. Caption in the DejaVu house style |
| ep20 | Me While Watching Jeolee Before Going to Sleep | v1 | 10.0 s, one continuous 300-frame shot (every frame rendered, 8 samples, pct 75). Bedroom from ep10 relit for 2 AM; Doug on his side, no hat, rolled back 16° to face the camera. Mouth is a keyed bezier tube that morphs bean → smile → big smile; lids/brows/blanket shape keys (pull, breath, curl, foot) driven per frame from the EMO table; beats in `beats.json` (re-time to the Jeolee audio). Generic iPhone-style phone (titanium frame, triple-lens bump, no logo) with screen light on his face. v1 has a silent track; `assemble.py --audio <file> [--offset s]` muxes the owner's clip unchanged. `overlays.py` → `render.sh` → `assemble.py` |

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
