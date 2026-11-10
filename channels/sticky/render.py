"""Render a sticky episode. Run from the episode folder (channels/sticky/episodes/<id>):
  python3 ../../render.py still 1.5 12.0 ...     # full-size stills -> stills/still_<t>.jpg
  python3 ../../render.py video 0 4 8 ...        # scene files -> sc00.mp4, sc04.mp4, ...
sticky.py wraps these (stills sheets, parallel render, audio, concat, mux, loop check).
"""
import os, sys, subprocess, numpy as np, math
sys.path.insert(0, os.getcwd()); sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))
from scenes import *
import scenes as _scenes_mod
FPS = 30
SC = scenes()
WORDS = [w for l in LINES for w in l['words']]
CAPF = skia.Font(skia.Typeface('Poppins', skia.FontStyle.Bold()), 82)

def apply_cam(cv, cam):
    z, cx, cy = cam
    hw, hh = W / (2 * z), H / (2 * z)
    cx = clamp(cx, hw, W - hw); cy = clamp(cy, hh, H - hh)
    cv.translate(W / 2, H / 2); cv.scale(z, z); cv.translate(-cx, -cy)

def draw_scene(cv, i, T):
    s0, s1, fn, (ca, cb) = SC[i][:4]
    f = (T - s0) / max(0.01, s1 - s0)
    z, cx, cy = cam_lerp(ca, cb, clamp(f, 0, 1.15))
    # subtle handheld drift (fades to zero at both ends so the loop stays seamless)
    amp = clamp(T / 1.2) * clamp((TL['total'] - T) / 1.2)
    z *= 1.0 + amp * (0.025 + 0.004 * math.sin(T * 1.1))
    cx += amp * (math.sin(T * 0.9 + i * 1.3) * 9 + math.sin(T * 2.3) * 3)
    cy += amp * (math.sin(T * 0.7 + i * 2) * 8)
    cv.save(); apply_cam(cv, (z, cx, cy)); fn(cv, T); cv.restore()

def caption(cv, T):
    cur = None
    for w in WORDS:
        if w['t0'] - 0.03 <= T < max(w['t1'], w['t0'] + 0.12): cur = w
    if not cur: return
    k = back(clamp((T - cur['t0'] + 0.03) / 0.12)); s = 0.78 + 0.22 * k
    txt = cur['w']
    wdt = CAPF.measureText(txt)
    cy = 990 if False else 1395
    cv.save(); cv.translate(540, cy); cv.scale(s, s)
    cv.drawString(txt, -wdt / 2, 0, CAPF, fillp(skia.Color(0, 0, 0, 90), blur=8))
    cv.drawString(txt, -wdt / 2, 0, CAPF, strokep(INK, 16))
    cv.drawString(txt, -wdt / 2, 0, CAPF, fillp(C('#ffffff')))
    cv.restore()

XF = 0.22
TRANS_LEN = {'fade': 0.22, 'whip': 0.3, 'zoom': 0.32, 'flash': 0.28, 'wipe': 0.32, 'cut': 0.0}
SC_CUR = [0]
def frame(i, T, surf, tmp):
    SC_CUR[0] = i
    cv = surf.getCanvas(); cv.clear(skia.ColorBLACK)
    tr = SC[i][4] if len(SC[i]) > 4 else 'fade'
    L = TRANS_LEN.get(tr, 0.22)
    s0 = SC[i][0]
    if i > 0 and T - s0 < L and tr != 'cut':
        k = ease(clamp((T - s0) / L))
        tc = tmp.getCanvas(); tc.clear(skia.ColorBLACK); draw_scene(tc, i - 1, T)
        prev = tmp.makeImageSnapshot()
        if tr == 'whip':
            cur = skia.Surface(W, H); cc = cur.getCanvas(); cc.clear(skia.ColorBLACK); draw_scene(cc, i, T)
            bl = 40 * math.sin(k * math.pi)
            p = skia.Paint(); p.setImageFilter(skia.ImageFilters.Blur(bl + 0.01, 0.01))
            cv.drawImage(prev, -k * W, 0, skia.SamplingOptions(), p)
            cv.drawImage(cur.makeImageSnapshot(), (1 - k) * W, 0, skia.SamplingOptions(), p)
        elif tr == 'zoom':
            draw_scene(cv, i, T)
            cv.save(); cv.translate(W / 2, H / 2); cv.scale(1 + k * 0.9, 1 + k * 0.9); cv.translate(-W / 2, -H / 2)
            p = skia.Paint(); p.setAlphaf(1 - k); p.setImageFilter(skia.ImageFilters.Blur(k * 14 + 0.01, k * 14 + 0.01))
            cv.drawImage(prev, 0, 0, skia.SamplingOptions(), p); cv.restore()
        elif tr == 'wipe':
            draw_scene(cv, i, T)
            cv.save(); pth = skia.Path(); x = k * (W + 700) - 350
            pth.moveTo(x + 350, -10); pth.lineTo(W + 10, -10); pth.lineTo(W + 10, H + 10); pth.lineTo(x - 350, H + 10); pth.close()
            cv.clipPath(pth, doAntiAlias=True); cv.drawImage(prev, 0, 0); cv.restore()
            cv.drawLine(x + 350, -10, x - 350, H + 10, strokep(C('#f4efe2'), 10, alpha=0.8))
        elif tr == 'flash':
            if k < 0.35: cv.drawImage(prev, 0, 0)
            else: draw_scene(cv, i, T)
            a_ = 1 - abs(k - 0.35) / 0.65
            cv.drawRect(skia.Rect(0, 0, W, H), fillp(C('#fff8ec'), alpha=max(0, a_) * 0.95))
        else:
            draw_scene(cv, i, T)
            p = skia.Paint(); p.setAlphaf(1 - k)
            cv.drawImage(prev, 0, 0, skia.SamplingOptions(), p)
    else:
        draw_scene(cv, i, T)
    end = TL['total']
    b = clamp((T - (end - 0.62)) / 0.6)
    if b > 0:  # loop: blend into the frozen first frame of the hook (SC[0] must accept frozen=True)
        hs = skia.Surface(W, H); hc = hs.getCanvas(); hc.clear(skia.ColorBLACK)
        hc.save(); apply_cam(hc, SC[0][3][0]); SC[0][2](hc, 0.0, frozen=True); hc.restore()
        p = skia.Paint(); p.setAlphaf(b)
        cv.drawImage(hs.makeImageSnapshot(), 0, 0, skia.SamplingOptions(), p)
    if hasattr(_scenes_mod, 'overlay'): _scenes_mod.overlay(cv, T)
    caption(cv, T)
    return surf

def render_scene(i, out):
    s0, s1 = SC[i][0], SC[i][1]
    n0 = round(s0 * FPS); n1 = round(s1 * FPS)
    surf = skia.Surface(W, H); tmp = skia.Surface(W, H)
    tmpname = out.replace('.mp4', '.part.mp4')
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmpname], stdin=subprocess.PIPE)
    for n in range(n0, n1):
        frame(i, n / FPS, surf, tmp)
        img = surf.makeImageSnapshot()
        p.stdin.write(img.tobytes() if hasattr(img, 'tobytes') else np.array(img).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmpname, out)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for ts in sys.argv[2:]:
            T = float(ts); i = max(k for k, s in enumerate(SC) if s[0] <= T)
            surf = skia.Surface(W, H); frame(i, T, surf, skia.Surface(W, H))
            os.makedirs('stills', exist_ok=True)
            surf.makeImageSnapshot().save(f'stills/still_{ts}.jpg', skia.kJPEG, 85)
    else:
        idx = [int(x) for x in sys.argv[2:]]
        for i in idx: render_scene(i, f'sc{i:02d}.mp4'); print('done', i, flush=True)
