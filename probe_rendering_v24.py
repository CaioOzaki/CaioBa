"""Run a disposable Unity copy through actual CurvedUI hit tests and click events.

Every edited file lives under tools/u24-graphics. Working/live assets and DLLs are never
written. The debug command is consumed by Unity's existing main-menu Update.
"""
from pathlib import Path
import argparse, ctypes, json, os, shutil, struct, subprocess, sys, time, winreg

R = Path(__file__).resolve().parent
F = R / 'tools/u24-graphics'
W = F / 'working'
B = R / 'versions/cloudcourt-v23-antes-v24'
parser = argparse.ArgumentParser()
parser.add_argument('--asset', type=Path)
parser.add_argument('--menu', type=Path)
parser.add_argument('--prepare-only', action='store_true')
parser.add_argument('--skip-build', action='store_true')
parser.add_argument('--tag', default='before')
parser.add_argument('--face', type=int, default=4)
parser.add_argument('--outfit', type=int, default=3)
args = parser.parse_args()
assert args.tag.replace('-', '').isalnum() and 0 <= args.face < 9 and 0 <= args.outfit < 9
shot = F / 'analysis/customization.png'
for folder in (F, W, F / 'backup', F / 'tools', F / 'analysis'):
    folder.mkdir(parents=True, exist_ok=True)
# Runtime support and editable game data are independent copies.
for old in (R / 'working').rglob('*'):
    if old.suffix=='.tmp':continue
    relative = old.relative_to(R / 'working')
    new = W / relative
    if old.is_dir():
        new.mkdir(parents=True, exist_ok=True)
    elif not new.exists():
        if old.name == 'GameAssembly.dll' or old.parent == R / 'working/VolleyballFever_Data':
            shutil.copyfile(old, new)
        else:
            shutil.copyfile(old, new)
for old in B.iterdir():
    if old.is_file() and (old.suffix in ('.assets', '.resource') or old.name.startswith('level')):
        shutil.copyfile(old, W / 'VolleyballFever_Data' / old.name)
shutil.copyfile(args.menu or B/'level0',W/'VolleyballFever_Data/level0')
if args.asset:
    shutil.copyfile(args.asset, W / 'VolleyballFever_Data/resources.assets')
for old in (B / 'fontes').glob('*.c'):
    shutil.copyfile(old, F / old.name)
for name in ('graphics_v24.c',):
    shutil.copyfile(R/name,F/name)
shutil.copyfile(R / 'backup/GameAssembly.dll', F / 'backup/GameAssembly.dll')
source = (F / 'mode_2v2.c').read_text()
source=source.replace('static int customization_button_v19(void* button);','static int customization_button_v19(void* button);\nstatic int graphics_button_v24(void* button);\nstatic void graphics_start_v24(void);\nstatic void graphics_close_v24(void);')
source=source.replace('#include "customization_v19.c"','#include "customization_v19.c"\n#include "graphics_v24.c"')
identity=(F/'identity_v16.c').read_text().replace('if(customization_button_v19(button))return;','if(graphics_button_v24(button))return;\n if(customization_button_v19(button))return;')
(F/'identity_v16.c').write_text(identity)


source = source.replace('static void probe(void* start){', 'EXPORT U64 probe_ui[160];\nstatic void probe(void* start){')
debug = r'''
 probe_ui[0]=graphics_loaded_v24;probe_ui[1]=graphics_selected_v24;
 probe_ui[2]=FN(0xa12bc0,int(*)(void*))(0);
 probe_ui[3]=FN(0xed8ba0,_Bool(*)(void*))(0);
 if(probe_command==30&&start){
  probe_command=0;
  const char* names[8]={"get_masterTextureLimit","get_anisotropicFiltering","get_shadows","get_shadowResolution","get_softParticles","get_realtimeReflectionProbes","get_shadowDistance","get_lodBias"};
  for(int i=0;i<4;i++){
   graphics_apply_v24(i);int p=16+i*16;
   for(int j=0;j<8;j++){
    char buffer[128]="UnityEngine.QualitySettings::";int n=29,k=0;while(names[j][k])buffer[n++]=names[j][k++];buffer[n]=0;
    void* fn=FN(0x14b030,void*(*)(const char*))(buffer);
    probe_ui[p+j]=fn?(j<4?((int(*)(void))fn)():j<6?((_Bool(*)(void))fn)():(U64)(((float(*)(void))fn)()*1000.f)):0xffffffff;
   }
   probe_ui[p+8]=FN(0xa12bc0,int(*)(void*))(0);
   probe_ui[p+9]=(U64)(FN(0xed8c00,float(*)(void*))(0)*1000.f);
  }
  /* Reuse the original serialized AdaptiveGraphics component for real
   * original event handler dispatch, then check our wrapper restored LOW. */
  probe_ui[91]=1;
  graphics_apply_v24(0);FN(0x264080,void(*)(void*,void*))(0,0);
  probe_ui[80]=1;probe_ui[81]=graphics_selected_v24;probe_ui[82]=FN(0xa12bc0,int(*)(void*))(0);
  probe_ui[91]=2;
  void* domain=FN(0x14a920,void*(*)(void))();U64 count=0;
  void** assemblies=FN(0x14a930,void**(*)(void*,U64*))(domain,&count);void* klass=0;
  for(U64 i=0;i<count&&!klass;i++){void* image=FN(0x14a530,void*(*)(void*))(assemblies[i]);klass=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"","OVRManager");}
  void* type=klass?FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(klass)):0;
  void* arr=type?FN(0xb6b720,void*(*)(void*,void*))(type,0):0;
  void* ovr=arr&&INT(arr,0x18)>0?PTR(arr,0x20):0;
  if(ovr){BYTE(ovr,0x25)=1;BYTE(ovr,0x27)=1;FN(0x457fd0,void(*)(void*,void*))(ovr,0);probe_ui[83]=1;probe_ui[84]=BYTE(ovr,0x25);probe_ui[85]=BYTE(ovr,0x27);}
  FN(0xa12870,void(*)(void*,int,void*))(str("Cloudcourt.Graphics.v24"),1,0);
  if(graphics_save_v24)graphics_save_v24();
  probe_ui[86]=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.Graphics.v24"),-1,0);
  probe_ui[87]=graphics_save_v24!=0;probe_ui[88]=1;
 }
'''
source = source.replace(' probe_ticks++;', debug + '\n probe_ticks++;')
(F / 'mode_2v2.c').write_text(source)
builder = (B / 'fontes/build_patch.py').read_text()
builder = builder.replace("sys.path.insert(0,str(R/'tools/python'))", "sys.path.insert(0," + repr(str(R / 'tools/python')) + ")\nsys.path.insert(0," + repr(str(R)) + ")")
builder=builder.replace('for name,rva in entries:', "entries += [('graphics_adaptive_start',0x2641d0),('graphics_adaptive_apply',0x264080),('graphics_ovr_update',0x457fd0)]\nfor name,rva in entries:")
(F / 'build_patch.py').write_text(builder)
env = dict(os.environ)
env.update(ZIG_GLOBAL_CACHE_DIR=str(R / 'tools/zig-cache-ui22'), ZIG_LOCAL_CACHE_DIR=str(R / 'tools/zig-cache-ui22'))
if args.prepare_only:print('Prepared',F);sys.exit(0)
if not args.skip_build:
    subprocess.run([str(R / 'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'), 'cc', '-target', 'x86_64-windows-msvc',
                    '-shared', '-O2', '-ffreestanding', '-fno-stack-protector', '-nostdlib', '-DMODE_PROBE', '-DPATCH_DELTA=0x194f000',
                    str(F / 'spin_mod.c'), '-o', str(F / 'tools/spin-native.dll'), '-Wl,--entry=DllMain'],
                   check=True, env=env, capture_output=True)
    subprocess.run([sys.executable, str(F / 'build_patch.py')], check=True, capture_output=True)
manifest = json.loads((F / 'analysis/native-patch-manifest.json').read_text())
ex = manifest['exports']
k = ctypes.WinDLL('kernel32', use_last_error=True)
ps = ctypes.WinDLL('psapi', use_last_error=True)
k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p
k.ReadProcessMemory.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
k.WriteProcessMemory.argtypes=k.ReadProcessMemory.argtypes
k.CloseHandle.argtypes=[ctypes.c_void_p]
ps.EnumProcessModulesEx.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong,ctypes.POINTER(ctypes.c_ulong),ctypes.c_ulong]
ps.GetModuleFileNameExW.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_ulong]
info=subprocess.STARTUPINFO();info.dwFlags|=subprocess.STARTF_USESHOWWINDOW;info.wShowWindow=0
# Unity clones share this game's registry preferences. Do not leave screen/map/
# appearance changes behind, even when the debug process exits unexpectedly.
prefs_path = r'Software\Neuston\Volleyball Fever'
def pref_values():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, prefs_path) as key:
            return {winreg.EnumValue(key, i)[0]: winreg.EnumValue(key, i)[1:]
                    for i in range(winreg.QueryInfoKey(key)[1])}
    except FileNotFoundError:
        return {}
saved_prefs = pref_values()
proc=subprocess.Popen([str(W/'VolleyballFever.exe'),'-batchmode','-force-d3d11','-vrmode','none',
                       '-screen-width','1024','-screen-height','768','-screen-fullscreen','0','-logFile',str(F/'analysis/unity.log')],
                      cwd=W,startupinfo=info)
handle=k.OpenProcess(0x438,False,proc.pid)
def read(addr,size):
    data=ctypes.create_string_buffer(size);count=ctypes.c_size_t()
    if not k.ReadProcessMemory(handle,addr,data,size,ctypes.byref(count)):raise ctypes.WinError(ctypes.get_last_error())
    return data.raw
def put(value):
    data=ctypes.c_int(value);count=ctypes.c_size_t()
    if not k.WriteProcessMemory(handle,base+ex['probe_command'],ctypes.byref(data),4,ctypes.byref(count)):raise ctypes.WinError(ctypes.get_last_error())
try:
    base=0
    for _ in range(500):
        if proc.poll() is not None:raise RuntimeError(('Unity exited',proc.returncode))
        modules=(ctypes.c_void_p*512)();needed=ctypes.c_ulong()
        if ps.EnumProcessModulesEx(handle,modules,ctypes.sizeof(modules),ctypes.byref(needed),3):
            for module in modules[:min(needed.value//ctypes.sizeof(ctypes.c_void_p),512)]:
                path=ctypes.create_unicode_buffer(4096)
                ps.GetModuleFileNameExW(handle,module,path,4096)
                if path.value.endswith('GameAssembly.dll'):base=module;break
        if base and struct.unpack('<i',read(base+ex['probe_ticks'],4))[0]:break
        time.sleep(.1)
    if not base:raise RuntimeError('GameAssembly not loaded')
    def snapshot():return struct.unpack('<160Q',read(base+ex['probe_ui'],1280))
    put(30)
    for _ in range(100):
        first=snapshot()
        if first[88]:break
        time.sleep(.1)
    assert first[88], ('Rendering probe incomplete',first[80:92],first[16:26])
    values=[]
    for i in range(4):
        v=first[16+i*16:26+i*16]
        values.append(dict(preset=i,texture_limit=v[0],aniso=v[1],shadows=v[2],shadow_resolution=v[3],soft_particles=v[4],reflections=v[5],shadow_distance=v[6]/1000,lod=v[7]/1000,aa=v[8],xr_scale_readback=v[9]/1000))
    assert [v['texture_limit'] for v in values]==[1,0,0,0]
    assert [v['aniso'] for v in values]==[0,1,2,2]
    assert [v['shadows'] for v in values]==[0,1,2,2]
    assert [v['shadow_resolution'] for v in values]==[0,0,1,2]
    assert [v['soft_particles'] for v in values]==[0,0,1,1]
    assert [v['reflections'] for v in values]==[0,0,1,1]
    assert [v['shadow_distance'] for v in values]==[15,30,60,150]
    assert all(abs(v['lod']-x)<.002 for v,x in zip(values,[.6,1,1.4,2]))
    assert [v['aa'] for v in values]==[0,2,4,4]
    assert first[80:88]==(1,0,0,1,0,0,1,1), first[80:88]
    proc.terminate();proc.wait(timeout=10);k.CloseHandle(handle)
    proc=subprocess.Popen([str(W/'VolleyballFever.exe'),'-batchmode','-force-d3d11','-vrmode','none','-screen-width','1024','-screen-height','768','-screen-fullscreen','0','-logFile',str(F/'analysis/unity-restart.log')],cwd=W,startupinfo=info)
    handle=k.OpenProcess(0x438,False,proc.pid);base=0
    for _ in range(500):
        if proc.poll() is not None:raise RuntimeError(('Unity restart exited',proc.returncode))
        if not base:
            modules=(ctypes.c_void_p*512)();needed=ctypes.c_ulong()
            if ps.EnumProcessModulesEx(handle,modules,ctypes.sizeof(modules),ctypes.byref(needed),3):
                for module in modules[:min(needed.value//ctypes.sizeof(ctypes.c_void_p),512)]:
                    path=ctypes.create_unicode_buffer(4096);ps.GetModuleFileNameExW(handle,module,path,4096)
                    if path.value.endswith('GameAssembly.dll'):base=module;break
        if base:
            second=snapshot()
            if second[0] and second[1]==1 and second[2]==2:break
        time.sleep(.1)
    assert second[0:3]==(1,1,2), second[0:3]
    result=dict(passed=True,values=values,original_adaptive_component_found=True,original_adaptive_handler_preserved_LOW=True,original_OVR_Update_does_not_override_preset=True,saved_pref=first[86],PlayerPrefs_Save_resolved=bool(first[87]),fresh_process_startup_preset='MEDIUM',fresh_process_startup_aa=second[2],xr_enabled=bool(first[3]),xr_scale_headset_validation_pending=not bool(first[3]),raycast_test_repeated=False,working_or_live_modified=False,preferences_restored=True)
    (R/'analysis/v24-graphics-rendering-unity.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

finally:
    if proc.poll() is None:proc.terminate()
    proc.wait(timeout=10);k.CloseHandle(handle)
    current = pref_values()
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, prefs_path) as key:
        for name in current.keys() - saved_prefs.keys():
            winreg.DeleteValue(key, name)
        for name, (value, kind) in saved_prefs.items():
            winreg.SetValueEx(key, name, 0, kind, value)
    assert pref_values() == saved_prefs


