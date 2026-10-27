"""All preset transitions defer render mutations until the next process."""
from pathlib import Path
import ctypes,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
env=dict(os.environ);env.update(ZIG_GLOBAL_CACHE_DIR=str(R/'tools/zig-cache-v17'),ZIG_LOCAL_CACHE_DIR=str(R/'tools/zig-cache-v17'))
h=(R/'test_graphics_v24_harness.c').read_text().replace('#include "graphics_v24.c"','#include "../graphics_v24.c"')
h=h.replace('static void child_label_v19(void* p,const char* path,const char* text){}',
'''static int warning;
static void child_label_v19(void* p,const char* path,const char* text){if(!strcmp(path,"CC_GraphicsLocal"))warning=strstr(text,"Restart Cloudcourt to apply")!=0;}''')
h+='\nEXPORT int test_running(void){return graphics_running_v26;}\nEXPORT int test_warning(void){return warning;}\nEXPORT void test_scene_reload(void){graphics_adaptive_start_hook(0,0);graphics_adaptive_apply_hook(0,0);}\n'
src=R/'tools/g26.c';src.write_text(h)
subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(src),'-o',str(R/'tools/g26.dll'),'-Wl,--entry=DllMain'],check=True,env=env,capture_output=True)
d=ctypes.CDLL(str(R/'tools/g26.dll'));d.test_press.argtypes=[ctypes.c_char_p];d.test_float.restype=ctypes.c_float
expect=[([0,1,0,0,0,0,0],[.7,15,.6]),([2,0,1,1,0,0,0],[.85,30,1]),([4,0,2,2,1,1,1],[.95,60,1.4]),([4,0,2,2,2,1,1],[1,150,2])]
rows=[]
for running in range(4):
 for selected,name in enumerate(('Low','Medium','High','Ultra')):
  d.test_reset(running);d.test_start();calls=d.test_value(11)
  assert d.test_running()==d.test_value(7)==running
  assert d.test_press(('CC_Graphics'+name).encode())==1
  assert d.test_value(7)==d.test_value(8)==selected and d.test_running()==running
  assert d.test_value(11)==calls,'Choice changed active render state'
  assert bool(d.test_warning())==(running!=selected)
  assert [d.test_value(j) for j in range(7)]==expect[running][0]
  assert all(abs(d.test_float(j)-expect[running][1][j])<1e-5 for j in range(3))
  d.test_scene_reload()
  assert d.test_running()==running and d.test_value(7)==selected
  assert [d.test_value(j) for j in range(7)]==expect[running][0]
  # New process reads the stored choice and applies the complete preset once.
  d.test_reset(selected);d.test_start()
  assert d.test_running()==d.test_value(7)==selected and not d.test_warning()
  assert [d.test_value(j) for j in range(7)]==expect[selected][0]
  rows.append(dict(running=running,selected=selected,no_live_render_mutation=True,persisted_to_next_start=True,scene_keeps_running_preset=True))
for invalid in (-2,9,2147483647):
 d.test_reset(invalid);d.test_start();assert d.test_running()==d.test_value(7)==3
assert d.test_ovr_fields(0)==d.test_ovr_fields(1)==1
import UnityPy
from build_ui_v26 import build_menu_v26
f=UnityPy.load(str(R/'versions/cloudcourt-v25-antes-v26/level0')).file
before={i:o.get_raw_data() for i,o in f.objects.items()};report=build_menu_v26(f)
assert not report['created_ids'] and len(report['changed_existing_ids'])==1
again=build_menu_v26(f);assert not again['changed_existing_ids']
result=dict(passed=True,transitions=rows,invalid_values_default_ultra=True,menu_delta=report,
            source_sha256=hashlib.sha256((R/'graphics_v24.c').read_bytes()).hexdigest(),VR_playtest=False)
(R/'analysis/v26-graphics-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(passed=True,transitions=len(rows),menu=report)))
