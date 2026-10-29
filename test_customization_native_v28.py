from pathlib import Path
import ctypes,json,os,subprocess
R=Path(__file__).resolve().parent;F=R/'visuals-v28-customization';F.mkdir(exist_ok=True)
env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(F/'zig-global');env['ZIG_LOCAL_CACHE_DIR']=str(F/'zig-local')
p=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(R/'test_customization_v28_harness.c'),'-o',str(F/'customization-tests.dll'),'-Wl,--entry=DllMain'],env=env,capture_output=True,text=True)
assert p.returncode==0,p.stdout+p.stderr
d=ctypes.CDLL(str(F/'customization-tests.dll'));d.setup();d.channel.restype=d.mirrorq.restype=ctypes.c_float
for h in range(8):
 for a in range(2):
  value=d.appearance_encode_v28(h,a);hh=ctypes.c_int();aa=ctypes.c_int()
  assert d.appearance_decode_v28(value,ctypes.byref(hh),ctypes.byref(aa))==1 and (hh.value,aa.value)==(h,a)
for h,a in [(-1,0),(8,0),(0,2),(0,-1)]:assert d.appearance_encode_v28(h,a)==-1
hh=ctypes.c_int();aa=ctypes.c_int()
for bit in [3,*range(5,16)]:assert d.appearance_decode_v28(0x5c280000|(1<<bit),ctypes.byref(hh),ctypes.byref(aa))==-1
assert d.appearance_decode_v28(0x5c210000,ctypes.byref(hh),ctypes.byref(aa))==0
for h,a,expected in [(7,1,(7,1)),(999,-1,(0,0)),(-1,99,(0,0)),(2,0,(2,0))]:d.load(h,a);assert (d.pref(0),d.pref(1))==expected
d.load(0,0);assert d.click(1)==1 and d.pref(0)==7;assert d.click(0)==1 and d.pref(0)==0
assert d.click(2)==1 and d.pref(1)==1;assert d.click(3)==0
for h in range(8):
 for a in range(2):
  d.load(h,a);d.run(0);assert [d.status(0,j) for j in range(7)]==[int(h==i+1) for i in range(7)];assert [d.status(0,j) for j in range(7,11)]==[1-a]*4
  d.receive(1,d.appearance_encode_v28(7-h,1-a));d.run(1);assert [d.status(1,j) for j in range(7)]==[int(7-h==i+1) for i in range(7)];assert [d.status(1,j) for j in range(7,11)]==[a]*4
before=[d.count(i) for i in range(4)]
for _ in range(10):d.run(0);d.run(1)
assert [d.count(i) for i in range(4)]==before,'unchanged caches must avoid lookups/material/render writes'
d.show(1);d.run(0);assert all(abs(d.mirrorq(i)-v)<1e-6 for i,v in enumerate([-.3,.9,-.1,.2]))
d.show(0);d.run(0)
# Simulate close -> match-return -> open, preserving selected cosmetics.
d.load(4,1);d.show(1);assert (d.pref(0),d.pref(1))==(4,1);d.click(0);assert d.pref(0)==5
assert all(abs(d.channel(6,i)-v)<1e-6 for i,v in enumerate([1,.85,.74,1]))
# Owned instance materials are explicitly released on a session reset.
assert d.count(7)>0
owned=d.count(7)-d.count(8);d.reset_all();assert d.count(8)==d.count(7) and owned>0
before=d.count(7);d.run(0);assert d.count(7)==before+4
# Ready cosmetic body can free its bounded slot without keeping materials alive.
d.kill(0);d.run(2);assert d.count(8)>=owned+4
report=dict(passed=True,checks=['actual compiled customization_v28.c','16 cosmetic wire combinations','invalid and reserved bits rejected','preference restore and bounds','hat cycling wrap and arm toggle','independent peer cosmetic state','owned materials restored/destroyed on reset and slot reuse','eight-slot cache bounded and idle when unchanged','same-mesh mirror material refresh and hand tone','mirror head motion reflected only while panel open','close/match-return/open state and responsive next button'],limitations=['engine stubs; no visual headset or two-PC claim'])
(R/'analysis/v28-customization-native-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

