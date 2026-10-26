"""Run a disposable Unity copy through actual CurvedUI hit tests and click events.

Every edited file lives under tools/u22-ui. Working/live assets and DLLs are never
written. The debug command is consumed by Unity's existing main-menu Update.
"""
from pathlib import Path
import argparse, ctypes, json, os, shutil, struct, subprocess, sys, time, winreg

R = Path(__file__).resolve().parent
F = R / 'tools/u22-ui'
W = F / 'working'
B = R / 'versions/cloudcourt-v21-antes-v22'
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
for name in ('customization_v19.c','avatar_style_v21.c','score_outline_v20.c'):
    shutil.copyfile(R/name,F/name)
shutil.copyfile(R / 'backup/GameAssembly.dll', F / 'backup/GameAssembly.dll')
source = (F / 'mode_2v2.c').read_text()

source = source.replace('static void probe(void* start){', 'EXPORT U64 probe_ui[96];\nstatic void probe(void* start){')
debug = r'''
 if(probe_command==10&&start){
  probe_command=0;void* panel=customization_panel_v19();probe_ui[0]=(U64)panel;
  preferences_loaded=1;preferred_skin=TEST_STYLE;
  if(panel){customization_refresh_v19();FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),1,0);
   for(int i=0;i<2;i++){
    void* t=find_child(panel,i?"CC_OutfitPreview":"CC_FacePreview");
    void* raw=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("RawImage"),0):0;
    void* tex=raw?FN(0x223290,void*(*)(void*,void*))(raw,0):0;
    probe_ui[1+i*4]=(U64)raw;probe_ui[2+i*4]=(U64)tex;
    if(tex){probe_ui[3+i*4]=FN(0xb72170,int(*)(void*,void*))(tex,0);probe_ui[4+i*4]=FN(0xb72130,int(*)(void*,void*))(tex,0);}
   }
  }
  void* domain=FN(0x14a920,void*(*)(void))();
  void* assembly=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.CoreModule");
  void* image=FN(0x14a530,void*(*)(void*))(assembly);
  void* gc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","GameObject");
  void* cc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","Camera");
  void* go=FN(0x1c22e0,void*(*)(void*))(gc);FN(0x94f8d0,void(*)(void*,void*,void*))(go,str("CloudcourtDebugCamera"),0);
  void* type=FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(cc));
  void* cam=FN(0x94f240,void*(*)(void*,void*,void*))(go,type,0);probe_ui[9]=(U64)cam;
  position_set(transform(cam),(V3){0,1.25f,-8.4f});FN(0xb75750,void(*)(void*,Q4,void*))(transform(cam),(Q4){0,0,0,1},0);
  FN(0x949a60,void(*)(void*,float,void*))(cam,999,0);FN(0x949b00,void(*)(void*,float,void*))(cam,45,0);
  void* cv=FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(menu_transform_v19()),str("Canvas"),0);if(cv)FN(0xece130,void(*)(void*,void*,void*))(cv,cam,0);
  FN(0x9499a0,void(*)(void*,int,void*))(cam,2,0);FN(0x9499e0,void(*)(void*,int,void*))(cam,-1,0);
 }
 if(probe_command==11&&start){
  probe_command=0;
  void* menu=menu_transform_v19();if(menu){position_set(menu,(V3){0,1.25f,-5.f});FN(0xb75750,void(*)(void*,Q4,void*))(menu,(Q4){0,0,0,1},0);}
  void* domain=FN(0x14a920,void*(*)(void))();void* assembly=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.CoreModule");
  void* image=FN(0x14a530,void*(*)(void*))(assembly);
  void* rtclass=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","RenderTexture");
  void* tc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","Texture2D");
  void* rt=FN(0x1c22e0,void*(*)(void*))(rtclass);FN(0xa1a6f0,void(*)(void*,int,int,int,void*))(rt,1024,768,24,0);
  FN(0xa19430,_Bool(*)(void*,void*))(rt,0);
  FN(0x949e00,void(*)(void*,void*,void*))((void*)probe_ui[9],rt,0);
  FN(0x948b30,void(*)(void*,void*))((void*)probe_ui[9],0);
  FN(0xa19c20,void(*)(void*,void*))(rt,0);
  void* tex=FN(0x1c22e0,void*(*)(void*))(tc);FN(0xb71570,void(*)(void*,int,int,int,_Bool,void*))(tex,1024,768,3,0,0);
  FN(0xb70cb0,void(*)(void*,Q4,int,int,_Bool,void*))(tex,(Q4){0,0,1024,768},0,0,0,0);
  FN(0xb702b0,void(*)(void*,_Bool,_Bool,void*))(tex,0,0,0);
  void* png=FN(0xedbea0,void*(*)(void*,void*))(tex,0);probe_ui[10]=png?*(U64*)((char*)png+0x18):0;
  if(png)FN(0x5cf690,void(*)(void*,void*,void*))(str(SCREENSHOT_PATH),png,0);
  FN(0xa19c20,void(*)(void*,void*))(0,0);
  FN(0x949e00,void(*)(void*,void*,void*))((void*)probe_ui[9],0,0);
 }
 if(probe_ui[9]){void* menu=menu_transform_v19();if(menu){position_set(menu,(V3){0,1.25f,-5.f});FN(0xb75750,void(*)(void*,Q4,void*))(menu,(Q4){0,0,0,1},0);}}
'''
debug = debug.replace('SCREENSHOT_PATH', json.dumps(str(shot))).replace('TEST_STYLE', str(args.face + 9 * args.outfit))
debug += r'''
 if(probe_command>=12&&probe_command<=17&&start){
  int command=probe_command;probe_command=0;void* panel=customization_panel_v19();void* menu=menu_transform_v19();
  const char* target=command==12?"CC_FaceNext":command==13?"CC_OutfitNext":command==14?"CC_HandToneNext":"CC_CustomizeBack";
  if(command==16){FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),1,0);target="CC_CustomizeBack";return;}
  int slot=16+((command==17?16:command)-12)*12;void* t=find_child(panel,target);V3 center=position(t);
  typedef struct{V3 o,d;} TestRay;TestRay ray={{center.x,center.y,-8.4f},{0,0,1}};
  void* caster=FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(menu),str("CurvedUIRaycaster"),0);
  void* hits=caster?FN(0x27c4a0,void*(*)(void*,TestRay,void*))(caster,ray,0):0;
  int count=hits?INT(hits,0x18):0;void* arr=hits?PTR(hits,0x10):0;void* first=count&&arr?PTR(arr,0x20):0;
  probe_ui[slot]=count;probe_ui[slot+1]=first==gameobject(t);probe_ui[slot+2]=FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(panel),0);
  probe_ui[slot+3]=preferred_style();probe_ui[slot+4]=preferred_hand_tone_v21;
  if(first){
   void* button=FN(0x94f410,void*(*)(void*,void*,void*))(first,str("Button"),0);
   if(button){
    void* domain=FN(0x14a920,void*(*)(void))();void* asm_=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.UI");
    void* img=FN(0x14a530,void*(*)(void*))(asm_);void* cls=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(img,"UnityEngine.EventSystems","PointerEventData");
    void* ev=FN(0x1c22e0,void*(*)(void*))(cls);FN(0x471c70,void(*)(void*,void*,void*))(ev,0,0);
    FN(0x472090,void(*)(void*,int,void*))(ev,0,0);FN(0x461da0,void(*)(void*,void*,void*))(button,ev,0);probe_ui[slot+5]=1;
   }
  }
  probe_ui[slot+6]=FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(panel),0);probe_ui[slot+7]=preferred_style();probe_ui[slot+8]=preferred_hand_tone_v21;
 }
'''
source = source.replace(' probe_ticks++;', debug + '\n probe_ticks++;')
(F / 'mode_2v2.c').write_text(source)
builder = (B / 'fontes/build_patch.py').read_text()
builder = builder.replace("sys.path.insert(0,str(R/'tools/python'))", "sys.path.insert(0," + repr(str(R / 'tools/python')) + ")\nsys.path.insert(0," + repr(str(R)) + ")")
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
    for _ in range(160):
        if proc.poll() is not None:raise RuntimeError(('Unity exited',proc.returncode))
        modules=(ctypes.c_void_p*512)();needed=ctypes.c_ulong()
        if ps.EnumProcessModulesEx(handle,modules,ctypes.sizeof(modules),ctypes.byref(needed),3):
            for module in modules[:min(needed.value//ctypes.sizeof(ctypes.c_void_p),512)]:
                path=ctypes.create_unicode_buffer(4096)
                ps.GetModuleFileNameExW(handle,module,path,4096)
                if path.value.endswith('GameAssembly.dll'):base=module;break
        if base and struct.unpack('<i',read(base+ex['probe_page_ready'],4))[0]:break
        time.sleep(.1)
    if not base:raise RuntimeError('GameAssembly not loaded')
    put(10)
    for _ in range(80):
        snapshot=struct.unpack('<96Q',read(base+ex['probe_ui'],768))
        if snapshot[9]:break
        time.sleep(.1)
    put(11);time.sleep(2)
    before_shot=shot.with_name('customization-'+args.tag+'-before.png')
    if shot.exists():shutil.copyfile(shot,before_shot)
    for cmd in (12,13,14,15,16,17):
        put(cmd);time.sleep(.6)
    put(11);time.sleep(1)
    snapshot=struct.unpack('<96Q',read(base+ex['probe_ui'],768))
    rows=[]
    for cmd,name in zip((12,13,14,15,16),('FaceNext','OutfitNext','HandToneNext','Done','Reopen and Done')):
        slot=16+(cmd-12)*12;v=snapshot[slot:slot+9]
        rows.append(dict(control=name,hit_count=v[0],top_hit_is_target=bool(v[1]),panel_before=bool(v[2]),style_before=v[3],tone_before=v[4],unity_pointer_click_invoked=bool(v[5]),panel_after=bool(v[6]),style_after=v[7],tone_after=v[8]))
    after_shot=shot.with_name('customization-'+args.tag+'-after.png')
    if shot.exists():shutil.copyfile(shot,after_shot)
    assert all(row['top_hit_is_target'] and row['unity_pointer_click_invoked'] for row in rows[:3])
    assert rows[0]['style_after']==rows[0]['style_before']+1 and rows[1]['style_after']==rows[1]['style_before']+9 and rows[2]['tone_after']==rows[2]['tone_before']+1
    expect_close=args.menu is not None
    assert all(row['top_hit_is_target']==expect_close and row['panel_after']!=expect_close for row in rows[3:])
    result={'passed':True,'expected_done_closes':expect_close,'rows':rows,'before_screenshot':str(before_shot),'after_screenshot':str(after_shot),'actual_CurvedUI_GetObjectsHitByRay':True,'unity_Button_OnPointerClick':True,'direct_button_press_hook':False,'working_or_live_modified':False,'preferences_restored':True,'menu':str(args.menu or B/'level0')}
    (R/('analysis/v22-ui-unity-'+args.tag+'.json')).write_text(json.dumps(result,indent=2))
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


