# ---- state interpolation + hip layers --------------------------------------
def conc_arms(rig, a):
    out = {}
    for side, (hand, el) in a.items():
        sh = rig.shoulder(side); hand = Vector(hand)
        if isinstance(el, tuple) and len(el) == 2 and el[0] == 'auto':
            elbow = rig.joint(sh, hand, rig.arm_len, el[1])
        else:
            elbow = Vector(el)
        out[side] = (hand, elbow)
    return out
def conc_legs(spec): return {k: (Vector(f_), Vector(b_)) for k, (f_, b_) in spec.items()}
def ST(rig, f, up=(0, 0, 0), rot=(0, 0, 0), sq=1.0, arms=None, legs='stand'):
    return dict(f=f, up=Vector(up), rot=Vector(rot), sq=sq, arms=conc_arms(rig, arms),
                legs=conc_legs(LEGS[legs]() if isinstance(legs, str) else legs))
def smooth(t): return t * t * (3 - 2 * t)
def interp(states, f):
    if f <= states[0]['f']: return states[0]
    if f >= states[-1]['f']: return states[-1]
    for a_, b_ in zip(states, states[1:]):
        if a_['f'] <= f <= b_['f']:
            t = smooth((f - a_['f']) / max(1, b_['f'] - a_['f'])); L = lambda x, y: x.lerp(y, t)
            return dict(up=L(a_['up'], b_['up']), rot=L(a_['rot'], b_['rot']), sq=a_['sq'] + (b_['sq'] - a_['sq']) * t,
                        arms={k: (L(a_['arms'][k][0], b_['arms'][k][0]), L(a_['arms'][k][1], b_['arms'][k][1])) for k in a_['arms']},
                        legs={k: (L(a_['legs'][k][0], b_['legs'][k][0]), L(a_['legs'][k][1], b_['legs'][k][1])) for k in a_['legs']})
def run(rig, f0, f1, states, layer=None):
    for f in range(f0, f1 + 1):
        s_ = interp(states, f)
        dup, drot, bd = layer(f) if layer else (V(0, 0, 0), V(0, 0, 0), (0, 0))
        rig.pose(f, up=tuple(s_['up'] + dup), rot=tuple(s_['rot'] + drot), sq=s_['sq'], arms=s_['arms'], legs=s_['legs'], bend=bd)
def kembot(rig, f0, amp=30, beat=BEAT, twist=8, shift=0.04, env=lambda f: 1.0):
    """side-to-side hip sway, snapping to each beat"""
    def L(f):
        ph = math.pi * (f - f0) / beat; v = math.copysign(abs(math.sin(ph)) ** 0.55, math.sin(ph)) * env(f)
        return V(-shift * v * rig.SIDE, 0, -0.025 * abs(v)), V(0, -3 * v, twist * v), (0, amp * v)
    return L
def giling(rig, f0, period=2 * BEAT, amp=30, shift=0.045, env=lambda f: 1.0):
    """circular hip roll"""
    def L(f):
        a_ = 2 * math.pi * (f - f0) / period; e = env(f)
        bx, by = amp * math.sin(a_) * e, amp * math.cos(a_) * e
        return V(-shift * math.cos(a_) * e * rig.SIDE, shift * math.sin(a_) * e * rig.FWD, -0.02 * e), V(5 * math.sin(a_) * e, -5 * math.cos(a_) * e, 6 * math.sin(a_) * e), (bx, by)
    return L
def thrust(rig, f0, amp=26, beat=BEAT):
    """hip pump forward on every beat"""
    def L(f):
        v = max(0.0, math.cos(2 * math.pi * (f - f0) / beat)) ** 3
        return V(0, -0.03 * v, -0.03 * v), V(-4 * v, 0, 0), (rig.FWD * amp * v, 0)
    return L

