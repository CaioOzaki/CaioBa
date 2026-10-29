"""Execute the production training state + native-boundary fixture and assets.
No headset or two-PC claim; native Motion/Freeze calls are captured fixtures.
"""
from pathlib import Path
import ctypes,hashlib,json,os,subprocess,sys,math
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from fix_gloves_v16 import hierarchy
from build_training_v29 import apply_training_v29
D=R/'tools/training-v29';D.mkdir(exist_ok=True)
(D/'harness.c').write_text((R/'test_training_v29_harness.c').read_text().replace('#include "training_v29.c"','#include "../../training_v29.c"'))
env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str(R/'tools/zig-cache-v17'),ZIG_LOCAL_CACHE_DIR=str(R/'tools/zig-cache-v17'))
result=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(D/'harness.c'),'-o',str(D/'harness.dll'),'-Wl,--entry=DllMain'],capture_output=True,text=True,env=env)
assert result.returncode==0,result.stderr
n=ctypes.CDLL(str(D/'harness.dll'))
n.contact.argtypes=[ctypes.c_float]*6+[ctypes.c_int]*4;n.sample.argtypes=[ctypes.c_float]*4;n.ground.argtypes=[ctypes.c_float]*3
n.measure.restype=ctypes.c_float;n.text.restype=ctypes.c_char_p;n.press.argtypes=[ctypes.c_char_p]
def launch(drill):
 n.reset();assert n.value(13)==0,'cold reset searched scene objects'
 n.start(drill);n.tick();assert n.value(11)==1
 n.trigger(1);assert n.value(5)==0,'must release trigger after entering drill'
 n.trigger(0);n.trigger(1);assert n.value(5)==1 and n.value(3)==1
 for _ in range(20):n.trigger(1)
 assert n.value(3)==1,'held trigger repeated feed/spawn'
 assert n.value(12)==0 and n.value(14)>0,'GameObject and Component transform APIs mixed'
def repeat():
 for _ in range(4):n.tick()
 n.trigger(0);n.trigger(1)
def contact(x=0,y=1.1,z=-5.2,vy=6,vz=4,hit=1,thr=0,id=1,team=0):n.contact(x,y,z,0,vy,vz,hit,thr,id,team)
cases=[]
launch(1);assert n.value(4)==0 and n.value(8)==1 and n.value(9)==0
contact(x=-2.2,y=2,z=-7.6,thr=1);assert n.value(0)==1
contact(x=-2.2,y=2,z=-7.6);assert n.value(0)==2
n.ground(-2.2,.1,6.1);assert n.value(1)==n.value(2)==1 and n.measure(0)<.001
n.ground(-2.2,.1,6.1);assert n.value(1)==1,'same landing credited twice'
n.tick();assert b'TARGET HIT' in n.text(1) and b'1/1' in n.text(1)
repeat();contact();n.ground(3.8,.1,8.8);assert n.value(1)==2 and n.value(2)==1
cases.append('serve real contact/landing, miss, duplicate guard, fresh trigger')
for drill in (2,3):
 launch(drill);assert n.value(4)==1 and n.value(9)==1 and n.value(8)==0
 assert n.value(7)==(1 if drill==3 else 0),'set second-touch preparation'
 if drill==3:assert abs(n.measure(8)+2.2)<.001,'set starting ring must align with assisted-set target lane'
 tx,ty,tz=(0,2.15,-1.65) if drill==2 else (-2.2,3.1,-1.25)
 n.sample(tx,ty+1,tz,-2);n.sample(tx,ty-1,tz,-3);assert n.value(2)==0 and n.value(0)==1,'unhit feed credited'
 contact();n.sample(tx,ty+1,tz,-2);n.sample(tx,ty-1,tz,-4)
 assert n.value(1)==n.value(2)==1 and n.measure(0)<.001
 repeat();contact(vy=-2);n.sample(0,ty+1,tz,-2);n.sample(0,ty-1,tz,-4);assert n.value(1)==2 and n.value(2)==1,'invalid touch shape credited'
 repeat();contact();n.sample(4,ty+1,tz,-2);n.sample(4,ty-1,tz,-4);assert n.value(1)==3 and n.value(2)==1
 cases.append(('receive' if drill==2 else 'set')+' accepted contact, swept target crossing, wrong shape and miss')
launch(4);assert n.value(7)==2
contact(y=2.1,z=-1.7);n.ground(2.2,.1,4.7);assert n.value(2)==0,'below net hit credited as spike'
repeat();contact(y=3.1,z=-1.7,vy=-2,vz=8);n.ground(0,.1,4.7);assert n.value(2)==1
cases.append('spike above tape + actual ground target, below tape rejected')
launch(2);count=n.value(4);n.press(b'CC_TrainRepeat');assert n.value(4)==count,'repeat cooldown ignored'
for _ in range(5):n.tick()
n.press(b'CC_TrainRepeat');assert n.value(4)==count+1
n.press(b'CC_TrainEasy');assert ctypes.c_int.in_dll(n,'training_difficulty_v29').value==0
n.press(b'CC_TrainChallenge');assert ctypes.c_int.in_dll(n,'training_difficulty_v29').value==2
n.network(0,1);assert n.training_request_v29(2)==0;n.tick();assert n.value(11)==0 and n.value(8)==n.value(9)==n.value(10)==0
n.reset();assert n.training_request_v29(0)==n.training_request_v29(5)==0
cases.append('repeat cooldown/difficulty/network refusal/session cleanup')
# Ballistic feed solves real destination at requested time with native gravity.
launch(2);ox,oy,oz=[n.measure(i) for i in (1,2,3)];vx,vy,vz=[n.measure(i) for i in (4,5,6)];t=1.8
assert abs(oy+vy*t-4.905*t*t-1.1)<.001 and abs(oz+vz*t+5.2)<.001
at_net=-oz/vz;assert oy+vy*at_net-4.905*at_net*at_net>2.4
cases.append('receive feed arrives at 1.1m with above-2.4m net clearance')
source=R/'versions/cloudcourt-v28-antes-v29';resources=UnityPy.load(str(source/'resources.assets')).file;assets=[]
for scene_name in ('level1','level2','level3'):
 scene=UnityPy.load(str(source/scene_name)).file;report=apply_training_v29(resources,scene)
 gs,ts,paths=hierarchy(scene)
 for name in ('GroundTarget','AirTarget','Origin'):
  tid=paths['CC_TrainingTargets/'+name];go=gs[ts[tid]['m_GameObject']['m_PathID']]
  assert not go['m_IsActive'];assert len(go['m_Component'])==3
 assert apply_training_v29(resources,scene)=={'created':False,'idempotent':True}
 out=D/scene_name;out.write_bytes(scene.save());roundtrip=UnityPy.load(str(out)).file
 assert 'CC_TrainingTargets/AirTarget' in hierarchy(roundtrip)[2]
 assets.append(dict(scene=scene_name,**report))
report=dict(passed=True,production_sha256=hashlib.sha256((R/'training_v29.c').read_bytes()).hexdigest(),native_cases=cases,assets=assets,headset_tested=False,unity_runtime_tested=False)
(R/'analysis/v29-training-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
