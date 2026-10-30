"""Targeted production C tests: native haptic ABI and in-match settings."""
from pathlib import Path
import ctypes,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parent;D=R/'tools/v30-runtime-tests';D.mkdir(parents=True,exist_ok=True)
def build(source,name):
 p=D/(name+'.c');p.write_text(source,encoding='utf8')
 env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str(R/'tools/zig-cache-v17'),ZIG_LOCAL_CACHE_DIR=str(R/'tools/zig-cache-v17'))
 c=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib','-Wl,--entry=DllMain','-target','x86_64-windows-msvc',str(p),'-o',str(D/(name+'.dll'))],capture_output=True,text=True,env=env)
 assert c.returncode==0,c.stderr
 return ctypes.CDLL(str(D/(name+'.dll')))
s=(R/'test_hit_feedback_v29_harness.c').read_text(encoding='utf-8-sig').replace('#include "hit_feedback_v29.c"','#include "../../hit_feedback_v29.c"')
s=s.replace('static void generic_dispatch(int slot,void*type,void*controller,int effect){generic++;if(slot!=17||effect!=1)backend=9;}','static int got_slot,got_effect;static void* got_type;static void* got_controller;static void generic_dispatch(int slot,void*type,void*controller,int effect){generic++;got_slot=slot;got_effect=effect;got_type=type;got_controller=controller;}')
s+='\nEXPORT int exact(int slot,int effect,int which){got_slot=got_effect=-999;got_type=got_controller=0;hit_haptic_dispatch_v29(slot,part_,controllers_[which],effect);return got_slot==slot&&got_effect==effect&&got_type==part_&&got_controller==controllers_[which];}\n'
h=build(s,'haptics');h.reset();h.exact.argtypes=[ctypes.c_int]*3
for side in range(3):
 for slot,effect in [(17,1),(17,0),(2,5),(0,-1)]:assert h.exact(slot,effect,side)==1
assert h.value(3)==12 and h.value(4)==0 and h.value(5)==0,'Native haptics replaced with custom coroutine'
s=(R/'test_settings_audio_v28_harness.c').read_text(encoding='utf-8-sig').replace('page_[64]','page_[256],menu_[64],ingame_[64]')
s=s.replace('static void* find_child(void*p,const char*s){return (void*)s;}','static void* find_child(void*p,const char*s){return eq(s,"Pages/Settings")?page_:eq(s,"Pages/InGame")?ingame_:(void*)s;}\nstatic void* menu_transform_v19(void){return menu_;}\nstatic void customization_close_v19(void){}\nstatic void refinement_close_v29(void){}\nstatic void refinement_tick_v29(void){}\nstatic void* hit_feedback_clip_v29(void*clip,void*e){return clip;}')
s=s.replace('static void* resolve(const char*s){','static void sibling(void*t){}\nstatic void* resolve(const char*s){if(eq(s,"UnityEngine.Transform::SetAsLastSibling"))return sibling;')
s=s.replace('static void active(void*s,_Bool b,void*m){}','static int settings_visible;static void active(void*s,_Bool b,void*m){if(s==page_)settings_visible=b;}\nstatic _Bool is_active(void*s,void*m){return s==ingame_?1:settings_visible;}\nstatic void* get_component(void*s,void*n,void*m){return s==page_?page_:0;}')
s=s.replace('case 0x94f700:return active;','case 0x94f700:return active;case 0x94f9a0:return is_active;case 0x94f410:return get_component;')
s=s.replace('#include "settings_audio_v28.c"','#include "../../settings_audio_v28.c"')
s+='\nEXPORT int match_state(int i){return i==0?settings_in_match_v30:i==1?settings_visible:settings_tab_v28;}\nEXPORT void match_back(void){PTR(page_,0x78)=(void*)"Native Back";settings_button_v28(PTR(page_,0x78));}\nEXPORT void menu_cleanup(void){settings_close_v28();}\n'
a=build(s,'settings');a.press.argtypes=[ctypes.c_char_p];a.level.restype=ctypes.c_float
a.reset(-999,-999,-999,-999);a.start();assert a.press(b'CC_SettingsAudio')==1
assert a.press(b'CC_MatchSettings')==1 and a.match_state(0)==1 and a.match_state(1)==1 and a.match_state(2)==0
assert a.press(b'CC_SettingsAudio')==1 and a.match_state(2)==2
a.press(b'CC_VolumeMusicMinus');assert a.value(1)==55 and abs(a.level(0)-.55)<1e-5
assert a.press(b'CC_SettingsGraphics')==1 and a.match_state(2)==2
a.match_back();assert a.match_state(0)==0 and a.match_state(1)==0 and a.match_state(2)==2
a.press(b'CC_MatchSettings');a.menu_cleanup();assert a.match_state(0)==0 and a.match_state(1)==0
report=dict(passed=True,native_haptic_argument_cases=12,custom_haptic_coroutines=0,match_settings_open_audio_controls_graphics_guard_back_cleanup=True,physical_headset_tested=False,sources={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['hit_feedback_v29.c','settings_audio_v28.c','match_settings_v30.c']})
(R/'analysis/v30-haptics-settings-tests.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
