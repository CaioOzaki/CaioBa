"""Native fixture for actual rewards_v29.c; does not install or run the game."""
from pathlib import Path
import ctypes,json,os,subprocess
R=Path(__file__).resolve().parent;D=R/'visuals-v29-rewards';D.mkdir(exist_ok=True)
env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(D/'zig-global');env['ZIG_LOCAL_CACHE_DIR']=str(D/'zig-local')
build=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(R/'test_rewards_v29_harness.c'),'-o',str(D/'reward-tests.dll'),'-Wl,--entry=DllMain'],env=env,capture_output=True,text=True)
assert build.returncode==0,build.stdout+build.stderr
d=ctypes.CDLL(str(D/'reward-tests.dll'));d.tick.argtypes=[ctypes.c_float]
for n in ['uv','scale','color','mirror_color']:getattr(d,n).restype=ctypes.c_float
d.label_value.restype=ctypes.c_char_p

def setup():d.setup();d.load()
def near(a,b):assert abs(a-b)<2e-6,(a,b)
def rgb(p,part,expected):
 for i,x in enumerate(expected):near(d.color(p,part,i),x/255)
def all_unlock():
 for k,n in [(1,2),(2,5),(3,5),(4,5)]:d.progress(k,n)

# Every route crosses its exact boundary; Skyline is combined receives+sets.
for kind,n,collection in [(1,2,1),(5,5,1),(4,5,3),(6,5,3)]:
 setup();d.progress(kind,n-1);assert d.unlocked(collection)==0;d.progress(kind,1);assert d.unlocked(collection)==1
setup();d.progress(2,4);d.progress(3,5);assert not d.unlocked(2);d.progress(3,1);assert d.unlocked(2)
assert d.unlocked(0)==1 and d.unlocked(-1)==0 and d.unlocked(4)==0
before=[d.value(i) for i in range(9)];sets=d.count(4)
for kind,amount in [(0,1),(7,1),(-5,9),(1,0),(1,-1)]:d.progress(kind,amount)
assert before==[d.value(i) for i in range(9)] and sets==d.count(4)
d.progress(1,2147483647);assert d.value(0)==1000000;d.progress(1,2147483647);assert d.value(0)==1000000

# Corrupt local settings cannot choose locked or out-of-range collections.
d.setup()
for i in range(6):d.setpref(i,-10)
for i,v in enumerate([3,99,-1],6):d.setpref(i,v)
d.load();assert [d.value(i) for i in range(9)]==[0]*9
setup();assert d.click(0,1)==1 and d.value(6)==0 and d.count(5)==0
assert d.click(-1,1)==0
d.progress(5,5);d.progress(6,5) # Sunset+Emerald; skip locked Skyline.
for wanted in [1,3,0,1]:d.click(0,1);assert d.value(6)==wanted
for wanted in [0,3,1]:d.click(0,-1);assert d.value(6)==wanted
assert d.value(7)==0 and d.value(8)==0
# SetInt records each mutation immediately. Save coalesces the burst.
assert d.count(3)==0;d.tick(1.0);assert d.count(3)==0;d.tick(.3);assert d.count(3)==1;d.tick(5);assert d.count(3)==1
d.click(1,1);d.tick(.8);d.click(2,1);d.tick(.8);assert d.count(3)==1;d.tick(.5);assert d.count(3)==2
before=[d.value(i) for i in range(9)];d.reset();assert before==[d.value(i) for i in range(9)];d.restart();assert before==[d.value(i) for i in range(9)]
d.progress(1,1);assert d.count(3)==2;d.reset();assert d.count(3)==3

# Independent, small companion packet leaves existing v21/v28 untouched.
setup()
for o in range(4):
 for f in range(4):
  for a in range(4):
   packet=d.rewards_encode_v29(o,f,a);oo,ff,aa=ctypes.c_int(),ctypes.c_int(),ctypes.c_int()
   assert d.rewards_decode_v29(packet,ctypes.byref(oo),ctypes.byref(ff),ctypes.byref(aa))==1
   assert (oo.value,ff.value,aa.value)==(o,f,a)
for values in [(-1,0,0),(4,0,0),(0,-1,0),(0,4,0),(0,0,-1),(0,0,4)]:assert d.rewards_encode_v29(*values)==-1
for bit in range(6,16):assert d.rewards_decode_v29(0x5c290000|(1<<bit),None,None,None)==-1
for unrelated in [0x5c210000,0x5c280000,0,0x5d290000]:assert d.rewards_decode_v29(unrelated,None,None,None)==0
for i in range(1,9):assert d.receive(i,d.rewards_encode_v29(i%4,(i+1)%4,(i+2)%4))==1
for i in range(1,9):assert [d.peer(i,k) for k in range(3)]==[i%4,(i+1)%4,(i+2)%4]
d.receive(9,d.rewards_encode_v29(3,3,3));assert [d.peer(9,k) for k in range(3)]==[0,0,0]
old=[d.peer(8,k) for k in range(3)];assert d.receive(8,0x5c290040)==1;assert old==[d.peer(8,k) for k in range(3)]
d.deadplayer(1);d.receive(8,d.rewards_encode_v29(1,2,3));assert d.peer_slots(8)==1 and [d.peer(8,k) for k in range(3)]==[1,2,3]
d.receive(9,d.rewards_encode_v29(3,2,1));assert [d.peer(9,k) for k in range(3)]==[3,2,1]

# Reuse head/body instances; source renderers remain disabled; all shared
# material setters are trapped. Independent outfit/face/accent selections.
setup();all_unlock();d.click(0,1);d.click(1,1);d.click(2,1);d.click(2,1)
d.run(0);assert [d.texture(0,i) for i in range(2)]==[2,3]
near(d.uv(0,0,0),0);near(d.uv(0,0,1),2/3);near(d.scale(0,0,0),1);near(d.scale(0,1,0),1)
rgb(0,2,(215,107,69));rgb(0,6,(99,215,244));assert d.count(2)==0
before=[d.count(i) for i in range(9)];root_count=d.root_total()
for _ in range(100):d.run(0)
assert before==[d.count(i) for i in range(9)] and root_count==d.root_total(),'stable body must not allocate, search, or rewrite materials'
# Reapply after the existing sleeves code changes transparency and resets color.
d.transparent_change(0,1);d.run(0);rgb(0,6,(99,215,244));d.transparent_change(0,0);d.run(0);rgb(0,6,(99,215,244))
# Peers may have other collections regardless of the local unlock catalog.
d.receive(1,d.rewards_encode_v29(3,2,1));d.run(1);near(d.uv(1,0,0),1/3);near(d.uv(1,1,0),2/3);rgb(1,2,(39,124,98));rgb(1,6,(255,207,88));rgb(0,2,(215,107,69))
# Base remains selected by original style, including all 81 base combinations.
for _ in range(3):d.click(0,1);d.click(1,1)
assert d.value(6)==d.value(7)==0
for style in range(81):
 d.style(0,style);d.run(0);assert [d.texture(0,i) for i in range(2)]==[0,1]
 for part,index in [(0,style%9),(1,style//9)]:near(d.uv(0,part,0),(index%3)/3);near(d.uv(0,part,1),(2-index//3)/3)
# Reset restores original texture/UV/palette and keeps preferences.
d.click(0,1);d.click(1,1);d.run(0);d.style(0,18);d.run(0);d.reset();assert [d.texture(0,i) for i in range(2)]==[0,1];near(d.uv(0,1,0),2/3);near(d.uv(0,1,1),2/3)
for part in [2,6]:
 for axis,x in enumerate([.06,.11,.16,1]):near(d.color(0,part,axis),x)
assert d.value(6)==d.value(7)==1
# Missing initial bindings retry when actual instances become available.
setup();all_unlock();d.click(1,1);d.material_missing(0,0);d.run(0);assert d.texture(0,0)==0;d.material_return(0,0);d.run(0);assert d.texture(0,0)==2
# Eight body slots remain bounded. Recycled slots restore old owned materials.
setup();all_unlock();d.click(0,1);d.run(0)
for p in range(1,8):d.run(p)
before=[d.count(i) for i in range(9)];d.run(8);assert before==[d.count(i) for i in range(9)]
d.body_dead(0);d.run(8);assert d.texture(0,1)==1
# Menu mirror follows preferences and preserves hand-tone materials.
setup();all_unlock();d.click(0,1);d.click(1,1);d.click(2,1);d.show();assert b'Sunset  UNLOCKED' in d.label_value(-1);assert d.label_value(1)==b'Wink'
d.mirror_run();assert [d.mirror_texture(i) for i in range(2)]==[2,3]
for i in [6,7]:
 for axis in range(4):near(d.mirror_color(i,axis),1)
d.mirror_base();d.mirror_run();near(d.mirror_color(2,0),215/255);assert d.count(2)==0
d.reset();assert [d.mirror_texture(i) for i in range(2)]==[0,1]
# Reproduce reward -> match reset -> native material loses mainTexture -> base.
# The persistent serialized UI atlases remain the source, not that null instance.
setup();all_unlock();d.click(0,1);d.click(1,1);d.mirror_run();d.reset();d.mirror_scene_loss()
for _ in range(3):d.click(0,1);d.click(1,1)
d.mirror_run();assert [d.mirror_texture(i) for i in range(2)]==[0,1]
report=dict(passed=True,checks=['actual compiled rewards_v29.c','all exact unlock boundaries and alternate routes','10 combined receives/sets','invalid events, saturated counters, corrupted preferences','base choices always available, skip locked choices, independent cycling','SetInt persistence, 1.25 second debounce and reset flush','64 packet combinations, reserved bits, unrelated protocols, eight peers and dead-slot reuse','owned head/body instances only; shared material writes trapped','reward texture/UV tiling and 81 base style restoration','independent peers and shirt/cuff palettes','transparent sleeves cache invalidation','100 idle updates perform zero searches/writes or root allocations','missing material retry, eight body slots and material restore on reuse','mirror applies after base refresh, preserves hands, restores on reset'],limitations=['Unity native calls are fixture stubs; no physical Quest3 or real two-PC claim','PlayerPrefs Save icall presence must be checked in desktop game runtime'])
(R/'analysis/v29-rewards-native-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

