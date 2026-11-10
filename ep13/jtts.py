import os, sys, numpy as np
os.environ.setdefault('OPEN_JTALK_DICT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'jp_dl', 'dic', 'open_jtalk_dic_utf_8-1.11'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
from kokoro_onnx import Kokoro
from misaki import ja
_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts')
K = Kokoro(os.path.join(_root, 'kokoro-q8.onnx'), os.path.join(_root, 'voices_jp.bin'))
G = ja.JAG2P()
def jp(text, voice, speed=1.0):
    ps = G(text)[0] if isinstance(G(text), tuple) else G(text)
    a, sr = K.create(ps, voice=voice, speed=speed, is_phonemes=True)
    nz = np.where(np.abs(a) > 0.01)[0]
    return a[max(0, nz[0] - 150): nz[-1] + 350], ps
