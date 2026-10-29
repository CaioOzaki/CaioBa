"""Execute production settings/audio native code and inspect authored audio/menu."""
from pathlib import Path
import ctypes,sys,subprocess,os,json,hashlib,wave,struct
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np,UnityPy
from build_menu_v19 import MenuEditor,BUTTON,IMAGE,TEXT,button_layout
D=R/'tools/audio-v28';D.mkdir(exist_ok=True)
s=(R/'test_settings_audio_v28_harness.c').read_text(encoding='utf-8-sig').replace('#include "settings_audio_v28.c"','#include "../../settings_audio_v28.c"');(D/'harness.c').write_text(s,encoding='utf-8')
env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str(R/'tools/zig-cache-v17'),ZIG_LOCAL_CACHE_DIR=str(R/'tools/zig-cache-v17'))
c=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(D/'harness.c'),'-o',str(D/'harness.dll'),'-Wl,--entry=DllMain'],capture_output=True,text=True,env=env)
assert c.returncode==0,c.stderr
n=ctypes.CDLL(str(D/'harness.dll'));n.press.argtypes=[ctypes.c_char_p];n.level.restype=ctypes.c_float
n.reset(-999,-999,-999,-999);n.start();assert [n.value(i) for i in range(4)]==[100,65,100,80];assert abs(n.level(0)-.65)<1e-5
warm_roots=n.value(9)
for i in range(100):n.tick()
assert n.value(9)==warm_roots,"idle audio allocated handles"
assert n.value(4)==1 and n.value(6)==1,'idle audio restarted or allocated again'
n.stop_request();assert n.value(4)==1,'scene music stop request restarted playlist'
n.set_music(0);assert n.level(0)==0;n.set_music(1);assert abs(n.level(0)-.65)<1e-5
for key,i in [('Master',0),('Music',1),('Game',2),('UI',3)]:
 for _ in range(12):assert n.press(('CC_Volume'+key+'Minus').encode())==1
 assert n.value(i)==0
 for _ in range(13):n.press(('CC_Volume'+key+'Plus').encode())
 assert n.value(i)==100
assert n.press(b'Unknown')==0
for i,key in enumerate(['Game','Graphics','Audio']):assert n.press(('CC_Settings'+key).encode())==1 and n.value(8)==i
n.reset(-3,150,50,0);n.start();assert [n.value(i) for i in range(4)]==[0,100,50,0]
n.effect_play();assert abs(n.level(2)-.4)<1e-5
n.press(b'CC_VolumeGamePlus');assert abs(n.level(2)-.48)<1e-5 and abs(n.level(4)-.192)<1e-5
n.press(b'CC_VolumeUIPlus');assert abs(n.level(3)-.055)<1e-5
n.rebind();assert n.value(4)==2
f=UnityPy.load(str(R/'visuals-v28/level0')).file;e=MenuEditor(f);buttons=0
for path,tid in e.paths()[2].items():
 if not path.startswith('Menu/Pages/Settings/'):continue
 button=e.component(tid,BUTTON)
 if button and '/CC_' in path:
  raw=button.get_raw_data();_,ev=button_layout(raw);assert struct.unpack_from('<I',raw,ev)[0]==0
  t=f.objects[tid].read_typetree();x,y=t['m_AnchoredPosition'].values();w,h=t['m_SizeDelta'].values();assert -400<=x-w/2<x+w/2<=400 and -200<=y-h/2<y+h/2<=200
  assert e.component(tid,IMAGE).get_raw_data()[60]==1;buttons+=1
for p in ['CC_SettingsGame','CC_SettingsGraphics','CC_SettingsAudio','CC_AudioControls']:assert e.find('Menu/Pages/Settings/'+p)
tracks=json.loads((R/'assets/cloudcourt-v28/lofi-playlist.json').read_text());audio=[]
for t in tracks:
 p=R/'assets/cloudcourt-v28'/t['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==t['sha256']
 with wave.open(str(p),'rb') as w:
  assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,22050);data=np.frombuffer(w.readframes(w.getnframes()),'<i2')/32768.
 assert max(abs(data))<=.481 and len(data)>22050*70 and abs(data[0])<1e-4 and abs(data[-1])<1e-4
 assert np.sqrt(np.mean(data**2))>.04
 audio.append(dict(title=t['title'],peak=float(max(abs(data))),rms=float(np.sqrt(np.mean(data**2))),seconds=len(data)/22050))
assert len(tracks)==3
r=dict(passed=True,production_source_sha256=hashlib.sha256((R/'settings_audio_v28.c').read_bytes()).hexdigest(),native_preferences_clamps_categories_music_enable_loop_and_scene_rebind=True,live_game_ui_whistle_volumes=True,settings_custom_buttons=buttons,playlist=audio,no_external_audio_samples=True,headset_tested=False)
(R/'analysis/v28-settings-audio-tests.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))
