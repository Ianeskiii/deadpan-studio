"""Episode scenes for a sticky short. Run from the episode folder; render.py and sticky.py import this file.

Replace this starter with 30-40 hand-built shots synced to the narration (see PLAYBOOK.md and examples/).
Timing helpers: lt0(i) = start of narration line i, wt(i, 'word', n=0) = start of a word in line i, TL['total'] = length.
"""
from core import *
from lib import _arm

ACCENT = C('#e8b84a')

def shot_hook(cv, T, frozen=False):
    # The hook must draw a clean frame when frozen=True (render.py blends the last 0.6 s into it, so the video loops).
    t = 0 if frozen else T
    night(cv, t)
    character(cv, 'kara', 540, 1700, 120, t=t, expr='worried', look=(math.sin(t * 2) * 0.6, -0.2))
    if frozen: return
    tag(cv, 'HOOK', 540, 320, RED, 64, k=pop(T, lt0(0) + 0.4))

def shot_story(cv, T):
    paper_bg(cv, C('#e8e2d4'))
    character(cv, 'kara', 360, 1720, 110, t=T, expr='smile', look=(0.6, 0))
    tag(cv, 'STORY', 540, 320, ACCENT, 60, INK, k=pop(T, lt0(1) if len(LINES) > 1 else 1.0))

def shot_back(cv, T):
    night(cv, T)
    character(cv, 'kara', 540, 1700, 120, t=T, expr='worried', look=(0, -0.2))

# Per-act colour grade: (start, tint, strength). End on the same tint as the start so the loop is seamless.
ACTS = [(0, C('#2a2a5a'), 0.10), (TL['total'] * 0.5, C('#8a6a2a'), 0.08), (TL['total'] - 2.0, C('#2a2a5a'), 0.10)]
def overlay(cv, T): grade(cv, T, ACTS)

def scenes():
    """[(start, shot_fn, (camA, camB), transition)], camera = (zoom, cx, cy). The hook's camA must be (1.0, 540, 960).
    Transitions: 'cut', 'fade', 'whip', 'zoom', 'wipe', 'flash' — mix them, don't repeat one back to back."""
    end = TL['total']
    Z = (1.0, 540, 960)
    def z(a, cx=540, cy=960): return (a, cx, cy)
    L = [
        (0.0, shot_hook, (Z, z(1.1, 540, 1100)), 'cut'),
        (end * 0.4, shot_story, (Z, z(1.08)), 'whip'),
        (end * 0.8, shot_back, (Z, Z), 'fade'),
    ]
    return [(s0, (L[i + 1][0] if i + 1 < len(L) else end), fn, cam, tr) for i, (s0, fn, cam, tr) in enumerate(L)]
