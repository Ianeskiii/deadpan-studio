"""Episode sound: music bed under the voice, transition whooshes and story-beat effects. Run from the episode folder."""
import os, sys
sys.path[:0] = [os.getcwd(), os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')]
from sfx import *

begin()
music_bed(prog=MINOR, bpm=100, calm=[], bright=[])   # pass (t0, t1) ranges for lighter / heroic sections
transition_sfx()
thud(lt0(0) + 0.4, 0.4)                               # story beats, e.g. thud(wt(3, 'guilty') - 0.05, 0.5)
finish()
