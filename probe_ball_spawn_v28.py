"""Run a disposable Unity copy through actual CurvedUI hit tests and click events.

Every edited file lives under tools/u26-ui. Working/live assets and DLLs are never
written. The debug command is consumed by Unity's existing main-menu Update.
"""
from pathlib import Path
import argparse, ctypes, json, os, shutil, struct, subprocess, sys, time, winreg

R = Path(__file__).resolve().parent
F = R / 'tools/u28-ball'
W = F / 'working'
B = R / 'versions/cloudcourt-v27-antes-v28'
parser = argparse.ArgumentParser()
parser.add_argument('--asset', type=Path)
parser.add_argument('--menu', type=Path)
parser.add_argument('--prepare-only', action='store_true')
parser.add_argument('--skip-build', action='store_true')
parser.add_argument('--tag', default='after')
parser.add_argument('--before', action='store_true')
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

if not args.before:shutil.copyfile(R/'ball_style_v26.c',F/'ball_style_v26.c')
shutil.copyfile(R / 'backup/GameAssembly.dll', F / 'backup/GameAssembly.dll')
source = (F / 'mode_2v2.c').read_text()

source = source.replace('static void probe(void* start){', 'EXPORT U64 probe_ui[256];\nstatic void probe(void* start){')
debug = '\n if(probe_command==40&&start){\n  probe_command=0;\n  void* domain=FN(0x14a920,void*(*)(void))();\n  void* assembly=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.CoreModule");\n  void* image=FN(0x14a530,void*(*)(void*))(assembly);\n  void* gc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","GameObject");\n  void* cc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","Camera");\n  void* cameraGo=FN(0x1c22e0,void*(*)(void*))(gc);FN(0x94f8d0,void(*)(void*,void*,void*))(cameraGo,str("BallSpawnProbeCamera"),0);\n  void* type=FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(cc));\n  void* cam=FN(0x94f240,void*(*)(void*,void*,void*))(cameraGo,type,0);probe_ui[100]=(U64)cam;\n  position_set(transform(cam),(V3){0,1.4f,-6.65f});FN(0xb75750,void(*)(void*,Q4,void*))(transform(cam),(Q4){0,0,0,1},0);\n  FN(0x949a60,void(*)(void*,float,void*))(cam,999,0);FN(0x949b00,void(*)(void*,float,void*))(cam,35,0);\n  FN(0x9499a0,void(*)(void*,int,void*))(cam,2,0);FN(0x9499e0,void(*)(void*,int,void*))(cam,-1,0);\n  for(int i=0;i<2;i++){\n   void* prefab=FN(0xb6b7b0,void*(*)(void*,void*))(str(i?"VolleyballBomb":"Volleyball"),0);\n   void* go=prefab?FN(0xa0b7a0,void*(*)(void*,V3,Q4,void*))(prefab,(V3){i?.4f:-.4f,1.4f,-5.f},(Q4){0,0,0,1},0):0;\n   void* ball=go?FN(0x94f410,void*(*)(void*,void*,void*))(go,str("Volleyball"),0):0;\n   probe_ui[i*40]=(U64)ball;\n   if(ball){\n    FN(0x77e220,void(*)(void*,void*))(ball,0);\n    void* local=PTR(ball,0x30);if(local)FN(0xec5e00,void(*)(void*,_Bool,void*))(local,1,0);\n   }\n  }\n }\n if(probe_command>=41&&probe_command<=44&&start){\n  int command=probe_command;probe_command=0;\n  for(int i=0;i<2;i++){\n   int k=i*40;void* ball=(void*)probe_ui[k];if(!ball)continue;\n   if(command==42)FN(0x77ee60,void(*)(void*,void*))(ball,0);\n   if(command==43)FN(0x77ee30,void(*)(void*,void*))(ball,0);\n   if(command==44){\n    void* visual=PTR(ball,0x38);void* regular=find_child(visual,"RegularMesh");\n    void* fallback=regular?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(regular),str("MeshRenderer"),0):0;\n    if(fallback)FN(0xa1b2f0,void(*)(void*,_Bool,void*))(fallback,1,0);\n   }\n   void* visual=PTR(ball,0x38);void* native=PTR(ball,0x40);\n   void* old=find_child(transform(ball),"VisualVolleyball/RegularMesh/DavidVolleyball");\n   void* t=find_child(visual,"RegularMesh/DavidVolleyball");\n   void* renderer=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshRenderer"),0):0;\n   void* mf=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshFilter"),0):0;\n   void* mesh=mf?FN(0xa062c0,void*(*)(void*,void*))(mf,0):0;\n   void* mat=renderer?FN(0xa1af10,void*(*)(void*,void*))(renderer,0):0;\n   probe_ui[k+1]=(U64)visual;probe_ui[k+2]=(U64)old;probe_ui[k+3]=(U64)t;\n   probe_ui[k+4]=(U64)renderer;probe_ui[k+5]=renderer?FN(0xa1b1e0,_Bool(*)(void*,void*))(renderer,0):0;\n   probe_ui[k+6]=(U64)native;probe_ui[k+7]=native?FN(0xa1b1e0,_Bool(*)(void*,void*))(native,0):0;\n   probe_ui[k+8]=(U64)mat;probe_ui[k+9]=mesh?FN(0xa09680,int(*)(void*,void*))(mesh,0):0;\n   probe_ui[k+10]=mat?(U64)(FN(0x955350,int(*)(void*,void*,void*))(mat,str("_Mode"),0)*1000):0;\n   probe_ui[k+11]=(U64)PTR(ball,0x60);probe_ui[k+12]=(U64)PTR(ball,0x80);\n   probe_ui[k+13]=mat?FN(0x9556c0,_Bool(*)(void*,void*,void*))(mat,str("_ALPHAPREMULTIPLY_ON"),0):0;\n  }\n }\n if(probe_command==47&&start){\n  probe_command=0;void* cam=(void*)probe_ui[100];\n  void* domain=FN(0x14a920,void*(*)(void))();void* assembly=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.CoreModule");\n  void* image=FN(0x14a530,void*(*)(void*))(assembly);\n  void* rc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","RenderTexture");\n  void* tc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","Texture2D");\n  void* rt=FN(0x1c22e0,void*(*)(void*))(rc);FN(0xa1a6f0,void(*)(void*,int,int,int,void*))(rt,1024,768,24,0);FN(0xa19430,_Bool(*)(void*,void*))(rt,0);\n  FN(0x949e00,void(*)(void*,void*,void*))(cam,rt,0);FN(0x948b30,void(*)(void*,void*))(cam,0);FN(0xa19c20,void(*)(void*,void*))(rt,0);\n  void* tex=FN(0x1c22e0,void*(*)(void*))(tc);FN(0xb71570,void(*)(void*,int,int,int,_Bool,void*))(tex,1024,768,3,0,0);\n  FN(0xb70cb0,void(*)(void*,Q4,int,int,_Bool,void*))(tex,(Q4){0,0,1024,768},0,0,0,0);FN(0xb702b0,void(*)(void*,_Bool,_Bool,void*))(tex,0,0,0);\n  void* png=FN(0xedbea0,void*(*)(void*,void*))(tex,0);if(png)FN(0x5cf690,void(*)(void*,void*,void*))(str(SCREENSHOT_PATH),png,0);\n  FN(0xa19c20,void(*)(void*,void*))(0,0);FN(0x949e00,void(*)(void*,void*,void*))(cam,0,0);\n  FN(0xa0ab40,void(*)(void*,void*))(tex,0);FN(0xa0ab40,void(*)(void*,void*))(rt,0);\n }\n'
debug=debug.replace('SCREENSHOT_PATH',json.dumps(str(shot)))
source = source.replace(' probe_ticks++;', debug + '\n probe_ticks++;')
(F / 'mode_2v2.c').write_text(source)
builder = (B / 'fontes/build_patch.py').read_text()
builder = builder.replace("sys.path.insert(0,str(R/'tools/python'))", "sys.path.insert(0," + repr(str(R / 'tools/python')) + ")\nsys.path.insert(0," + repr(str(R)) + ")")
(F / 'build_patch.py').write_text(builder)
env = dict(os.environ)
env.update(ZIG_GLOBAL_CACHE_DIR=str(R / 'tools/zig-cache-ball28'), ZIG_LOCAL_CACHE_DIR=str(R / 'tools/zig-cache-ball28'))
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
    for _ in range(600):
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
    time.sleep(6)  # Wait for startup Indoor scene load before creating a debug camera.
    put(40);time.sleep(2)
    rows=[]
    for command in (41,42,41,43,41,44,41):
        put(command);time.sleep(.4)
        snapshot=struct.unpack('<256Q',read(base+ex['probe_ui'],2048))
        rows.append(dict(command=command,balls=[list(snapshot[:14]),list(snapshot[40:54])]))
    put(47);time.sleep(.7)
    render=shot.with_name('v28-ball-'+args.tag+'.png');shutil.copyfile(shot,render)
    result=dict(passed=True,before=args.before,rows=rows,scope='Actual Unity object Instantiate and native Awake, both resource prefabs, native transparent/solid changes, fallback re-enable',working_or_live_modified=False,preferences_restored=True)
    (R/('analysis/v28-ball-unity-'+args.tag+'.json')).write_text(json.dumps(result,indent=2))
    assert all(row['balls'][i][0] and row['balls'][i][1] and not row['balls'][i][2] and row['balls'][i][3] for row in rows for i in range(2)), 'Awake hierarchy detachment mismatch'
    if not args.before:
        for row in rows:
            for ball in row['balls']:
                assert ball[5] and ball[9]==6144, ('authored renderer missing',row)
        assert all(not ball[7] for ball in rows[-1]['balls']), 'Fallback re-enable was not repaired'
        assert all(ball[10]==3000 and ball[13] for ball in rows[2]['balls']), 'Transparent material state not mirrored'
        assert all(ball[10]==0 and not ball[13] for ball in rows[4]['balls']), 'Solid material state not restored'
    result['screenshot']=str(render)
    (R/('analysis/v28-ball-unity-'+args.tag+'.json')).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

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


