"""Production native preference/preset logic and serialized Unity menu checks."""
from pathlib import Path
import ctypes,hashlib,json,os,struct,subprocess,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_menu_v19 import MenuEditor,BUTTON,IMAGE,TEXT,CURVED,button_layout
from build_graphics_v24 import build_menu_v24
env=dict(os.environ);env.update(ZIG_GLOBAL_CACHE_DIR=str(R/'tools/zig-cache-v17'),ZIG_LOCAL_CACHE_DIR=str(R/'tools/zig-cache-v17'))
source=R/'tools/g24.c';source.write_text((R/'test_graphics_v24_harness.c').read_text().replace('#include "graphics_v24.c"','#include "../graphics_v24.c"'))
subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(source),'-o',str(R/'tools/g24.dll'),'-Wl,--entry=DllMain'],check=True,env=env,capture_output=True)
d=ctypes.CDLL(str(R/'tools/g24.dll'));d.test_press.argtypes=[ctypes.c_char_p];d.test_float.restype=ctypes.c_float
assert d.test_ovr_fields(0)==d.test_ovr_fields(1)==1
assert d.test_adaptive_apply()==1
expected=[([0,1,0,0,0,0,0],[.7,15,.6]),([2,0,1,1,0,0,0],[.85,30,1]),([4,0,2,2,1,1,1],[.95,60,1.4]),([4,0,2,2,2,1,1],[1,150,2])]
for invalid in (-1,-2,9,2147483647):
    d.test_reset(invalid);d.test_start();assert d.test_value(7)==3
    assert d.test_value(9)==0 # startup never writes unrelated/local defaults
for i,name in enumerate(('Low','Medium','High','Ultra')):
    d.test_reset(-1);assert d.test_press(b'CC_GraphicsOpen')==1 and d.test_value(10)==1
    assert d.test_press(('CC_Graphics'+name).encode())==1
    assert [d.test_value(j) for j in range(7)]==expected[i][0]
    assert all(abs(d.test_float(j)-expected[i][1][j])<1e-5 for j in range(3))
    assert d.test_value(7)==d.test_value(8)==i and d.test_value(9)==1
    assert d.test_press(b'CC_GraphicsBack')==1 and d.test_value(10)==0
    d.test_reset(i);d.test_start();assert d.test_value(7)==i
    calls=d.test_value(11);d.test_start();assert d.test_value(11)==calls
    assert d.test_press(b'Unrelated Button')==0
source=R/'versions/cloudcourt-v23-antes-v24/level0';f=UnityPy.load(str(source)).file
before={i:o.get_raw_data() for i,o in f.objects.items()};old=MenuEditor(f);canvas=f.objects[old.find('Menu')].read_typetree()
report=build_menu_v24(f);serialized=f.save();check=UnityPy.load(serialized).file;e=MenuEditor(check)
after_canvas=check.objects[e.find('Menu')].read_typetree()
assert all(canvas[k]==after_canvas[k] for k in canvas if k!='m_Children')
assert report['changed_existing_ids']==[145,616,640]
for p,i in e.paths()[2].items():
    if not (p.startswith('Menu/CC_Graphics') or p=='Menu/Pages/Settings/CC_GraphicsOpen'):continue
    t=check.objects[i].read_typetree();x,y=t['m_AnchoredPosition'].values();w,h=t['m_SizeDelta'].values()
    if e.component(i,BUTTON):
        raw=e.component(i,BUTTON).get_raw_data();_,event=button_layout(raw)
        assert struct.unpack_from('<I',raw,event)[0]==0
        assert -400<=x-w/2 and x+w/2<=400 and -200<=y-h/2 and y+h/2<=200
        assert e.component(i,IMAGE).get_raw_data()[60]==1
    if e.component(i,TEXT):assert e.component(i,TEXT).get_raw_data()[60]==0
repeat=build_menu_v24(check);assert not repeat['created_ids'] and not repeat['changed_existing_ids']
result=dict(passed=True,native_preferences_presets_reload_bounds_unknown_buttons=True,serialized_menu_bounds_and_zero_callbacks=True,unchanged_canvas_geometry_and_original_references=True,default='ULTRA',changed_existing_ids=report['changed_existing_ids'],added_count=len(report['created_ids']),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
(R/'analysis/v24-graphics-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
