"""Original CC0 lofi playlist, categorized Settings and reused Cloudcourt emblem.

Only own oscillator/noise synthesis. No downloaded song, sample, or reference photo.
Caller supplies in-memory Unity assets; this module never installs or publishes.
"""
from pathlib import Path
import copy,hashlib,json,math,struct,sys,wave
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np
from PIL import Image
from build_audio_v18 import fsb
from build_art_v26 import banner_art,texture
from build_menu_v19 import MenuEditor,RAW_IMAGE,set_raw
A=R/'assets/cloudcourt-v28';SR=22050
TRACKS=[('Boardwalk Afterglow',76,[57,53,60,55]),('Soft Court Lights',72,[62,58,65,60]),('Sea Glass',80,[60,56,63,58])]

def note(frequency,duration,gain=.1,warm=True):
    t=np.arange(round(duration*SR))/SR
    env=(1-np.exp(-t*28))*np.exp(-t*(2.1 if warm else 5.5))
    y=np.sin(2*np.pi*frequency*t)
    if warm:y+=.22*np.sin(2*np.pi*frequency*2*t)+.07*np.sin(2*np.pi*frequency*3*t)
    return y*env*gain

def lofi_track(index):
    title,bpm,roots=TRACKS[index];beat=60/bpm;beats=96
    y=np.zeros(round((beats*beat+2)*SR));rng=np.random.default_rng(2800+index)
    def put(at,data):
        j=round(at*SR);n=min(len(data),len(y)-j)
        if n>0:y[j:j+n]+=data[:n]
    hz=lambda midi:440*2**((midi-69)/12)
    for bar in range(24):
        root=roots[(bar//2)%4];start=bar*4*beat
        # Relaxed seventh chords with spread voicings, all original note choices.
        intervals=[0,3,7,10] if (bar//2)%4 in (0,2) else [0,4,7,11]
        for k,n in enumerate(intervals):put(start+.014*k,note(hz(root+n),beat*3.8,.055))
        for at in [0,1.75,2.5]:put(start+at*beat,note(hz(root-24),beat*.9,.16,False))
        if bar%4 in (1,2,3):
            for k in range(3):
                n=[7,10,14,12,3,7][(bar+k+index)%6]
                put(start+(1+k*.75)*beat,note(hz(root+n+12),beat*.65,.025))
        for b in range(4):
            j=start+b*beat
            if b in (0,2):
                t=np.arange(round(.24*SR))/SR
                put(j,np.sin(2*np.pi*(43*t+35*(1-np.exp(-t*30))/30))*np.exp(-t*22)*.22)
            if b in (1,3):
                t=np.arange(round(.15*SR))/SR;n=rng.normal(0,1,len(t))
                n=np.convolve(n,np.ones(7)/7,'same');put(j+.025,n*np.exp(-t*35)*.10+np.sin(2*np.pi*180*t)*np.exp(-t*45)*.018)
            for off in [0,.58]:
                t=np.arange(round(.06*SR))/SR;n=rng.normal(0,1,len(t));n-=np.convolve(n,np.ones(5)/5,'same')
                put(j+off*beat,n*np.exp(-t*90)*(.016 if off else .022))
    # A restrained tape-like low pass and soft saturation, not audible hiss loops.
    y=np.convolve(y,np.array([1,2,3,2,1])/9,'same');y=np.tanh(y*1.25)
    # A short stereo-free room echo keeps VR music cheap: one streaming mono clip.
    delay=round(.18*SR);y[delay:]+=y[:-delay]*.11
    fade=round(1.25*SR);y[:fade]*=np.linspace(0,1,fade);y[-fade:]*=np.linspace(1,0,fade)
    y*=.48/max(np.max(np.abs(y)),.01)
    return np.rint(y*32767).astype('<i2')

def write_audio_art():
    A.mkdir(parents=True,exist_ok=True);parts=[];rows=[];offset=0
    for i,(name,bpm,_) in enumerate(TRACKS):
        pcm=lofi_track(i);path=A/f'lofi-{i+1}.wav'
        with wave.open(str(path),'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes(pcm.tobytes())
        rows.append(dict(title=name,bpm=bpm,seconds=len(pcm)/SR,start_seconds=offset,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),file=path.name))
        offset+=len(pcm)/SR;parts.append(pcm)
    license_text='Cloudcourt v28 original lofi playlist\n\n'+ '\n'.join(x['title'] for x in rows)+'\n\nAll music and sounds in these tracks are synthesized by build_settings_audio_v28.py from oscillators and deterministic noise. No third-party recording, sample, melody, or audio file is used.\n\nTo the extent possible under law, the creators waive copyright and related rights to these generated recordings and compositions under CC0 1.0 Universal. https://creativecommons.org/publicdomain/zero/1.0/\n'
    (A/'LOFI-LICENSE.txt').write_text(license_text,encoding='utf-8')
    (A/'lofi-playlist.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    return np.concatenate(parts),rows

def apply_audio_v28(file,old_bank,pcm):
    bank=bytearray();audit=[]
    for o in sorted(file.objects.values(),key=lambda x:x.path_id):
        if o.type.name!='AudioClip':continue
        d=o.read_typetree();res=d['m_Resource'];old=dict(res)
        if o.path_id==171:
            data=fsb(pcm,'Cloudcourt_Original_Lofi_Playlist_v28')
            d.update(m_Name='Cloudcourt Lofi Playlist',m_Frequency=SR,m_Channels=1,m_BitsPerSample=16,m_Length=len(pcm)/SR,m_CompressionFormat=0,m_SubsoundIndex=0,m_LoadType=2,m_PreloadAudioData=False,m_LoadInBackground=True)
        else:
            data=old_bank[res['m_Offset']:res['m_Offset']+res['m_Size']]
            assert len(data)==res['m_Size']
        bank.extend(bytes((-len(bank))%32));start=len(bank);bank.extend(data)
        d['m_Resource']=dict(m_Source='sharedassets0.resource',m_Offset=start,m_Size=len(data));o.save_typetree(d)
        audit.append(dict(id=o.path_id,changed_audio=o.path_id==171,old=old,new=d['m_Resource']))
    return bytes(bank),audit

def apply_settings_logo_v28(resources,menu):
    e=MenuEditor(menu);s='Menu/Pages/Settings'
    game=['Movement Button','Jump Button','Jump Height Button','Snap Turn Button','Front Row Only Button','Aim Assist Button','Friend Bot Pro Button','Opponent Bot Pro Button','Movement Speed Slider','Region Button']
    for i,name in enumerate(game):
        e.rect(e.find(s+'/'+name),-160 if i<5 else 160,93-(i%5)*43,288,35)
        e.active(e.find(s+'/'+name),True)
    e.rect(e.find(s+'/Back Button'),0,-155,216,36)
    for name,text,x in [('Game','[ GAME ]',-220),('Graphics','GRAPHICS',0),('Audio','SOUND',220)]:
        e.button(s+'/CC_Settings'+name,text,x,157,205,38,18)
    e.label(s+'/CC_GameHint','Comfort, controls, bots and connection.',0,-124,690,26,16)
    e.rect(e.find(s+'/CC_GraphicsOpen'),0,42,320,45)
    e.label(s+'/CC_GraphicsSummary','LOW / MEDIUM / HIGH / ULTRA',0,102,700,34,23)
    e.label(s+'/CC_GraphicsWarning','Graphics changes take effect after restarting Cloudcourt.',0,-30,690,58,18)
    for path in ['CC_GraphicsOpen','CC_GraphicsSummary','CC_GraphicsWarning']:e.active(e.find(s+'/'+path),False)
    controls=e.ensure(s+'/CC_AudioControls','Menu/Pages/Start/Cloudcourt Big rallies. Good company.')
    # A transparent non-raycasting container. Text is empty; only children draw.
    e.text(controls,'',12);e.rect(controls,0,0,760,260)
    e.rect(e.find(s+'/Music Button'),0,104,320,34);e.active(e.find(s+'/Music Button'),False)
    for i,(key,label) in enumerate([('Master','MASTER VOLUME  100%'),('Music','MUSIC VOLUME  65%'),('Game','GAME SOUNDS  100%'),('UI','INTERFACE SOUNDS  80%')]):
        y=56-i*43;p=s+'/CC_AudioControls/'
        e.label(p+'CC_Volume'+key+'Value',label,0,y,370,31,18)
        e.button(p+'CC_Volume'+key+'Minus','-',-258,y,62,32,23)
        e.button(p+'CC_Volume'+key+'Plus','+',258,y,62,32,23)
    e.label(s+'/CC_AudioControls/CC_PlaylistCredit','LOFI PLAYLIST  /  3 original CC0 tracks',0,-125,690,24,15)
    e.active(controls,False)
    # Reuse the exact emblem from our own indoor banners; no new brand artwork.
    emblem=banner_art().crop((118,47,394,323)).resize((256,256),Image.Resampling.LANCZOS)
    emblem.save(A/'startup-emblem.png')
    tex=texture(resources,next(o for o in resources.objects.values() if o.type.name=='Texture2D'),'Cloudcourt startup emblem v28',emblem)
    fid=next(i+1 for i,x in enumerate(menu.externals) if x.path.replace('\\','/').rsplit('/',1)[-1].lower()=='resources.assets')
    logo=e.ensure('Menu/Pages/Start/CC_StartupLogo','Menu/CC_Customization/CC_FacePreview')
    e.rect(logo,-243,144,76,76);e.color(logo,(1.,1.,1.,1.))
    raw=e.component(logo,RAW_IMAGE);b=bytearray(raw.get_raw_data());struct.pack_into('<iq',b,72,fid,tex);struct.pack_into('<4f',b,84,0,0,1,1);b[60]=0;set_raw(raw,b)
    e.rect(e.find('Menu/Pages/Start/Cloudcourt CLOUDCOURT VR'),42,146,510,48)
    return dict(categories=['GAME','GRAPHICS','SOUND'],volumes=['Master','Music','Game','Interface'],native_restart_warning=True,logo_texture_id=tex,created_paths=e.created)

def main():
    pcm,tracks=write_audio_art();D=R/'visuals-v28-root';D.mkdir(exist_ok=True)
    import UnityPy
    files={n:UnityPy.load(str(R/'versions/cloudcourt-v27-antes-v28'/n)).file for n in ['resources.assets','level0','sharedassets0.assets']}
    report=apply_settings_logo_v28(files['resources.assets'],files['level0'])
    bank,audit=apply_audio_v28(files['sharedassets0.assets'],(R/'versions/cloudcourt-v27-antes-v28/sharedassets0.resource').read_bytes(),pcm)
    for n,f in files.items():(D/n).write_bytes(f.save())
    (D/'sharedassets0.resource').write_bytes(bank)
    report.update(playlist=tracks,audio=audit,shared_bank_bytes=len(bank),only_own_music=True)
    (D/'root-assets-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k in ['categories','volumes','only_own_music','shared_bank_bytes','playlist']}))
if __name__=='__main__':main()
