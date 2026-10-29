"""Focused production-native hit feedback tests. No game files are modified."""
from pathlib import Path
import ctypes,subprocess,os,math,json,sys
R=Path(__file__).resolve().parent
D=R/'tools/hit-v29';D.mkdir(exist_ok=True)
s=(R/'test_hit_feedback_v29_harness.c').read_text(encoding='utf-8-sig').replace('#include "hit_feedback_v29.c"','#include "../../hit_feedback_v29.c"')
(D/'harness.c').write_text(s,encoding='utf-8')
env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str(D/'global-cache'),ZIG_LOCAL_CACHE_DIR=str(D/'local-cache'))
p=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(D/'harness.c'),'-o',str(D/'harness.dll'),'-Wl,--entry=DllMain'],env=env,text=True,capture_output=True)
assert p.returncode==0,p.stderr
n=ctypes.CDLL(str(D/'harness.dll'))
class V(ctypes.Structure):_fields_=[('x',ctypes.c_float),('y',ctypes.c_float),('z',ctypes.c_float)]
n.classify.argtypes=[ctypes.POINTER(V)]*3+[ctypes.c_int]
n.begin.argtypes=[ctypes.POINTER(V),ctypes.POINTER(V),ctypes.c_int,ctypes.c_int]
n.accept.argtypes=[ctypes.POINTER(V),ctypes.c_int]
n.level.restype=ctypes.c_float;n.sample.restype=ctypes.c_float
checks=0
cases=[('gentle tap',(0,-1,0),(0,.5,0),(0,2,0),0,0),('controlled fast receive',(0,-12,0),(0,.8,0),(0,5,0),0,1),('ordinary receive',(0,-5,0),(0,1,0),(0,5,0),0,1),('strong driven spike',(0,-4,0),(0,-5,0),(0,-10,5),0,2),('fast horizontal attack',(0,-2,0),(7,0,0),(14,0,0),0,2),('soft overhead set',(0,-4,0),(0,1.5,0),(0,7,0),0,1),('fast assisted set',(0,-4,0),(0,-7,0),(0,-14,0),1,1),('fast incoming does not imply spike',(0,-22,0),(0,.4,0),(0,12,0),0,1),('swing without fast return',(0,-2,0),(0,-4,0),(0,-4,0),0,0),('upward jump set',(0,-4,0),(0,7,0),(0,13,0),0,0)]
for name,i,h,o,a,want in cases:
 assert n.classify(ctypes.byref(V(*i)),ctypes.byref(V(*h)),ctypes.byref(V(*o)),a)==want,name;checks+=1
for value in [float('nan'),float('inf'),-float('inf'),1e30]:
 for arg in range(3):
  v=[V(0,-5,0),V(0,-5,0),V(0,-12,0)];v[arg]=V(value,0,0)
  assert n.classify(*(ctypes.byref(x) for x in v),0)==0;checks+=1

def begin(kind=0,owned=1):
 _,i,h,o,a,_=cases[[0,1,3][kind]]
 n.begin(ctypes.byref(V(*i)),ctypes.byref(V(*h)),a,owned)
 return V(*o)
def accept(kind=0):
 o=begin(kind);n.accept(ctypes.byref(o),1)

n.reset();o=begin(2)
assert n.sound(1)==-1 and n.value(0)==0
n.haptic(0);assert n.value(3)==1 and n.value(5)==0
n.accept(ctypes.byref(o),0);assert n.value(9)==0
n.accept(ctypes.byref(o),1);assert n.value(10)==2
assert n.sound(0)==-1 and n.value(0)==0
assert n.sound(1)==0 and n.value(0)==1
for _ in range(300):assert n.sound(1)==0
assert [n.value(k) for k in [0,1,2,11]]==[1,1,1,1]
n.haptic(0);assert abs(n.level(0)-.78)<1e-6 and abs(n.level(1)-.092)<1e-6
assert n.value(12)==1 and n.value(4)==1 and n.value(5)==1
n.haptic(0);assert n.value(5)==1 and n.value(3)==1
n.haptic(1);assert n.value(13)==1 and n.value(4)==2 and n.value(5)==2
n.haptic(2);assert n.value(3)==2
n.other_haptic(17,0);n.other_haptic(18,1);assert n.value(3)==4
n.end();assert n.value(8)==0 and n.value(9)==0 and n.sound(1)==-1
n.haptic(0);assert n.value(3)==5
assert n.value(6)==0,'native method/argument ABI mismatch'

n.reset();n.begin(ctypes.byref(V(0,-4,0)),ctypes.byref(V(0,-5,0)),0,0)
n.accept(ctypes.byref(V(0,-15,0)),1)
assert n.value(8)==0 and n.sound(1)==-1
for k in range(1,5):
 n.reset();n.invalid_contact(k);begin();assert n.value(8)==0

profiles=[]
n.reset()
for k,count in enumerate([1654,2425,3087]):
 accept(k);assert n.sound(1)==k;n.haptic(0);amp=n.level(0);duration=n.level(1)
 pcm=[n.sample(k,i) for i in range(count)]
 peak=max(map(abs,pcm));rms=math.sqrt(sum(x*x for x in pcm)/count)
 assert all(map(math.isfinite,pcm)) and 0<peak<.72 and .015<rms<.2,(k,peak,rms)
 assert abs(pcm[0])<1e-6 and abs(pcm[-1])<.0001
 first=sum(x*x for x in pcm[:400]);last=sum(x*x for x in pcm[-400:]);assert first>last*200
 profiles.append(dict(kind=['weak','receive','spike'][k],peak=peak,rms=rms,seconds=count/22050,haptic_amplitude=amp,haptic_seconds=duration))
 n.end()
assert profiles[0]['peak']<profiles[1]['peak']<profiles[2]['peak']
assert profiles[0]['haptic_seconds']<profiles[1]['haptic_seconds']<profiles[2]['haptic_seconds']
assert [n.value(k) for k in [0,1,2,11]]==[3,3,3,3]
for _ in range(100):
 for k in range(3):accept(k);n.sound(1);n.end()
assert [n.value(k) for k in [0,1,2,11]]==[3,3,3,3]

for failure in [1,2]:
 n.reset();n.failure(failure);accept(0)
 for _ in range(100):assert n.sound(1)==-1
 assert n.value(0)==(1 if failure==2 else 0)
 assert n.value(7)==(1 if failure==2 else 0) and n.value(11)==0
for failure in [3,4]:
 n.reset();n.failure(failure);accept(1);n.haptic(0)
 assert n.value(3)==1 and n.value(5)==0 and n.value(4)==0
assert n.value(6)==0
r=dict(passed=True,native_classification_cases=checks,accepted_local_context=True,rejected_and_remote_contacts_preserved=True,exact_effect_replacement_no_added_play=True,three_cached_original_synth_clips=True,bounded_gc_roots=True,both_backends_native_coroutine_ownership=True,duplicate_controller_suppression=True,menu_and_unsupported_haptics_preserved=True,failure_fallbacks=True,profiles=profiles,headset_tested=False)
(R/'analysis/v29-hit-feedback-tests.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps(r))
