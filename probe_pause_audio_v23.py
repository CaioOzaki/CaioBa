"""Disposable Unity runtime probe for real pause-menu Button clicks and audio state."""
from pathlib import Path
import argparse, ctypes, json, os, shutil, struct, subprocess, sys, time, winreg
R=Path(__file__).resolve().parent
B=R/'versions/cloudcourt-v22-antes-v23'
F=R/'tools/p23'; W=F/'working'
p=argparse.ArgumentParser(); p.add_argument('--prepare-only',action='store_true'); p.add_argument('--skip-build',action='store_true'); p.add_argument('--tag',default='baseline'); p.add_argument('--fixed',action='store_true')
args=p.parse_args()
for d in (F,W,F/'tools',F/'backup',F/'analysis'):d.mkdir(parents=True,exist_ok=True)
for old in (R/'tools/u22-ui/working').rglob('*'):
    new=W/old.relative_to(R/'tools/u22-ui/working')
    if old.is_dir():new.mkdir(parents=True,exist_ok=True)
    elif not new.exists() and old.suffix!='.tmp':shutil.copyfile(old,new)
for old in B.iterdir():
    if old.is_file() and (old.suffix in ('.assets','.resource') or old.name.startswith('level')):shutil.copyfile(old,W/'VolleyballFever_Data'/old.name)
for old in (B/'fontes').glob('*.c'):shutil.copyfile(old,F/old.name)
if args.fixed:shutil.copyfile(R/'input_v19.c',F/'input_v19.c')
shutil.copyfile(R/'backup/GameAssembly.dll',F/'backup/GameAssembly.dll')
source=(F/'mode_2v2.c').read_text()
source=source.replace('#include "identity_v16.c"','EXPORT U64 audio_probe[2048];\nstatic unsigned audio_page;\n#include "identity_v16.c"')
identity=(F/'identity_v16.c').read_text().replace('EXPORT void in_game_active_hook(void* page,void* arg,void* m){','EXPORT void in_game_active_hook(void* page,void* arg,void* m){\n root_set(&audio_page,page);')
(F/'identity_v16.c').write_text(identity)
inp=(F/'input_v19.c').read_text().replace('static void ui_click_v19(void* button){','static void ui_click_v19(void* button){\n audio_probe[1]++;')
inp=inp.replace('FN(0xebbe30,void(*)(void*,void*))(source,0);','FN(0xebbe30,void(*)(void*,void*))(source,0); audio_probe[2]++;')
(F/'input_v19.c').write_text(inp)
debug=r'''
static int audio_capture,audio_frame;
static void audio_pointer_click(void* button){
 void* domain=FN(0x14a920,void*(*)(void))();void* asm_=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.UI");
 void* img=FN(0x14a530,void*(*)(void*))(asm_);void* cls=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(img,"UnityEngine.EventSystems","PointerEventData");
 void* ev=FN(0x1c22e0,void*(*)(void*))(cls);FN(0x471c70,void(*)(void*,void*,void*))(ev,0,0);
 FN(0x472090,void(*)(void*,int,void*))(ev,0,0);FN(0x461da0,void(*)(void*,void*,void*))(button,ev,0);
}
static void audio_sample(void){
 void* page=rooted(audio_page),*s=rooted(ui_v19_click_source);
 audio_probe[0]=(U64)page;audio_probe[3]=(U64)s;
 if(audio_capture&&audio_frame<200){
  U64* row=audio_probe+32+audio_frame*10;row[0]=audio_frame;row[1]=audio_probe[1];row[2]=audio_probe[2];
  float scale=FN(0xb72a80,float(*)(void*))(0);*(float*)(row+3)=scale;
  row[4]=FN(0xebacc0,_Bool(*)(void*))(0);
  row[5]=s?FN(0xebc0d0,_Bool(*)(void*,void*))(s,0):0;
  row[6]=s?FN(0xebc1d0,int(*)(void*,void*))(s,0):0;
  float pitch=s?FN(0xebbc80,float(*)(void*,void*))(s,0):0;*(float*)(row+7)=pitch;
  row[8]=s?FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(s),0):0;
  float volume=s?FN(0xebc290,float(*)(void*,void*))(s,0):0;*(float*)(row+9)=volume;
  audio_frame++;audio_probe[4]=audio_frame;
 }
}
static void audio_command(int c){
 void* page=rooted(audio_page);if(!page)return;
 if(c==20){FN(0x314a70,void(*)(void*,void*))(page,0);FN(0x314860,void(*)(void*,void*))(page,0);return;}
 if(c==25){
  typedef void(*SetPause)(_Bool);SetPause setpause=(SetPause)FN(0x14b030,void*(*)(const char*))("UnityEngine.AudioListener::set_pause");
  if(setpause){setpause(1);audio_probe[12]=1;}return;
 }
 if(c>=21&&c<=24){
  void* button=PTR(page,c==24?0x38:0x30);audio_probe[5]=(U64)button;
  audio_probe[6]=ui_button_valid_v19(button);
  if(c==23)FN(0x83de80,void(*)(void*,_Bool,void*))(button,0,0);
  audio_frame=0;audio_capture=1;
  audio_pointer_click(button);
  audio_sample();
  if(c==23)FN(0x83de80,void(*)(void*,_Bool,void*))(button,1,0);
  return;
 }
}
'''
source=source.replace('static void probe(void* start){',debug+'\nstatic void probe(void* start){\n if(probe_command==18&&start){probe_command=0;audio_frame=0;audio_capture=1;audio_pointer_click(PTR(start,0x38));}\n if(probe_command>=20){int c=probe_command;probe_command=0;audio_command(c);}\n audio_sample();')
source+='\n#ifdef MODE_PROBE\nTRAMP(void,probe_ingame,(void* o,void* m))\nEXPORT void probe_ingame_hook(void* o,void* m){probe_ingame_trampoline(o,m);probe(0);}\n#endif\n'
(F/'mode_2v2.c').write_text(source)
builder=(B/'fontes/build_patch.py').read_text().replace("sys.path.insert(0,str(R/'tools/python'))","sys.path.insert(0,"+repr(str(R/'tools/python'))+")\nsys.path.insert(0,"+repr(str(R))+")")
builder=builder.replace("entries += [('landing_collision'","entries += [('probe_ingame',0x314ad0)]\nentries += [('landing_collision'")
(F/'build_patch.py').write_text(builder)
if args.prepare_only:print('Prepared',F);sys.exit(0)
if not args.skip_build:
    env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str(R/'tools/zig-cache-p23'),ZIG_LOCAL_CACHE_DIR=str(R/'tools/zig-cache-p23'))
    cp=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib','-DMODE_PROBE','-DPATCH_DELTA=0x194f000',str(F/'spin_mod.c'),'-o',str(F/'tools/spin-native.dll'),'-Wl,--entry=DllMain'],env=env,capture_output=True,text=True)
    if cp.returncode:raise RuntimeError(cp.stderr)
    cp=subprocess.run([sys.executable,str(F/'build_patch.py')],capture_output=True,text=True)
    if cp.returncode:raise RuntimeError(cp.stderr)
ex=json.loads((F/'analysis/native-patch-manifest.json').read_text())['exports']
k=ctypes.WinDLL('kernel32',use_last_error=True);ps=ctypes.WinDLL('psapi',use_last_error=True)
k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p
k.ReadProcessMemory.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)];k.WriteProcessMemory.argtypes=k.ReadProcessMemory.argtypes;k.CloseHandle.argtypes=[ctypes.c_void_p]
ps.EnumProcessModulesEx.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong,ctypes.POINTER(ctypes.c_ulong),ctypes.c_ulong];ps.GetModuleFileNameExW.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_ulong]
prefs_path=r'Software\Neuston\Volleyball Fever'
def pref_values():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,prefs_path) as key:return {winreg.EnumValue(key,i)[0]:winreg.EnumValue(key,i)[1:] for i in range(winreg.QueryInfoKey(key)[1])}
    except FileNotFoundError:return {}
saved=pref_values(); info=subprocess.STARTUPINFO();info.dwFlags|=subprocess.STARTF_USESHOWWINDOW;info.wShowWindow=0
proc=subprocess.Popen([str(W/'VolleyballFever.exe'),'-batchmode','-force-d3d11','-vrmode','none','-screen-width','640','-screen-height','480','-screen-fullscreen','0','-logFile',str(F/'analysis'/('unity-'+args.tag+'.log'))],cwd=W,startupinfo=info)
h=k.OpenProcess(0x438,False,proc.pid);base=0
def read(addr,n):
    b=ctypes.create_string_buffer(n);count=ctypes.c_size_t()
    if not k.ReadProcessMemory(h,addr,b,n,ctypes.byref(count)):raise ctypes.WinError(ctypes.get_last_error())
    return b.raw
def vals():return struct.unpack('<2048Q',read(base+ex['audio_probe'],2048*8))
def put(c):
    v=ctypes.c_int(c);n=ctypes.c_size_t()
    if not k.WriteProcessMemory(h,base+ex['probe_command'],ctypes.byref(v),4,ctypes.byref(n)):raise ctypes.WinError(ctypes.get_last_error())
    for _ in range(100):
        if not struct.unpack('<i',read(base+ex['probe_command'],4))[0]:return
        if proc.poll() is not None:raise RuntimeError(('Unity exited',proc.returncode))
        time.sleep(.1)
    raise RuntimeError(('Command timed out',c))
def snapshot():
    v=vals();rows=[]
    for i in range(min(v[4],200)):
        row=v[32+i*10:42+i*10]
        f=lambda j:struct.unpack('<f',struct.pack('<Q',row[j])[:4])[0]
        rows.append(dict(frame=row[0],clicks=row[1],plays=row[2],timeScale=f(3),listenerPause=bool(row[4]),isPlaying=bool(row[5]),timeSamples=row[6],pitch=f(7),sourceOwnerActive=bool(row[8]),volume=f(9)))
    return dict(page=hex(v[0]),source=hex(v[3]),clicks=v[1],plays=v[2],buttonValid=bool(v[6]),rows=rows,listenerSetterResolved=bool(v[12]))
try:
    for _ in range(200):
        if proc.poll() is not None:raise RuntimeError(('Unity exited',proc.returncode))
        modules=(ctypes.c_void_p*512)();n=ctypes.c_ulong()
        if ps.EnumProcessModulesEx(h,modules,ctypes.sizeof(modules),ctypes.byref(n),3):
            for m in modules[:min(n.value//8,512)]:
                path=ctypes.create_unicode_buffer(4096);ps.GetModuleFileNameExW(h,m,path,4096)
                if path.value.endswith('GameAssembly.dll'):base=m;break
        if base and struct.unpack('<i',read(base+ex['probe_ticks'],4))[0]:break
        time.sleep(.1)
    put(18);time.sleep(.3);mainmenu=snapshot();time.sleep(.7);put(2)
    for _ in range(200):
        if vals()[0]:break
        time.sleep(.1)
    assert vals()[0],'Match never activated'
    time.sleep(2)
    results={'mainmenu_solo':mainmenu}
    for name,c in [('resume',21),('disabled_resume',23),('listener_paused_resume',21),('leave',24)]:
        put(20);time.sleep(.3)
        if name=='listener_paused_resume':put(25)
        put(c);time.sleep(.3);results[name]=snapshot()
    main,resume,disabled,paused,leave=[results[n] for n in ('mainmenu_solo','resume','disabled_resume','listener_paused_resume','leave')]
    assert main['source']==resume['source']==paused['source']==leave['source']
    assert resume['plays']==main['plays']+1==disabled['plays']
    assert paused['plays']==resume['plays']+1 and leave['plays']==paused['plays']+1
    assert paused['listenerSetterResolved'] and all(r['listenerPause'] for r in paused['rows']+leave['rows'])
    assert all(r['timeScale']==0 for r in leave['rows'])
    assert all(r['pitch']==1 and r['sourceOwnerActive'] for r in paused['rows']+leave['rows'])
    assert (max(r['timeSamples'] for r in paused['rows'])>0)==args.fixed
    assert (max(r['timeSamples'] for r in leave['rows'])>0)==args.fixed
    out=dict(passed=True,tag=args.tag,results=results,unity_Button_OnPointerClick=True,only_disposable_copy_modified=True,preferences_restored=True,hardware_VR_tested=False)
    (R/'analysis'/('v23-pause-audio-unity-'+args.tag+'.json')).write_text(json.dumps(out,indent=2));print(json.dumps({k:{x:y for x,y in v.items() if x!='rows'} for k,v in results.items()},indent=2))
finally:
    if proc.poll() is None:proc.terminate()
    proc.wait(timeout=10);k.CloseHandle(h)
    now=pref_values()
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER,prefs_path) as key:
        for name in now.keys()-saved.keys():winreg.DeleteValue(key,name)
        for name,(value,kind) in saved.items():winreg.SetValueEx(key,name,0,kind,value)
    assert pref_values()==saved

