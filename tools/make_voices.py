"""Build tts/voices.bin (English) and tts/voices_jp.bin (English + Japanese) from the npm voice files."""
import glob, os, sys, numpy as np
root = sys.argv[1]  # .cache folder made by setup.sh
def load(folder):
    return {os.path.basename(p)[:-4]: np.fromfile(p, dtype=np.float32).reshape(-1, 1, 256)
            for p in sorted(glob.glob(os.path.join(folder, '*.bin')))}
en = load(os.path.join(root, 'kokoro-local-runtime', 'package', 'voices'))
jp = {k: v for k, v in load(os.path.join(root, 'kokoro-js', 'package', 'voices')).items() if k[0] == 'j'}
with open('tts/voices.bin', 'wb') as f: np.savez(f, **en)
with open('tts/voices_jp.bin', 'wb') as f: np.savez(f, **en, **jp)
print(len(en), 'English voices,', len(jp), 'Japanese voices')
