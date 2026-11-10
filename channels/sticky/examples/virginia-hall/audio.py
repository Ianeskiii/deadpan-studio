# Example audio.py as delivered (virginia-hall); older self-contained style. New episodes use sfx.py (see template/audio.py).
import json, numpy as np, soundfile as sf, os, sys
sys.path[:0]=[os.getcwd(), os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')]
from scenes import lt0, wt, TL, scenes, LINES
SR=44100; N=int(TL['total']*SR)+SR; mus=np.zeros(N); sfx=np.zeros(N)
rng=np.random.default_rng(1)
def add(buf,t,x):
    i=max(0,int(t*SR)); j=min(len(buf),i+len(x)); buf[i:j]+=x[:j-i]
mid=lambda m:440*2**((m-69)/12)
def noise(d): return rng.standard_normal(int(d*SR))
def note(f,d,amp=0.2,dec=6):
    t=np.arange(int(d*SR))/SR
    return amp*np.exp(-dec*t)*(np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)*np.exp(-12*t)+0.12*np.sin(2*np.pi*4*f*t)*np.exp(-20*t))
def pad(f,d,amp=0.05):
    t=np.arange(int(d*SR))/SR; env=np.minimum(1,t/0.6)*np.minimum(1,(d-t)/0.6)
    return amp*env*(np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*f*1.003*t)+0.3*np.sin(2*np.pi*f*2*t))
bpm=104; beat=60/bpm; total=TL['total']
# spy-noir bed: minor ostinato (A minor / F / D minor / E)
prog=[(45,[57,60,64]),(41,[57,60,65]),(38,[57,62,65]),(40,[56,59,64])]
hero0=lt0(15)-0.2; hero1=lt0(16)-0.1
t=0; k=0
while t<total:
    bar=(k//8)%4; root,ch=prog[bar]
    if hero0<=t<hero1:
        if k%8==0:
            for m in (48,55,60,64,67): add(mus,t,pad(mid(m),beat*4.2,0.035))
        if k%2==0: add(mus,t,note(mid([72,76,79,84][(k//2)%4]),0.5,0.04,5))
    else:
        if k%2==0: add(mus,t,note(mid(root),0.45,0.2,6))
        if k%8==0:
            for m in ch: add(mus,t,pad(mid(m),beat*4.1,0.02))
        if k%2==1: add(mus,t,note(mid(ch[(k//2)%3]+12),0.25,0.035,12))
        # brushed hat
        x=noise(0.04); x=x-np.convolve(x,np.ones(4)/4,'same'); add(mus,t,0.03*x*np.exp(-np.arange(len(x))/SR*80))
        if k%4==0: tt=np.arange(int(0.25*SR))/SR; add(mus,t,0.18*np.sin(2*np.pi*55*tt)*np.exp(-18*tt))
    t+=beat/2; k+=1
def whoosh(t,d=0.3,a=0.06):
    x=noise(d); env=np.sin(np.linspace(0,np.pi,len(x)))**2
    x=np.convolve(x,np.ones(30)/30,'same'); add(sfx,t-d/2,a*x*env*3)
def thud(t,a=0.5):
    tt=np.arange(int(0.35*SR))/SR; add(sfx,t,a*np.sin(2*np.pi*70*tt)*np.exp(-14*tt)+0.15*np.convolve(noise(0.35),np.ones(60)/60,'same')*np.exp(-20*tt))
def tick(t,a=0.15):
    tt=np.arange(int(0.03*SR))/SR; add(sfx,t,a*np.sin(2*np.pi*2400*tt)*np.exp(-150*tt))
def type_(t,a=0.12):
    x=noise(0.03)*np.exp(-np.arange(int(0.03*SR))/SR*200); add(sfx,t,a*x)
def beep(t,f=800,d=0.08,a=0.07):
    tt=np.arange(int(d*SR))/SR; env=np.minimum(1,np.minimum(tt,d-tt)/0.005); add(sfx,t,a*env*np.sin(2*np.pi*f*tt))
def step(t,a=0.12,low=False):
    tt=np.arange(int(0.09*SR))/SR; x=np.convolve(noise(0.09),np.ones(25)/25,'same')*4
    add(sfx,t,a*(x*np.exp(-40*tt)+0.6*np.sin(2*np.pi*(90 if low else 130)*tt)*np.exp(-30*tt)))
def limp_steps(t0,t1,a=0.1,per=0.62):
    t=t0; i=0
    while t<t1: step(t,a,low=i%2==0); t+= per*(0.38 if i%2==0 else 0.62); i+=1
def wind(t0,d,a=0.05):
    x=np.convolve(noise(d),np.ones(120)/120,'same')*9; tt=np.arange(len(x))/SR
    env=np.minimum(1,np.minimum(tt,d-tt)/0.4); add(sfx,t0,a*x*env*(0.6+0.4*np.sin(2*np.pi*0.4*tt)))
def boom(t,a=0.7,d=1.6):
    tt=np.arange(int(d*SR))/SR; x=np.convolve(noise(d),np.ones(80)/80,'same')*6
    add(sfx,t,a*(x*np.exp(-3*tt)+np.sin(2*np.pi*45*tt)*np.exp(-4*tt)))
def bang(t,a=0.6):
    tt=np.arange(int(0.5*SR))/SR; add(sfx,t,a*(noise(0.5)*np.exp(-25*tt)*0.6+np.sin(2*np.pi*80*tt)*np.exp(-12*tt)))
def knock(t,a=0.35):
    for i in range(3):
        tt=np.arange(int(0.08*SR))/SR; add(sfx,t+i*0.16,a*np.sin(2*np.pi*180*tt)*np.exp(-50*tt))
def chime(t,a=0.1):
    for i,m in enumerate([79,84,88,91]): add(sfx,t+i*0.07,note(mid(m),1.0,a,4))
def waves_(t0,d,a=0.03):
    x=np.convolve(noise(d),np.ones(200)/200,'same')*12; tt=np.arange(len(x))/SR; add(sfx,t0,a*x*(0.5+0.5*np.sin(2*np.pi*0.25*tt)))
SC=scenes()
for s_ in SC[1:]:
    tr=s_[4]
    if tr in ('whip','zoom','wipe'): whoosh(s_[0]+0.12,0.32,0.07)
    elif tr=='flash': thud(s_[0],0.25)
# hook
limp_steps(0.0,4.0,0.09); whoosh(wt(0,'dangerous')-0.1,0.3,0.05)
thud(wt(0,'wooden')-0.1,0.45)
chime(wt(1,'virginia')-0.15,0.06)
thud(wt(2,'1933')-0.1,0.3)
bang(wt(2,'accident')-0.1)
thud(wt(4,'rejected')-0.05,0.6)
boom(wt(4,'world')-0.1,0.35,2.0)
whoosh(lt0(5)-0.1,0.4,0.07)
for i in range(16): beep(44.0+i*0.11*(1 if i%3 else 2),900,0.05 if i%3 else 0.13,0.05)
limp_steps(50.0,52.0,0.1)
for i in range(40): type_(52.6+i*0.065,0.08)
thud(wt(8,'find')-0.05,0.6); thud(wt(8,'destroy')-0.05,0.5)
knock(60.7)
limp_steps(61.4,62.5,0.12,0.5)
wind(62.6,5.4,0.06)
for i in range(22): beep(wt(10,'cuthbert')-0.1+i*0.08,900,0.045,0.04)
for i in range(30): type_(wt(11,'replied')+i*0.07,0.08)
thud(wt(11,'eliminate')-0.05,0.5)
waves_(79.3,2.9,0.035)
whoosh(wt(13,'grey')-0.15,0.5,0.08)
limp_steps(85.6,88.8,0.07,0.9)
boom(wt(14,'bridges')-0.15,0.6)
chime(wt(15,'distinguished')-0.15,0.09)
thud(102.3,0.3)
v,vsr=sf.read('voice.wav')
if v.ndim>1: v=v.mean(1)
vi=np.interp(np.arange(int(len(v)*SR/vsr))/SR, np.arange(len(v))/vsr, v)
voice=np.zeros(N); voice[:min(N,len(vi))]=vi[:N]
env=np.abs(voice); win=int(0.15*SR); env=np.convolve(env,np.ones(win)/win,'same'); duck=1-0.45*np.clip(env/0.03,0,1)
mix=voice*1.0+mus*0.5*duck+sfx*0.8
mix=mix[:int(total*SR)]
fade=int(0.03*SR); mix[-fade:]*=np.linspace(1,0,fade)
mix/=max(1,np.abs(mix).max()/0.95)
sf.write('mix.wav',mix,SR)
print('ok')
