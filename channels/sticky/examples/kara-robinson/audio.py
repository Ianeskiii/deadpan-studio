# Example audio.py as delivered (kara-robinson); older self-contained style. New episodes use sfx.py (see template/audio.py).
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
bpm=100; beat=60/bpm; total=TL['total']
prog=[(40,[52,55,59]),(36,[52,55,60]),(38,[50,54,57]),(35,[51,54,59])]
calm=(lt0(1)+2.0, lt0(2)); bright=(lt0(16)-0.2, total-0.3)
t=0; k=0
while t<total:
    bar=(k//8)%4; root,ch=prog[bar]
    if calm[0]<=t<calm[1] or bright[0]<=t<bright[1]:
        if k%2==0: add(mus,t,note(mid([64,67,71,76][(k//2)%4]),0.5,0.05,5))
        if k%8==0:
            for m in (48,55,64): add(mus,t,pad(mid(m),beat*4.2,0.03))
    else:
        if k%2==0: add(mus,t,note(mid(root),0.45,0.2,6))
        if k%8==0:
            for m in ch: add(mus,t,pad(mid(m),beat*4.1,0.022))
        if k%4==2: add(mus,t,note(mid(ch[(k//4)%3]+12),0.3,0.035,9))
        x=noise(0.04); x=x-np.convolve(x,np.ones(4)/4,'same'); add(mus,t,0.025*x*np.exp(-np.arange(len(x))/SR*80))
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
def heart(t,a=0.35):
    for d in (0,0.18):
        tt=np.arange(int(0.15*SR))/SR; add(sfx,t+d,a*(1 if d==0 else 0.7)*np.sin(2*np.pi*55*tt)*np.exp(-25*tt))
def clink(t,a=0.15):
    for f in (2200,3300): tt=np.arange(int(0.2*SR))/SR; add(sfx,t,a*np.sin(2*np.pi*f*tt)*np.exp(-30*tt)/2)
def siren(t,d=2.0,a=0.05):
    tt=np.arange(int(d*SR))/SR; f=650+250*np.sin(2*np.pi*1.5*tt); add(sfx,t,a*np.sin(2*np.pi*np.cumsum(f)/SR))
def engine(t0,d,a=0.05):
    tt=np.arange(int(d*SR))/SR; add(sfx,t0,a*np.sin(2*np.pi*(60+20*np.sin(2*np.pi*0.3*tt))*tt)*np.minimum(1,np.minimum(tt,d-tt)/0.3))
def birds(t0,d,a=0.03):
    t=t0
    while t<t0+d:
        tt=np.arange(int(0.12*SR))/SR; add(sfx,t,a*np.sin(2*np.pi*(3000+800*np.sin(2*np.pi*20*tt))*tt)*np.exp(-20*tt)); t+=0.35+0.3*rng.random()
for i in range(3): heart(0.2+i*0.9,0.25)
for i in range(5): tick(wt(0,'trapped')+0.6+i*0.3,0.1)
for i in range(5): tick(lt0(0)+5.4+i*0.28,0.12)
chime(wt(1,'kara')-0.15,0.06)
thud(wt(1,'june')-0.1,0.3)
birds(12.7,2.8)
thud(wt(2,'gun')-0.1,0.6); boom(wt(2,'gun')-0.05,0.25,1.2)
engine(21.2,1.6,0.06); thud(wt(3,'locked')-0.02,0.5)
engine(25.7,1.8,0.04)
for i in range(18): tick(27.6+i*0.13,0.1)
for i in range(4): heart(30.9+i*0.85,0.22)
for i,w in enumerate(('calm','act','study')): clink(wt(5,w)+0.35,0.1)
for i in range(8): tick(37.2+i*0.32,0.14)
thud(wt(6,'proof')-0.05,0.5)
for i in range(5): beep(43.4+[0,0.4,1.35,1.6,1.85][i],1400,0.05,0.04)
for i in range(4): beep(45.95+i*0.3,1800,0.05,0.04)
for i in range(4): heart(49.2+i*0.6,0.28)
clink(wt(9,'hand'),0.2); clink(wt(9,'hand')+0.3,0.15)
thud(wt(9,'ran')-0.05,0.5)
engine(55.9,1.6,0.06)
siren(57.7,1.8,0.04)
siren(64.0,1.8,0.05)
thud(wt(12,'gone')-0.05,0.55)
thud(wt(13,'richard')-0.1,0.4)
siren(71.0,1.5,0.05); engine(71.0,1.5,0.07)
thud(wt(14,'horrifying')-0.1,0.5)
boom(wt(15,'three')-0.1,0.3,1.6)
wind(82.3,2.6,0.05)
chime(wt(16,'save')-0.15,0.08)
for i in range(3): thud(wt(16,'solved')-0.05+i*0.25,0.35)
heart(90.3,0.2)
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
