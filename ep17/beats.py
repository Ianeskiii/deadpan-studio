"""ep17 "When you finish work at 4:59 PM" - every beat in frames (30 fps). Imported by build.py, screen.py, audio.py, assemble.py.
Speech placement comes from the takes (vo17.py): m1 speech 0.50-1.07 s into the file, a2 speech 0.44-1.27 s."""
FPS = 30
SH = dict(
    A=(1, 25),        # 0.0-0.8   medium (front-left 3/4): typing, glances up at the clock
    I=(26, 40),       # 0.8-1.3   insert: the screen, 4:59 PM (same framing as S - so S is the payoff)
    B=(41, 110),      # 1.3-3.7   medium (as A): shoulders drop, small smile, headset off, pen up, "Mamba out.", pen drop
    S=(111, 165),     # 3.7-5.5   screen close-up: 4:59:58 -> 4:59:59 PM, BOSS incoming call (ringtone)
    C=(166, 255),     # 5.5-8.5   medium close-up: frozen, smile drains, screen -> pen -> screen, slowly retrieves the pen
    D=(256, 360),     # 8.5-12.0  medium (other side): pen back in its place, headset back on, shoulders sink, UNMAMBA., "...Alright.", hand to mouse, cursor toward Accept
    E=(361, 432),     # 12.0-14.4 tight close-up from the webcam: cursor stops short, eyes come up into the lens, dead stare (1.5 s)
)
N = 442               # 433-442 black (ringtone cut)
BLACK = 433
TYPE = (1, 24); CLOCK_LOOK = (18, 26); RELAX = (40, 50)
HS_OFF = (48, 68)     # hands to the cups 48-55, lift off 55-61, down to the desk 61-66, let go 66-68
PEN_PICK = (68, 79)   # left hand to the pen 68-73, picks it up 73-79 (held up like a mic)
M_F = 64              # "Mamba out." take starts (breath in/out 64-76, speech ~79-96)
PEN_DROP = 97; PEN_LAND = 105
CLK_59 = 115; CALL = 119                     # clock ticks to 4:59:59, call card pops (ring starts)
DRAIN = (166, 192); G_SCREEN = (170, 178); G_PEN = (194, 202); G_BACK = (210, 218)
REACH = (222, 242); PEN_UP = (242, 254)
PEN_BACK = (256, 272); HS_GRAB = (276, 286); HS_ON = (286, 306); HANDS_DOWN = (306, 316); SINK = (312, 326)
UNMAMBA = 316
A_F = 319             # "...Alright." take starts (breath 319-328, speech ~332-357)
MOUSE = (338, 350); CURSOR = (348, 372)      # cursor glides toward Accept and stops just short (frame 372)
LOOK_UP = (374, 386)                          # eyes up into the lens; hold to the end of E
