"""Replace every shipped AudioClip bank with CC0 effects and new synthesis.
No sound from the original game is sampled. FSB5 PCM16 is authored from WAV.
Format reference: https://github.com/HearthSim/python-fsb5/blob/master/FSB5.bt
"""
from pathlib import Path
import sys,json,struct,wave,io,hashlib,shutil
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import numpy as np,UnityPy,fmod_toolkit
A=R/'assets/audio-v18';A.mkdir(exist_ok=True);W=R/'working/VolleyballFever_Data';SR=22050
rng=np.random.default_rng(1818)
def tone(freq,dur=.5):
 t=np.arange(round(dur*SR))/SR;env=np.minimum(t/.007,1)*np.exp(-t*7/max(dur,.1))
 return (np.sin(2*np.pi*freq*t)+.24*np.sin(4*np.pi*freq*t))*env
def noise(dur):
 a=rng.normal(0,1,round(dur*SR));return np.convolve(a,np.ones(12)/12,'same')
def motif(notes,dur=.75):
 a=np.zeros(round(dur*SR));step=dur/(len(notes)+1)
 for i,f in enumerate(notes):
  b=tone(f,step*1.9);j=round(i*step*SR);k=min(len(b),len(a)-j);a[j:j+k]+=b[:k]
 return a
def ambience(night=False,birds=False):
 dur=16;t=np.arange(SR*dur)/SR;a=noise(dur)
 a*=.035+.05*(.5+.5*np.sin(2*np.pi*t/8))**2
 if birds:
  a*=.3
  for start in [1,4.2,9.3,12.1]:
   q=np.arange(int(SR*.45))/SR;b=np.sin(2*np.pi*(1150*q+450*q*q))*np.sin(np.pi*q/.45)**2*.16;j=int(start*SR);a[j:j+len(b)]+=b
 if night:a*=.65
 # An integer wave period with matching endpoints; fade derivative noise seam.
 fade=int(.2*SR);a[:fade]*=np.linspace(0,1,fade);a[-fade:]*=np.linspace(1,0,fade)
 return a
def music(stinger=False):
 beat=60/112;dur=8*beat if stinger else 64*beat;a=np.zeros(round(dur*SR))
 chords=[(261.63,329.63,392),(220,261.63,329.63),(174.61,220,261.63),(196,246.94,293.66)]
 for b in range(8 if stinger else 64):
  chord=chords[(b//4)%4]
  for f,gain in [(chord[b%3]*2,.13),(chord[0]/2,.14)]:
   q=tone(f,beat*.92)*gain;j=round(b*beat*SR);a[j:j+len(q)]+=q[:len(a)-j]
  if b%2==0:
   q=noise(.07)*np.exp(-np.arange(round(.07*SR))/SR*65)*.12;j=round(b*beat*SR);a[j:j+len(q)]+=q[:len(a)-j]
 return a
def kenney(pack,name):
 path=A/pack/'Audio'/name
 from fmod_toolkit.fmod import pyfmodex
 raw=path.read_bytes();system,lock=fmod_toolkit.get_pyfmodex_system_instance(2,pyfmodex.flags.INIT_FLAGS.NORMAL)
 with lock:
  sound=system.create_sound(raw,pyfmodex.flags.MODE.OPENMEMORY,exinfo=pyfmodex.structure_declarations.CREATESOUNDEXINFO(length=len(raw)))
  try:data=fmod_toolkit.subsound_to_wav(sound)
  finally:sound.release()
 with wave.open(io.BytesIO(data)) as f:
  assert f.getsampwidth()==2
  pcm=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float).reshape(-1,f.getnchannels()).mean(axis=1)/32768
  old=f.getframerate()
 return np.interp(np.arange(round(len(pcm)*SR/old))*old/SR,np.arange(len(pcm)),pcm)
def fsb(pcm,name):
 raw=np.asarray(pcm,'<i2').tobytes();raw+=bytes((-len(raw))%32)
 names=struct.pack('<I',4)+name.encode()+b'\0';names+=bytes((-len(names))%16)
 sample=(5<<1)|(len(pcm)<<34)
 header=struct.pack('<4s6I8s16s8s',b'FSB5',1,1,8,len(names),len(raw),2,bytes(8),hashlib.md5(raw).digest(),bytes(8))
 return header+struct.pack('<Q',sample)+names+raw
def write_wav(path,pcm):
 with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes(pcm.tobytes())
def main():
 inventory=json.loads((R/'analysis/v18-audio-inventory.json').read_text());report=[]
 for asset in sorted({e['asset'] for e in inventory}):
  file=UnityPy.load(str(W/asset)).file;bank=bytearray()
  for item in [e for e in inventory if e['asset']==asset]:
   old=item['info']['m_Name'];source='Cloudcourt original synthesis';key=f"{Path(asset).stem}-{item['id']}"
   if old.startswith('BallHit'):
    choice='impactSoft_medium_000.ogg' if old.endswith('01') else 'impactPunch_medium_002.ogg'
    a=kenney('impact',choice);source='Kenney Impact Sounds / '+choice+' (CC0)';peak=.65
   elif old=='Interface01':a=kenney('interface','click_003.ogg');source='Kenney Interface Sounds / click_003.ogg (CC0)';peak=.38
   elif old.startswith(('RedPoint','BluePoint')):
    a=motif([392,493.88,587.33] if old.startswith('Blue') else [440,554.37,659.25]);peak=.35
   elif old=='Music02':a=music();peak=.28
   elif old=='TeamPresentationStinger':a=music(True);peak=.36
   elif old.startswith('Ambience_'):a=ambience('Night' in old,'Seagulls' in old);peak=.17 if 'Seagulls' not in old else .12
   elif old=='Positive':a=motif([523.25,659.25,783.99,1046.5],1.15);peak=.36
   elif old=='Negative':a=motif([392,349.23,293.66],.85);peak=.32
   elif old=='Silence':a=np.zeros(round(.08*SR));peak=0
   elif old=='FuseTick':a=tone(880,.11);peak=.3
   elif old=='Fuse':a=motif([220,293.66,329.63,392],2);peak=.24
   elif old=='ReadyToExplode':a=motif([392,523.25,783.99],.9);peak=.32
   else:
    t=np.arange(SR)/SR;a=noise(1)*np.exp(-t*9)+.25*np.sin(2*np.pi*(75*t-20*t*t))*np.exp(-t*8);peak=.55
   if np.max(np.abs(a))>0:a=a/np.max(np.abs(a))*peak
   # Tiny end fade removes clicks without touching the timing of an impact.
   fade=min(round(SR*.005),len(a)//2);a[:fade]*=np.linspace(0,1,fade);a[-fade:]*=np.linspace(1,0,fade)
   pcm=np.rint(a*32767).astype('<i2');write_wav(A/(key+'.wav'),pcm);blob=fsb(pcm,key)
   bank.extend(bytes((-len(bank))%32));offset=len(bank);bank.extend(blob)
   obj=file.objects[item['id']];d=obj.read_typetree()
   d.update(m_Frequency=SR,m_Channels=1,m_BitsPerSample=16,m_Length=len(pcm)/SR,m_CompressionFormat=0,m_SubsoundIndex=0,m_LoadType=2 if old.startswith('Ambience_') or old=='Music02' else 0)
   d['m_Resource']={'m_Source':asset.replace('.assets','.resource'),'m_Offset':offset,'m_Size':len(blob)};obj.save_typetree(d)
   # Decode the ACTUAL new bank with FMOD, not only the writer's assumptions.
   decoded=next(iter(fmod_toolkit.raw_to_wav(blob,key,1,SR).values()))
   with wave.open(io.BytesIO(decoded)) as f:
    assert f.getframerate()==SR and f.getnchannels()==1 and f.getnframes()==len(pcm)
    assert f.readframes(f.getnframes())==pcm.tobytes()
   report.append({'asset':asset,'id':item['id'],'event':old,'source':source,'wav':key+'.wav','duration':len(pcm)/SR,'peak':float(np.max(np.abs(a))),'fsb_bytes':len(blob)})
  (W/asset).write_bytes(file.save());(W/asset.replace('.assets','.resource')).write_bytes(bank)
 (A/'CREDITS.md').write_text('# Cloudcourt VR — audio v18\n\nKenney, Impact Sounds (1.0), CC0: https://kenney.nl/assets/impact-sounds\nKenney, Interface Sounds (1.0), CC0: https://kenney.nl/assets/interface-sounds\nLicenses verified 2026-10-25; original license files included.\n\nAll other WAV files are original procedural sound/music composed by build_audio_v18.py. No original game audio is used. The project dedicates these new synthesized WAVs to CC0.\nScore voices were replaced with distinct blue/red team chimes; score text identifies the team.\n',encoding='utf-8')
 (R/'analysis/v18-audio-validation.json').write_text(json.dumps({'passed':True,'clips':report,'count':len(report),'all_fmod_roundtrips':True},indent=2))
 print(json.dumps({'clips':len(report),'fmod_decoded':True}))
if __name__=='__main__':main()
