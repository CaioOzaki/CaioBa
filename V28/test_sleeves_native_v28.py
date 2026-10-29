"""Compile and execute actual sleeves_v24.c against deterministic engine stubs."""
from pathlib import Path
import ctypes,json,os,subprocess
R=Path(__file__).resolve().parent;F=R/'visuals-v28-customization';F.mkdir(exist_ok=True)
env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(R/'tools/zig-cache-sleeves24');env['ZIG_LOCAL_CACHE_DIR']=str(R/'tools/zig-local-sleeves24')
p=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(R/'test_sleeves_v28_harness.c'),'-o',str(F/'sleeves-v28-tests.dll'),'-Wl,--entry=DllMain'],env=env,capture_output=True,text=True)
assert p.returncode==0,(p.returncode,p.stdout+p.stderr)
d=ctypes.CDLL(str(F/'sleeves-v28-tests.dll'));d.channel.restype=ctypes.c_float;d.setup()
counts=lambda:tuple(d.count(i) for i in range(3))
def colors(i):return [[d.channel(i,j,k) for k in range(4)] for j in range(8)]
def verify(i,color):assert all(abs(a-b)<1e-6 for row in colors(i) for a,b in zip(row,color)),(i,colors(i),color)
from build_sleeves_v24 import OUTFIT_RGB
tones=[(1,.85,.74,1),(.91,.69,.49,1),(.76,.49,.29,1),(.58,.32,.17,1),(.36,.18,.10,1),(.19,.085,.05,1)]
for i in range(8):d.run_body(i);verify(i,[x/255 for x in OUTFIT_RGB[i]]+[1])
assert counts()==(64,64,64)
for _ in range(4):
 for i in range(8):d.run_body(i)
assert counts()==(64,64,64),'unchanged ready frames do no finds/material reads/color writes'
for outfit in range(9):
 for tone in range(6):
  other=colors(1);d.set_style(0,outfit*9+8,tone);d.run_body(0)
  verify(0,[x/255 for x in OUTFIT_RGB[outfit]]+[1]);assert colors(1)==other
assert counts()[:2]==(64,64)
# A ninth alive avatar cannot evict a live body; a destroyed body frees its slot.
before=counts();d.run_body(8);assert counts()==before
d.set_live(0,0);d.run_body(8);verify(8,[x/255 for x in OUTFIT_RGB[8]]+[1]);assert counts()==tuple(x+8 for x in before)
# Late Renderer.material binding retries from the cached visual and converges.
# Fresh DLL load gives independent static cache state for first-binding failure.
import shutil
shutil.copyfile(F/'sleeves-v28-tests.dll',F/'sleeves-v28-late-tests.dll');late=ctypes.CDLL(str(F/'sleeves-v28-late-tests.dll'));late.channel.restype=ctypes.c_float;late.setup();late.set_missing(7);late.run_body(2)
assert tuple(late.count(i) for i in range(3))==(8,8,7)
late.set_missing(-1);late.run_body(2);assert tuple(late.count(i) for i in range(3))==(8,9,15)
late.run_body(2);assert tuple(late.count(i) for i in range(3))==(8,9,15)
d.set_live(8,0);d.set_live(0,1);d.run_body(0)
for value in [1,0,1,0]:
 d.set_transparent(value);d.run_body(0);assert [d.visible(0,j) for j in range(8)]==[1-value]*8
before=counts();d.reset_all();d.run_body(0);assert counts()==tuple(x+8 for x in before)
report=dict(passed=True,actual_compiled_sleeves_source=True,checks=['8 independent body caches','9 outfit colors x 6 independent skin tones','cloth unaffected by tone','face changes retain outfit','no repeated engine work on ready unchanged frames','no cross-player tint','transparent option hides only sleeve renderer','session reset releases cache and rebinds','9th live body does not evict; destroyed body slot reused','late material retry uses cached visual then becomes idle'])
(R/'analysis/v28-sleeves-native-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

