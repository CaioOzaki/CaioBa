"""Run a disposable Unity copy through actual CurvedUI hit tests and click events.

Every edited file lives under tools/u28-custom. Working/live assets and DLLs are never
written. The debug command is consumed by Unity's existing main-menu Update.
"""
from pathlib import Path
import argparse, ctypes, json, os, shutil, struct, subprocess, sys, time, winreg

R = Path(__file__).resolve().parent
F = R / 'tools/u28-custom'
W = F / 'working'
B = R / 'versions/cloudcourt-v27-antes-v28'
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
    for own in ['sharedassets0.assets','sharedassets0.resource']:
        shutil.copyfile(args.asset.parent/own,W/'VolleyballFever_Data'/own)
for old in (B / 'fontes').glob('*.c'):
    shutil.copyfile(old, F / old.name)
for name in [p.name for p in R.glob('*.c')]:
    shutil.copyfile(R/name,F/name)
shutil.copyfile(R / 'backup/GameAssembly.dll', F / 'backup/GameAssembly.dll')
source = (F / 'mode_2v2.c').read_text()

source = source.replace('static void probe(void* start){', 'EXPORT U64 probe_ui[256];\nstatic void probe(void* start){')
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
  const char* target=command==12?"CC_FaceNext":command==13?"CC_OutfitNext":command==14?"CC_HandToneNext":command==15?"CC_HatNext":command==16?"CC_ArmsNext":"CC_CustomizeBack";

  int slot=16+(command-12)*12;void* t=find_child(panel,target);V3 center=position(t);
  typedef struct{V3 o,d;} TestRay;TestRay ray={{center.x,center.y,-8.4f},{0,0,1}};
  void* caster=FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(menu),str("CurvedUIRaycaster"),0);
  void* hits=caster?FN(0x27c4a0,void*(*)(void*,TestRay,void*))(caster,ray,0):0;
  int count=hits?INT(hits,0x18):0;void* arr=hits?PTR(hits,0x10):0;void* first=count&&arr?PTR(arr,0x20):0;
  probe_ui[slot]=count;probe_ui[slot+1]=first==gameobject(t);probe_ui[slot+2]=FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(panel),0);
  probe_ui[slot+3]=preferred_style();probe_ui[slot+4]=preferred_hand_tone_v21;probe_ui[slot+9]=preferred_hat_v28;
  if(first){
   void* button=FN(0x94f410,void*(*)(void*,void*,void*))(first,str("Button"),0);
   if(button){
    void* domain=FN(0x14a920,void*(*)(void))();void* asm_=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.UI");
    void* img=FN(0x14a530,void*(*)(void*))(asm_);void* cls=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(img,"UnityEngine.EventSystems","PointerEventData");
    void* ev=FN(0x1c22e0,void*(*)(void*))(cls);FN(0x471c70,void(*)(void*,void*,void*))(ev,0,0);
    FN(0x472090,void(*)(void*,int,void*))(ev,0,0);FN(0x461da0,void(*)(void*,void*,void*))(button,ev,0);probe_ui[slot+5]=1;
   }
  }
  probe_ui[slot+6]=FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(panel),0);probe_ui[slot+7]=preferred_style();probe_ui[slot+8]=preferred_hand_tone_v21;probe_ui[slot+10]=preferred_hat_v28;probe_ui[slot+11]=preferred_transparent_arms_v28;
 }
'''

debug += r"""
 if(probe_command==20&&start){
  probe_command=0;customization_close_v19();
  /* Run the real page-entry hook between visits, as the menu transition does. */
  main_menu_hook(start,0,0);
  void* panel=customization_panel_v19();
  if(panel){customization_refresh_v19();FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),1,0);}
 }
 if(probe_command==21&&start){customization_probe_v28(9);
  probe_command=0;void* panel=customization_panel_v19();
  for(int i=0;i<2;i++){
   void* t=find_child(panel,i?"CC_OutfitPreview":"CC_FacePreview");
   void* raw=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("RawImage"),0):0;
   void* fx=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("CurvedUIVertexEffect"),0):0;
   int k=100+i*20;probe_ui[k]=(U64)raw;probe_ui[k+1]=(U64)fx;
   if(raw){Q4 uv=*(Q4*)((char*)raw+0xd0);probe_ui[k+2]=(U64)(uv.x*10000);probe_ui[k+3]=(U64)(uv.y*10000);}
   if(fx){probe_ui[k+4]=BYTE(fx,0x58);probe_ui[k+5]=BYTE(fx,0x59);probe_ui[k+6]=(U64)PTR(fx,0x160);probe_ui[k+7]=(U64)PTR(fx,0x168);}
  }
 }
 if(probe_command==30&&start){
  probe_command=0;customization_close_v19();
  void* domain=FN(0x14a920,void*(*)(void))();
  void* core=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.CoreModule");
  void* ci=FN(0x14a530,void*(*)(void*))(core);
  void* gc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(ci,"UnityEngine","GameObject");
  void* assembly=FN(0x14a910,void*(*)(void*,const char*))(domain,"Unity.TextMeshPro");
  void* image=assembly?FN(0x14a530,void*(*)(void*))(assembly):0;
  void* cls=image?FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"TMPro","TextMeshPro"):0;
  probe_ui[155]=(U64)assembly;probe_ui[156]=(U64)image;probe_ui[157]=(U64)cls;
  if(cls){
   void* go=FN(0x1c22e0,void*(*)(void*))(gc);FN(0x94f8d0,void(*)(void*,void*,void*))(go,str("Cloudcourt Point Popup Probe"),0);
   void* type=FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(cls));
   void* text=FN(0x94f240,void*(*)(void*,void*,void*))(go,type,0);probe_ui[150]=(U64)text;
   if(text){
    style_tmp(text);FN(0x23f9d0,void(*)(void*,float,void*))(text,48,0);
    void* rt=FN(0x94f410,void*(*)(void*,void*,void*))(go,str("RectTransform"),0);
    if(rt)FN(0xa17260,void(*)(void*,V2,void*))(rt,(V2){600,200},0);
    position_set(transform(text),(V3){-1.6f,1.9f,-6.f});FN(0xb75750,void(*)(void*,Q4,void*))(transform(text),(Q4){0,0,0,1},0);
    FN(0xb75560,void(*)(void*,V3,void*))(transform(text),(V3){.006f,.006f,.006f},0);
    FN(0x2405f0,void(*)(void*,void*,void*))(text,str("<color=#75CFFF>BLUE +1</color>\n<size=60%>Four touches by red team</size>"),0);
    void* mat=FN(0x23e790,void*(*)(void*,void*))(text,0);probe_ui[151]=(U64)mat;
    probe_ui[152]=mat?FN(0x9556c0,_Bool(*)(void*,void*,void*))(mat,str("OUTLINE_ON"),0):0;
    score_outline_tmp_force_v21(text);
    probe_ui[153]=mat?FN(0x9556c0,_Bool(*)(void*,void*,void*))(mat,str("OUTLINE_ON"),0):0;
    probe_ui[154]=(U64)(FN(0x23eba0,float(*)(void*,void*))(text,0)*10000);
   }
  }
 }
 if(probe_command==31&&start){
  probe_command=0;probe_ui[160]=graphics_running_v26;probe_ui[161]=FN(0xa12bc0,int(*)(void*))(0);
  const char* buttons[4]={"CC_GraphicsLow","CC_GraphicsMedium","CC_GraphicsHigh","CC_GraphicsUltra"};
  int selected=(graphics_running_v26+1)%4;void* t=find_child(graphics_panel_v24(),buttons[selected]);
  void* button=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("Button"),0):0;
  if(button)graphics_button_v24(button);
  probe_ui[162]=graphics_selected_v24;probe_ui[163]=graphics_running_v26;probe_ui[164]=FN(0xa12bc0,int(*)(void*))(0);
  probe_ui[165]=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.Graphics.v24"),-1,0);
 }
 if(probe_command==32&&start){
  probe_command=0;void* text=(void*)probe_ui[150];
  if(text){
   score_outline_tmp_force_v21(text);
   void* mat=FN(0x23e790,void*(*)(void*,void*))(text,0);probe_ui[172]=(U64)mat;
   probe_ui[153]=mat?FN(0x9556c0,_Bool(*)(void*,void*,void*))(mat,str("OUTLINE_ON"),0):0;
   probe_ui[171]=mat?FN(0x955630,_Bool(*)(void*,void*,void*))(mat,str("_OutlineWidth"),0):0;
   void* shader=mat?FN(0x9565d0,void*(*)(void*,void*))(mat,0):0;
   probe_ui[170]=shader?(U64)FN(0xa0bdd0,void*(*)(void*,void*))(shader,0):0;
  }
 }
"""

debug += r"""
 if(probe_command>=40&&probe_command<=49&&start){
  int command=probe_command;probe_command=0;customization_close_v19();
  void* menu=menu_transform_v19();void* page=find_child(menu,"Pages/Settings");
  if(command==49){if(page)FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(page),0,0);return;}
  if(!page)return;
  if(command==40){
   FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(page),1,0);
   void* controller=FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(page),str("SettingsPageController"),0);
   if(controller)settings_refresh_v28_hook(controller,0);
  }else{
   const char* target=command==41?"CC_SettingsGame":command==42?"CC_SettingsGraphics":command==43?"CC_SettingsAudio":command==44?"CC_AudioControls/CC_VolumeMusicMinus":command==45?"CC_AudioControls/CC_VolumeMasterMinus":command==46?"CC_AudioControls/CC_VolumeMusicPlus":command==47?"CC_AudioControls/CC_VolumeMasterPlus":"Music Button";
   int slot=140+(command-40)*12;void* t=find_child(page,target);if(!t)return;V3 center=position(t);
   typedef struct{V3 o,d;} TestRaySettings;TestRaySettings ray={{center.x,center.y,-8.4f},{0,0,1}};
   void* caster=FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(menu),str("CurvedUIRaycaster"),0);
   void* hits=caster?FN(0x27c4a0,void*(*)(void*,TestRaySettings,void*))(caster,ray,0):0;
   int count=hits?INT(hits,0x18):0;void* arr=hits?PTR(hits,0x10):0;void* first=count&&arr?PTR(arr,0x20):0;
   probe_ui[slot]=count;probe_ui[slot+1]=first==gameobject(t);probe_ui[slot+2]=settings_tab_v28;probe_ui[slot+3]=audio_levels_v28[1];probe_ui[slot+4]=audio_levels_v28[0];
   if(first){void* button=FN(0x94f410,void*(*)(void*,void*,void*))(first,str("Button"),0);if(button){
    void* domain=FN(0x14a920,void*(*)(void))();void* asm_=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.UI");
    void* img=FN(0x14a530,void*(*)(void*))(asm_);void* cls=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(img,"UnityEngine.EventSystems","PointerEventData");
    void* ev=FN(0x1c22e0,void*(*)(void*))(cls);FN(0x471c70,void(*)(void*,void*,void*))(ev,0,0);FN(0x472090,void(*)(void*,int,void*))(ev,0,0);FN(0x461da0,void(*)(void*,void*,void*))(button,ev,0);probe_ui[slot+5]=1;
   }}
   probe_ui[slot+6]=settings_tab_v28;probe_ui[slot+7]=audio_levels_v28[1];probe_ui[slot+8]=audio_levels_v28[0];
   void* system=rooted(audio_system_v28);void* source=system?PTR(system,0x58):0;
   if(source){probe_ui[slot+9]=(U64)(FN(0xebc290,float(*)(void*,void*))(source,0)*10000);probe_ui[slot+10]=FN(0xebc0d0,_Bool(*)(void*,void*))(source,0);void* clip=FN(0xebc090,void*(*)(void*,void*))(source,0);probe_ui[slot+11]=0;if(clip){void* name=FN(0xa0bdd0,void*(*)(void*,void*))(clip,0);probe_ui[248]=text_equals(name,"Cloudcourt Lofi Playlist");probe_ui[249]=(U64)(FN(0xebaa80,float(*)(void*,void*))(clip,0)*1000);probe_ui[250]=FN(0xebc110,_Bool(*)(void*,void*))(source,0);probe_ui[251]=FN(0xebaa00,int(*)(void*,void*))(clip,0);probe_ui[252]=FN(0xebaa40,int(*)(void*,void*))(clip,0);}}
  }
 }
"""

source = source.replace(' probe_ticks++;', debug + '\n probe_ticks++;')
(F / 'mode_2v2.c').write_text(source)
builder = (R / 'build_patch.py').read_text()
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
    put(10)
    for _ in range(80):
        snapshot=struct.unpack('<256Q',read(base+ex['probe_ui'],2048))
        if snapshot[9]:break
        time.sleep(.1)
    assert snapshot[9], 'Main-thread probe was not initialized'
    rows=[]
    def snapshot():return struct.unpack('<256Q',read(base+ex['probe_ui'],2048))
    def stats():return list(struct.unpack('<12i',read(base+ex['customization_stats_v28'],48)))
    for visit in range(2):
        if visit:put(20);time.sleep(1)
        put(11);time.sleep(1)
        before=shot.with_name('v28-'+args.tag+'-visit'+str(visit)+'-before.png');shutil.copyfile(shot,before)
        clicks=[]
        for command in range(12,17):
            put(command);time.sleep(.35)
            q=snapshot();slot=16+(command-12)*12;clicks.append(dict(command=command,result=list(q[slot:slot+12])))
        put(21);time.sleep(.3);state=stats()
        put(11);time.sleep(1)
        after=shot.with_name('v28-'+args.tag+'-visit'+str(visit)+'-after.png');shutil.copyfile(shot,after)
        put(17);time.sleep(.35);q=snapshot();done=list(q[76:88])
        rows.append(dict(visit=visit,before=str(before),after=str(after),clicks=clicks,stats=state,done=done))
    settings=[]
    put(40);time.sleep(.5)
    for command in range(41,49):
        put(command);time.sleep(.4);q=snapshot();slot=140+(command-40)*12;a=list(q[slot:slot+12])
        name=read(a[11]+0x14,struct.unpack('<i',read(a[11]+0x10,4))[0]*2).decode('utf-16-le') if a[11] else None
        settings.append(dict(command=command,result=a,playlist=list(q[248:253])))
        if command in [41,42,43]:
            put(11);time.sleep(.7);shutil.copyfile(shot,shot.with_name('v28-'+args.tag+'-settings-'+str(command)+'.png'))
    put(49);time.sleep(.5);put(11);time.sleep(.7);shutil.copyfile(shot,shot.with_name('v28-'+args.tag+'-start.png'))
    result=dict(passed=False,settings=settings,visits=rows,working_or_live_modified=False,preferences_restored=True,real_menu_hook_between_visits=True,headset_or_two_pc_test=False)
    output=R/('analysis/v28-customization-unity-'+args.tag+'.json')
    output.write_text(json.dumps(result,indent=2))
    for row in rows:
        assert row['stats'][4]==255,'All eight graphical preview material instances must bind'
        for click in row['clicks']:
            a=click['result'];assert a[0] and a[1] and a[5] and a[6],('actual raycast/click failed',click)
            if click['command']==12:assert a[7]%9==(a[3]%9+1)%9
            if click['command']==13:assert a[7]//9==(a[3]//9+1)%9
            if click['command']==14:assert a[8]==(a[4]+1)%6
            if click['command']==15:assert a[10]==(a[9]+1)%8
        done=row['done'];assert done[1] and done[5] and not done[6],('Done did not close actual panel',done)
    for item in settings:
        assert item['result'][1] and item['result'][5],('Settings real hit/click failed',item)
    assert all(t['playlist']==[1,233789,1,1,22050] for t in settings),settings
    assert settings[-1]['result'][10]==1,'Music source is not playing'
    result['passed']=True;output.write_text(json.dumps(result,indent=2));print(json.dumps(dict(passed=True,visits=len(rows),settings_clicks=len(settings),playlist=settings[-1]['playlist'],audio_playing=True)))

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


