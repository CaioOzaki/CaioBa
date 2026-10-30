"""Native desktop launch regression in an owned disposable Unity copy.
Run: python probe_launch_v30.py --fixed --all
Uses actual native Button.OnPointerClick dispatch for Solo, Training, Extras,
drills, Leave, and in-match Settings. Records native Fade alpha, real rules,
players, bot counts, pause ownership and source hashes. No test camera or state
forcing is used. Does not establish physical headset or two-PC validation.
Never writes the Steam installation or another process; closes only its own
child process and restores registry preferences after the session.
"""
from pathlib import Path
import sys,os,shutil,subprocess,json,ctypes,struct,time,winreg,argparse,hashlib
R=Path(__file__).resolve().parent
a=argparse.ArgumentParser();a.add_argument('--fixed',action='store_true');a.add_argument('--case',default='serve');a.add_argument('--reuse',action='store_true');a.add_argument('--all',action='store_true');a.add_argument('--diagnose',action='store_true');a.add_argument('--bombs',action='store_true');args=a.parse_args()
F=R/'tools/u30-launch';W=F/'working';B=R/'versions/cloudcourt-v29-antes-v30';src=R if args.fixed else B/'fontes'
if args.fixed:B=R/'visuals-v30'
for d in [F,W,F/'backup',F/'analysis',F/'tools']:d.mkdir(parents=True,exist_ok=True)
if not (W/'VolleyballFever.exe').exists():shutil.copytree(R/'working',W,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.tmp'))
for p in B.iterdir():
 if p.is_file() and (p.suffix in ('.assets','.resource') or p.name.startswith('level')):shutil.copyfile(p,W/'VolleyballFever_Data'/p.name)
for p in src.glob('*.c'):shutil.copyfile(p,F/p.name)
if args.fixed:
 sys.path[:0]=[str(R/'tools/python'),str(R)];import UnityPy
 from build_launch_ui_v30 import apply_launch_ui_v30
 e=UnityPy.load(str(W/'VolleyballFever_Data/level0'));apply_launch_ui_v30(e.file);(W/'VolleyballFever_Data/level0').write_bytes(e.file.save())
shutil.copyfile(R/'backup/GameAssembly.dll',F/'backup/GameAssembly.dll')
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in F.glob('*.c')}
s=(F/'mode_2v2.c').read_text(encoding='utf-8-sig')
s=s[:s.index('#ifdef MODE_PROBE')]+'''#ifdef MODE_PROBE
TRAMP(void,probe_start,(void* o,void* m))
TRAMP(void,probe_solo,(void* o,void* m))
EXPORT int probe_command,probe_ticks,probe_page_ready;
EXPORT U64 probe_ui[128];
static unsigned probe_start_saved;
static void probe(void* start){if(start)root_set(&probe_start_saved,start);probe_ticks++;}
EXPORT void probe_start_hook(void* o,void* m){probe_start_trampoline(o,m);probe(o);}
EXPORT void probe_solo_hook(void* o,void* m){probe_solo_trampoline(o,m);probe(0);}
#endif
'''
# Observe all lifecycle changes, execute real pointer button dispatch from the permanent AudioSystem Update.
persistent=r'''
static void probe_ray_v30(void* b){
 void* menu=menu_transform_v19();V3 center=position(transform(b));V3 forward=FN(0xb748d0,GetVec)(menu,0);
 typedef struct{V3 o,d;} RayV30;RayV30 ray={sub(center,mul(forward,3)),forward};
 void* caster=FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(menu),str("CurvedUIRaycaster"),0);
 void* hits=caster?FN(0x27c4a0,void*(*)(void*,RayV30,void*))(caster,ray,0):0;
 int count=hits?INT(hits,0x18):0;void* a=hits?PTR(hits,0x10):0;void* first=count&&a?PTR(a,0x20):0;
 probe_ui[90]=count;probe_ui[91]=first==gameobject(b);probe_ui[92]=(U64)first;probe_ui[93]=(U64)gameobject(b);
}
static void probe_click_v30(void* b){
 probe_ui[30]=(U64)b;probe_ui[31]=ui_button_valid_v19(b);if(!b)return;probe_ray_v30(b);
 void* domain=FN(0x14a920,void*(*)(void))();void* a=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.UI");
 void* image=FN(0x14a530,void*(*)(void*))(a);void* cls=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine.EventSystems","PointerEventData");
 void* ev=FN(0x1c22e0,void*(*)(void*))(cls);FN(0x471c70,void(*)(void*,void*,void*))(ev,0,0);
 FN(0x472090,void(*)(void*,int,void*))(ev,0,0);FN(0x461da0,void(*)(void*,void*,void*))(b,ev,0);probe_ui[32]++;
}
static void probe_persistent_v30(void){
 void* page=rooted(page_root),*menu=menu_transform_v19();void* rules=rooted(rules_root);
 probe_ui[0]=probe_ticks;probe_ui[1]=solo_stage;probe_ui[2]=training_requested_v29();probe_ui[3]=training_active_v29();probe_ui[4]=training_drill_v29;probe_ui[5]=(U64)rules;probe_ui[6]=(U64)local_avatar_player();probe_ui[7]=offline();
 probe_ui[8]=rules?BYTE(rules,0x68):999;probe_ui[9]=doubles_enabled;probe_ui[10]=quartet_enabled;
 for(int i=0;i<5;i++){void* b=page?PTR(page,0x40+i*8):0;probe_ui[11+i]=b?FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(b),0):999;}
 void* cls=PTR((void*)base(),0x1542308),*stat=cls?PTR(cls,0xb8):0,*fade=stat?PTR(stat,0):0;
 probe_ui[16]=(U64)fade;
 if(fade){void* rr=PTR(fade,0x20);void* mat=rr?FN(0xa1ae90,void*(*)(void*,void*))(rr,0):0;if(mat){Q4 c=FN(0x9563e0,Q4(*)(void*,void*))(mat,0);probe_ui[17]=(U64)(c.w*10000);probe_ui[86]=(U64)(c.x*10000);probe_ui[87]=(U64)(c.y*10000);probe_ui[88]=(U64)(c.z*10000);}}
 void* teams=rules?PTR(rules,0x60):0;
 for(int i=0;i<2;i++){void* team=teams?PTR(teams,0x20+i*8):0,*bots=team?PTR(team,0x30):0;probe_ui[18+i]=bots?INT(bots,0x18):999;}
 probe_ui[20]=page?FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(page),0):999;
 void* st=rooted(probe_start_saved);probe_ui[21]=st?FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(st),0):999;
 probe_ui[22]=menu?FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(menu),0):999;
#ifdef PROBE_FIXED_V30
 void* settings=rooted(settings_page_v28),*it=menu?find_child(menu,"Pages/InGame"):0;
 probe_ui[40]=settings_in_match_v30;probe_ui[41]=settings_tab_v28;
 probe_ui[42]=settings?FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(settings),0):0;
 probe_ui[43]=it?FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(it),0):0;
 void* gr=settings?find_child(transform(settings),"CC_SettingsGraphics"):0;
 probe_ui[44]=gr?FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(gr),0):0;
 probe_ui[45]=(U64)(FN(0xb72a80,float(*)(void*))(0)*1000);
 for(int i=0;i<4;i++)probe_ui[46+i]=audio_levels_v28[i];
 void* audio=rooted(audio_system_v28),*primary=audio?PTR(audio,0x58):0,*secondary=audio?PTR(audio,0x60):0;
 probe_ui[50]=primary?(U64)(FN(0xebc290,float(*)(void*,void*))(primary,0)*10000):999;
 probe_ui[51]=secondary?(U64)(FN(0xebc290,float(*)(void*,void*))(secondary,0)*10000):999;
 probe_ui[52]=primary?FN(0xebc0d0,_Bool(*)(void*,void*))(primary,0):0;
 probe_ui[54]=(U64)rooted(audio_bound_clip_v28);probe_ui[53]=probe_ui[54]?(U64)(FN(0xebaa80,float(*)(void*,void*))((void*)probe_ui[54],0)*1000):0;probe_ui[57]=primary?(U64)(FN(0xebc210,float(*)(void*,void*))(primary,0)*1000):0;probe_ui[55]=FN(0xef33f0,_Bool(*)(void*))(0);
 probe_ui[56]=FN(0xef3230,_Bool(*)(void*))(0);
 void* task=page?PTR(page,0x28):0;probe_ui[60]=(U64)task;probe_ui[61]=task?INT(task,0x38):0;
 static unsigned debug_exception_string;
 if(task&&(INT(task,0x38)&0x200000)&&!rooted(debug_exception_string)){
  void* err=FN(0x402850,void*(*)(void*,void*))(task,0);
  if(err)root_set(&debug_exception_string,FN(0x3b3ae0,void*(*)(void*,void*))(err,0));
 }
 probe_ui[62]=(U64)rooted(debug_exception_string);
 probe_ui[70]=probe_ui[71]=0;
 for(int side=0;teams&&side<2;side++){
  void* team=PTR(teams,0x20+side*8),*list=team?PTR(team,0x18):0,*items=list?PTR(list,0x10):0;int n=list?INT(list,0x18):0;
  if(items&&n==4)for(int slot=0;slot<4;slot++){
   void* area=PTR(items,0x20+slot*8),*def=area?PTR(area,0x30):0;
   if(alive(area)&&alive(def))probe_ui[71]++;
   if(alive(area)&&alive(FN(0x26e8d0,void*(*)(void*,void*))(area,0)))probe_ui[70]++;
  }
 }
 void* local=local_avatar_player(),*area=local?PTR(local,0x20):0;
 probe_ui[72]=(U64)area;probe_ui[73]=alive(area)?(U64)FN(0x26e8d0,void*(*)(void*,void*))(area,0):0;probe_ui[74]=area?(U64)PTR(area,0x30):0;
 void* ball=v19_ball();probe_ui[76]=(U64)ball;
 if(alive(ball)){V3 pp=position(transform(ball)),vv=*(V3*)((char*)ball+0x8c);probe_ui[77]=(U64)((pp.x+100)*1000);probe_ui[78]=(U64)((pp.y+100)*1000);probe_ui[79]=(U64)((pp.z+100)*1000);probe_ui[80]=(U64)(dot(vv,vv)*1000);}

#endif
 int cmd=probe_command;if(!cmd)return;probe_command=0;
 if(cmd==23&&rules){probe_ui[94]=(U64)FN(0x253580,void*(*)(void*,int,void*))(rules,INT(rules,0x90),0);probe_ui[95]=BYTE(rules,0x79);probe_ui[96]=BYTE(rules,0x7a);return;}
#ifdef PROBE_FIXED_V30
 if(cmd>=30&&cmd<=37){
  void* target=0,*st=settings?transform(settings):0;
  if(cmd==30)target=it?find_child(it,"CC_MatchSettings"):0;
  if(cmd==31)target=st?find_child(st,"CC_SettingsAudio"):0;
  if(cmd==32)target=st?find_child(st,"CC_AudioControls/CC_VolumeMusicMinus"):0;
  if(cmd==33)target=st?find_child(st,"CC_AudioControls/CC_VolumeMusicPlus"):0;
  if(cmd==34)target=st?find_child(st,"CC_SettingsGame"):0;
  if(target)probe_click_v30(FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(target),str("Button"),0));
  if(settings&&cmd==35)probe_click_v30(PTR(settings,0x48));
  if(settings&&cmd==36)probe_click_v30(PTR(settings,0x78));
  if(settings&&cmd==37)probe_click_v30(PTR(settings,0x38));
  return;
 }
#endif
 if(cmd==1){if(st)probe_click_v30(PTR(st,0x38));return;}
 if(cmd>=2&&cmd<=6){if(page)probe_click_v30(PTR(page,0x40+(cmd-2)*8));return;}
 if(cmd>=11&&cmd<=14){void* p=refinement_panel_v29(0);const char* names[]={"CC_TrainServe","CC_TrainReceive","CC_TrainSet","CC_TrainSpike"};void* t=find_child(p,names[cmd-11]);if(t)probe_click_v30(FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("Button"),0));return;}
 if(cmd==20){void* t=find_child(menu,"Pages/InGame");void* c=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("InGamePageController"),0):0;probe_ui[33]=(U64)c;if(c)probe_click_v30(PTR(c,0x38));return;}
 if(cmd==21||cmd==22){void* t=find_child(menu,"Pages/InGame");void* c=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("InGamePageController"),0):0;if(c){if(cmd==22)FN(0x314a70,void(*)(void*,void*))(c,0);else probe_click_v30(PTR(c,0x30));}return;}
}
'''
s=s.replace('static unsigned page_root,day_text_root,night_text_root;','static unsigned page_root,day_text_root,night_text_root;\nstatic unsigned probe_start_saved;static void probe_persistent_v30(void);')
s=s.replace('static unsigned probe_start_saved;\nstatic void probe(void* start)', 'static void probe(void* start)')
# Need symbols declared before refinement include.
s=s.replace('#include "refinement_v29.c"','EXPORT extern int probe_command,probe_ticks;EXPORT extern U64 probe_ui[128];\n'+persistent+'\n#include "refinement_v29.c"')
s=s.replace('static void refinement_menu_v29(void);','static void refinement_menu_v29(void);\nstatic void* refinement_panel_v29(int);')
if args.diagnose:
 s=s.replace('EXPORT void spawn_bot_hook(void* o,void* prefab,int team,int slot,float yaw,void* m){','EXPORT void spawn_bot_hook(void* o,void* prefab,int team,int slot,float yaw,void* m){probe_ui[63]=1;probe_ui[64]=team;probe_ui[65]=slot;')
 s=s.replace(' bots_spawn_begin_v20(o,team,slot);',' probe_ui[63]=2;bots_spawn_begin_v20(o,team,slot);probe_ui[63]=3;')
 s=s.replace(' spawn_bot_trampoline(o,prefab,team,slot,yaw,m);',' spawn_bot_trampoline(o,prefab,team,slot,yaw,m);probe_ui[63]=4;')
 s=s.replace(' bots_spawn_end_v20();',' bots_spawn_end_v20();probe_ui[63]=5;')
 s=s.replace('static unsigned page_root,day_text_root,night_text_root;','EXPORT extern U64 probe_ui[128];\nstatic unsigned page_root,day_text_root,night_text_root;')
s='EXPORT extern U64 probe_ui[128];\n'+s
s=s.replace('EXPORT void bot_hit_hook(void* bot,void* ball,void* m){','EXPORT void bot_hit_hook(void* bot,void* ball,void* m){probe_ui[83]++;')
s=s.replace('EXPORT _Bool serve_routine_hook(void* routine,void* m){','EXPORT _Bool serve_routine_hook(void* routine,void* m){probe_ui[84]++;')
(F/'mode_2v2.c').write_text(s,encoding='utf8')
r=(F/'refinement_v29.c').read_text(encoding='utf-8-sig').replace('static void refinement_tick_v29(void){','static void refinement_tick_v29(void){probe_persistent_v30();')
(F/'refinement_v29.c').write_text(r,encoding='utf8')
b=(R/'build_patch.py').read_text();b=b.replace("sys.path.insert(0,str(R/'tools/python'))","sys.path.insert(0,"+repr(str(R/'tools/python'))+")\nsys.path.insert(0,"+repr(str(R))+")")
(F/'build_patch.py').write_text(b,encoding='utf8')
env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str(F/'zig-cache'),ZIG_LOCAL_CACHE_DIR=str(F/'zig-cache'))
cp=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib','-DMODE_PROBE',*(['-DPROBE_FIXED_V30'] if args.fixed else []),'-DPATCH_DELTA=0x194f000',str(F/'spin_mod.c'),'-o',str(F/'tools/spin-native.dll'),'-Wl,--entry=DllMain'],env=env,capture_output=True,text=True)
if cp.returncode:print(cp.stderr);sys.exit(cp.returncode)
cp=subprocess.run([sys.executable,str(F/'build_patch.py')],capture_output=True,text=True)
if cp.returncode:print(cp.stdout,cp.stderr);sys.exit(cp.returncode)
ex=json.loads((F/'analysis/native-patch-manifest.json').read_text())['exports']
k=ctypes.WinDLL('kernel32',use_last_error=True);ps=ctypes.WinDLL('psapi',use_last_error=True)
k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p
k.ReadProcessMemory.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)];k.WriteProcessMemory.argtypes=k.ReadProcessMemory.argtypes;k.CloseHandle.argtypes=[ctypes.c_void_p]
ps.EnumProcessModulesEx.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong,ctypes.POINTER(ctypes.c_ulong),ctypes.c_ulong];ps.GetModuleFileNameExW.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_ulong]
info=subprocess.STARTUPINFO();info.dwFlags|=subprocess.STARTF_USESHOWWINDOW;info.wShowWindow=0
log=F/'analysis'/('launch-'+('fixed-' if args.fixed else 'baseline-')+('all' if args.all else 'bombs' if args.bombs else args.case)+'.log')
prefs_path=r'Software\Neuston\Volleyball Fever'
def pref_values():
 try:
  with winreg.OpenKey(winreg.HKEY_CURRENT_USER,prefs_path) as key:return {winreg.EnumValue(key,i)[0]:winreg.EnumValue(key,i)[1:] for i in range(winreg.QueryInfoKey(key)[1])}
 except FileNotFoundError:return {}
saved_prefs=pref_values()
p=subprocess.Popen([str(W/'VolleyballFever.exe'),'-batchmode','-force-d3d11','-vrmode','none','-screen-width','1024','-screen-height','768','-screen-fullscreen','0','-logFile',str(log)],cwd=W,startupinfo=info)
h=k.OpenProcess(0x438,False,p.pid);base=0
rows=[];passed=False
def read(a,n):
 b=ctypes.create_string_buffer(n);cnt=ctypes.c_size_t();assert k.ReadProcessMemory(h,a,b,n,ctypes.byref(cnt));return b.raw
def snapshot():return list(struct.unpack('<128Q',read(base+ex['probe_ui'],1024)))
def put(n):
 d=ctypes.c_int(n);cnt=ctypes.c_size_t();assert k.WriteProcessMemory(h,base+ex['probe_command'],ctypes.byref(d),4,ctypes.byref(cnt))
def record(label,seconds=1):
 time.sleep(seconds);v=snapshot();rows.append(dict(label=label,state=v[:100]));print(label,v[:23],v[40:58],v[70:100],flush=True);return v
try:
 for i in range(600):
  if p.poll() is not None:raise RuntimeError(('Unity exited',p.returncode))
  mods=(ctypes.c_void_p*512)();need=ctypes.c_ulong()
  if ps.EnumProcessModulesEx(h,mods,ctypes.sizeof(mods),ctypes.byref(need),3):
   for mo in mods[:min(need.value//8,512)]:
    path=ctypes.create_unicode_buffer(4096);ps.GetModuleFileNameExW(h,mo,path,4096)
    if path.value.endswith('GameAssembly.dll'):base=mo;break
  if base and struct.unpack('<i',read(base+ex['probe_ticks'],4))[0]:break
  time.sleep(.1)
 record('startup',6)
 cases=['serve','receive','set','spike','bomb2','bomb4'] if args.all else ['bomb2','bomb4'] if args.bombs else [args.case]
 for case in cases:
  put(1);v=record(case+'-solo',.7)
  if args.fixed:assert v[1]==0 and v[11:15]==[1,1,1,1],('first-solo-layout',case,v[:23])
  if case in ['serve','receive','set','spike']:
   put(4);record(case+'-training',.25);put(11+['serve','receive','set','spike'].index(case))
  else:
   put(5);record(case+'-extras',.25);put(2 if case=='bomb4' else 3)
  record(case+'-fade-black',.3)
  v=record(case+'-ready',4)
  if args.fixed and not args.diagnose:
   for sample in range(12):
    if v[5] and v[6] and v[17]==0:break
    v=record(case+'-fade-settle'+str(sample),.25)
  if args.diagnose:
   print('DIAG',v[60:70],flush=True)
   if v[62]:
    ptr=v[62];length=struct.unpack('<i',read(ptr+16,4))[0];print('TASK_EXCEPTION',read(ptr+20,length*2).decode('utf16'),flush=True)
   break
  if args.fixed:
   assert v[5] and v[6] and v[17]==0,('native fade/rules/player',case,v[:23])
   if case in ['serve','receive','set','spike']:assert v[3]==1 and v[4]==1+['serve','receive','set','spike'].index(case) and v[18:20]==[0,0],('drill',case,v[:23])
   else:
    assert v[3]==0 and v[8]==1 and v[18:20]==([3,4] if case=='bomb4' else [1,2]),('bomb',case,v[:23])
    assert v[70:72]==[8,8] and all(v[72:75]),('native-human-placement',case,v[70:86])
    put(23);record(case+'-native-serving-player',.2);v=record(case+'-native-ball',4)
    assert v[76] and v[84],('native ball/serve flow missing',case,v[76:85])
   put(22);v=record(case+'-menu',.25);same_rules=v[5]
   if case=='bomb4':
    for visit in range(2):
     put(30);v=record('match-settings-open'+str(visit),.3);assert v[40:45]==[1,0,1,1,0] and v[5]==same_rules and v[45]==0,v[40:57]
     assert v[90] and v[91],('MatchSettings ray blocked',v[90:94])
     aim=v[56];put(35);v=record('game-option-change',.2);assert v[56]!=aim,v[40:57]
     put(35);v=record('game-option-restore',.2);assert v[56]==aim,v[40:57]
     put(31);v=record('sound-tab',.2);music=v[47];enabled=v[55]
     if not enabled:put(37);v=record('music-on',.3)
     assert v[52]==1 and 287400<=v[53]<=287600 and v[50]>0,('new-playlist-playback',v[40:58])
     previous_time=v[57];v=record('music-time-advances',.3);assert v[57]>previous_time,v[40:58]
     put(32);v=record('music-minus',.2);assert v[90] and v[91],('MusicMinus ray blocked',v[90:94]);assert v[47]==max(0,music-10) and abs(v[50]-v[47]*100)<=1,v[40:57]
     put(33);v=record('music-plus',.2);assert v[47]==music,v[40:57]
     put(37);v=record('native-mute',.2);assert v[55]==0 and v[50]==0,v[40:57]
     put(37);v=record('native-unmute',.2);assert v[55]==1 and abs(v[50]-v[47]*100)<=1,v[40:57]
     if not enabled:put(37);record('restore-original-music-toggle',.2)
     put(36);v=record('match-settings-back'+str(visit),.2);assert v[90] and v[91],('Back ray blocked',v[90:94]);assert v[40]==0 and v[42]==0 and v[43]==1 and v[45]==0 and v[5]==same_rules,v[40:57]
    put(21);v=record('native-resume',.3);assert v[45]==1000 and v[5]==same_rules,v[40:57]
    put(22);record('menu-before-leave',.2)
   put(20);v=record(case+'-native-leave',3)
   assert not v[3] and not v[5] and v[21]==1 and v[17]==0,('leave',case,v[:23])
 if args.fixed and not args.diagnose:
  put(1);record('final-solo-reenter',.7);put(4);record('final-training-reenter',.25);put(12);v=record('final-receive-reenter',4)
  assert v[17]==0 and v[3]==1 and v[4]==2,('reentry fade',v[:23])
 passed=not args.diagnose
 print('DIAGNOSTIC ONLY' if args.diagnose else 'PASS: native clicks all requested modes, fade lifecycle, leave/reentry and settings.',flush=True)

finally:
 (F/'analysis'/('launch-'+('fixed-' if args.fixed else 'baseline-')+('all' if args.all else 'bombs' if args.bombs else args.case)+'.json')).write_text(json.dumps(dict(passed=passed,sources=source_hashes,rows=rows,candidate_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in B.iterdir() if p.is_file()},scope='native desktop PointerEventData / Button.OnPointerClick; no VR headset or physical two-PC validation'),indent=2))
 if p.poll() is None:p.terminate()
 p.wait(timeout=15);k.CloseHandle(h)
 with winreg.CreateKey(winreg.HKEY_CURRENT_USER,prefs_path) as key:
  for name in set(pref_values())-set(saved_prefs):winreg.DeleteValue(key,name)
  for name,(value,kind) in saved_prefs.items():winreg.SetValueEx(key,name,0,kind,value)
 assert pref_values()==saved_prefs,'Preference restoration failed'
 print('Registry preferences restored.',flush=True)
