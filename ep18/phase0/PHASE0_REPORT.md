# EP18: POV: Commuting in PH, Phase 0 report

Status: **Phase 0 complete. Waiting for approval before Phase 1 (character modeling).** No modeling, animation or rendering has been done.
Prepared 2026-11-12 from brief V9.

---

## 1. Asset inventory

Every asset was copied under its exact brief filename into `ep18/assets/`. The originals in uploads are untouched.

| Brief filename | Resolved absolute path | Size | MD5 | Status |
|---|---|---|---|---|
| `jeolee.mp4` | /home/claude/deadpan-studio/ep18/assets/jeolee.mp4 | 1080×1920, 30 fps, 19.37 s | 3e851ec7… | OK |
| `TubeTown_Barista_Name_v5.mp4` | /home/claude/deadpan-studio/ep18/assets/TubeTown_Barista_Name_v5.mp4 | 1080×1920, 30 fps, 25.23 s | 96313705… | OK |
| `TubeTown_Front_Camera_v3(1).mp4` | /home/claude/deadpan-studio/ep18/assets/TubeTown_Front_Camera_v3.mp4 | 1080×1920, 30 fps, 15.80 s | d8f19386… | OK (uploaded without "(1)"; same episode, ep14 v3) |
| `passenger_reference_image.png` | /home/claude/deadpan-studio/ep18/assets/passenger_reference_image.png | 1881×836 PNG, 2.6 MB | e5c92a21… | Readable. **See §5: limitation** |
| `driver_shaman_dialogue.mp3` | /home/claude/deadpan-studio/ep18/assets/driver_shaman_dialogue.mp3 | 33,480 B | 4af87b6b… | OK |
| `passenger_voice_1.mp3` | /home/claude/deadpan-studio/ep18/assets/passenger_voice_1.mp3 | 42,014 B | ed6c0a8b… | OK |
| `passenger_voice_2.mp3` | /home/claude/deadpan-studio/ep18/assets/passenger_voice_2.mp3 | 49,537 B | 90090e4e… | OK, one note |
| `passenger_voice_3.mp3` | /home/claude/deadpan-studio/ep18/assets/passenger_voice_3.mp3 | 37,834 B | 49a1073d… | OK |

---

## 2. Audio validation report

All four files decode without errors. All are MP3, 44.1 kHz, mono, 128 kb/s. They are original recordings and will be used as delivered: no TTS, no pitch or speed change, no trimming of speech.
Transcription used faster-whisper small (Tagalog), run once with a hint prompt and once without, so the result isn't just repeating the prompt. Speech windows come from an RMS envelope at −40 dBFS.

| File | Character | Duration | Frames @30 | Speech window | Peak / mean | Transcript (no hint) | Transcript (hinted) | Verdict |
|---|---|---|---|---|---|---|---|---|
| `driver_shaman_dialogue.mp3` | Jeepney driver | 2.090 s | 63 | 0.08–1.86 s. Gap 0.93–1.17 s between the two phrases | −4.4 / −21.1 dB | "Maluwag pagyan, siya manyan" | "Maluwag pa 'yan! Shaman 'yan!" | **PASS.** Matches the script. The last syllable ends at 1.86 s (file frame 56), so the flash can start no earlier than file frame 57. |
| `passenger_voice_1.mp3` | Left neighbor, blue shirt and tie | 1.567 s | 47 | 0.12–1.55 s | −1.6 / −18.9 dB | "Dito pa talaga upo" | "Dito pa talaga umupo." | **PASS.** Peak at −1.6 dB is hot but doesn't clip. |
| `passenger_voice_2.mp3` | Older man with glasses | 2.038 s | 61 | 0.07–0.95 s, then 1.08 s of silence | −3.8 / −20.6 dB | "Ano ba yan siya?" | "Ano ba 'yan siya?" | **PASS with note.** Both passes hear something extra after "'yan" (0.6–0.95 s). It's probably the drawn-out "…" ending, but please confirm by ear that there isn't an extra word. |
| `passenger_voice_3.mp3` | Phone rider | 1.306 s | 39 | 0.07–1.25 s | −3.4 / −20.2 dB | "sikip sikip nga" | "Sikip-sikip na nga." | **PASS.** The short "na" is quick and present in the waveform. |

All four lines are shorter than their 3-second windows, so nothing needs stretching and there's room for reactions between lines without any overlap.

### Draft cue windows (to be locked in Phase 3/4)

| # | File | Window in brief | Speech length | Planned placement |
|---|---|---|---|---|
| 1 | driver_shaman_dialogue.mp3 | 5.0–7.5 s | 1.78 s | Start ≈ 5.3 s (f159). Speech ends ≈ 7.16 s (f215). Flash ≥ f216 |
| 2 | passenger_voice_1.mp3 | 20–23 s | 1.43 s | Start ≈ 20.5 s |
| 3 | passenger_voice_2.mp3 | 23–26 s | 0.88 s | Start ≈ 23.5 s, after line 2 plus a reaction beat |
| 4 | passenger_voice_3.mp3 | 26–29 s | 1.18 s | Start ≈ 26.5 s |

Exact frame ranges will be written to the cue sheet in Phase 5.

---

## 3. Reference contact sheet

`ep18/phase0/reference_contact_sheet.jpg`: four frames each from jeolee (row 1), Barista v5 (row 2) and Front Camera v3 (row 3).

---

## 4. Tube Town visual style guide (from the three videos)

**Bodies**
- One continuous capsule ("tube") per character: torso and head are the same form, with no neck. The top is a hemisphere.
- Height-to-width is about 2.6:1 seated.
- Arms and legs are thin rubber-hose cylinders with sphere joints and rounded mitten hands. Feet are short rounded capsules.
- Every surface is smooth and subdivided, with no visible facets or seams.

**Materials**
- Soft, slightly glossy plastic/clay look: low roughness on skin, matte cloth on clothing and props.
- Body colors are saturated but warm: Doug yellow-orange, barista lavender, jeolee peach and pink.
- Clothing is simple sleeves or wraps: aprons, collars, a ring at the neck.

**Faces**
- Eyes are two large, glossy white spheres set close together near the top of the tube, with brown or blue irises, a single white specular dot, and lids that are part of the body color.
- Doug has heavy upper lids and no brows. Other characters have floating bar brows (dark, rounded rectangles).
- The mouth is a small dark-red pill or bean. It opens to a rounded triangle or oval for speech. There are no teeth or lips.
- Optional blush circles on the cheeks. There's no nose, or at most a tiny bump.

**Hair**
- Sculpted clay masses: thick bob or fringe shapes with no strand detail (see the jeolee girl).
- It sits on the capsule like a helmet, with simple pointed or rounded clumps.

**Lighting**
- Interiors use a warm key with a soft cool fill. Front Camera adds a blue-hour rim.
- The renderer is Cycles: soft shadows, a gentle background falloff, and shallow depth of field on close-ups.
- Exposure is kept down so the yellow body never blows out.

**Camera**
- Vertical framing alternating wide, medium and big close-up. Close-ups fill the frame with the eyes, framed from the top of the hat or hair down to the mouth.
- Mostly locked-off shots with slow push-ins. Comedy cuts are hard cuts.

**Acting**
- Stillness, eye darts and slow blinks. Eyes move first, then the head.
- Doug never overreacts. His biggest reaction is lids snapping open.

**Captions**
- Bold white sans-serif with a black outline, top-center, two lines at most, inside the Shorts safe zone.
- Dialogue subtitles sit lower-center (jeolee and Barista do this).

**Doug, the source of truth**
- Yellow-orange tube, **coral/orange bucket hat** (not a cap), half-lidded deadpan eyes, no brows, small bean mouth.
- The model is `tubetown/lib.py` exactly as it is. No redesign.

---

## 5. Transformation reference image: limitation

`passenger_reference_image.png` shows Yoh, Anna, Manta and Amidamaru from **Shaman King**, redrawn in this style. They are protected characters, and changing the art style doesn't change that, so I won't model them or any close variant of them. That covers Characters A, B, C and the guardian spirit as written in brief §8–§11.

**Everything else in the brief stays as written:** the "Shaman 'yan!" pun, the flash, the four close-ups with their timing and camera moves, the spirit floating above the aisle, the face slap and the return to normal.

### Proposed original lineup (needs your approval)

These keep the folk-shaman joke and give it a Filipino flavor:

| Slot | Working name | Look (Tube Town tube) | Close-up acting (brief §8–§11 timing) |
|---|---|---|---|
| A | **The Albularyo Kid** | Tan tube. Woven buri sun-hat with a frayed brim. A string of carved wooden anting-anting charms on a cord. Rolled-sleeve green barong-style shirt. Rattan staff with a glowing amber charm resting on his knee. | Eyes slide to Doug, head follows, slow knowing smirk (0.6 s, push-in) |
| B | **The Babaylan** | Deep-brown tube. Tall black curly bun held by a gold hairpin. Purple-and-gold woven tapis wrap with a shell bead necklace. Bangles stacked on one arm. | Cold stare, brows lower, chin lifts slightly (0.6 s, fast cut or whip-pan) |
| C | **The Apprentice** | Small, round, pale-green tube. Oversized yellow raincoat with the hood up. Hugs a glass jar of glowing fireflies (alitaptap) to his chest. | Eyes go wide, hugs the jar tighter, shoulders rise, the fireflies flicker (0.6 s, push-in) |
| Spirit | **Lolo Ninuno** (ancestor guardian) | Huge translucent **amber-gold** spectral tube floating above the aisle. Ghostly salakot hat. Long wispy smoke-like beard and brows that drift. Transparent barong with an embroidered collar. Glowing narrow eyes, soft gold bloom, lower body fading into smoke. | Eyes shift to Doug, face follows, brows lower, beard drifts. The strongest zoom (0.7 s) |

The remaining transformed seats (no duplicates, no placeholders) would be filled by: a tikbalang-mask commuter, a mananambal with a cloth pouch of herbs, a stern lola holding a glowing rosary-like string of beads, a sun-faced diwata with leaf hair, and a pair of tiny duwende twins sharing one seat.

---

## 6. Ordinary passengers and seat map (draft for Phase 2)

- **Driver:** front left, white sando, face towel over one shoulder, visible in the rear-view mirror. Speaks line 1.
- **Passenger 1:** right bench, directly left of Doug's gap, facing the camera. Blue shirt and tie, office ID lanyard. Speaks line 2.
- **Passenger 2:** right bench, directly right of the gap. Older man, glasses, grey hair. Speaks line 3.
- **Passenger 3:** left bench, opposite the gap, eyes on a phone. Speaks line 4.
- **Extras:** about 8 more across both benches (student, vendor with bilao, nurse, etc.), so every seat is full except Doug's ~11 cm gap.

Each transformed character takes the seat of one ordinary passenger, so seats stay full through the transformation.

---

## 7. Questions before Phase 1

1. **Lineup:** approve the original lineup in §5, or send changes.
2. **Doug's look:** keep his established coral/orange **bucket hat**? (The brief says "orange cap". The style references and the rig have the bucket hat.)
3. **"Hayst…":** record it yourself as `doug_hayst.mp3`, or use a temporary sigh labeled TEMP?
4. **Subtitles:** the channel targets a US audience but the dialogue is Tagalog. Burn in subtitles under the dialogue: Tagalog, English, or none?
5. **Passenger 2:** listen and confirm there's no extra word after "Ano ba 'yan" (see §2).

## 8. Production notes

- No `shorts/<id>/short.json` has been created yet. Committing one would start the GitHub Actions queue and skip your approval gates. EP18 lives only in `ep18/` until you approve the final render.
- `jeolee.mp4` is used only for style (materials, lighting, captions). None of its characters will be copied.
