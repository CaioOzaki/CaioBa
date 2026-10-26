"""Restore original authored legacy bot textures, preserving v20.1 meshes/rig.

Only five explicitly requested profiles are updated. Other faces, BOT1's middle
part, materials, renderers, player atlases and identity selection stay unchanged.
"""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
from PIL import Image,ImageDraw
import UnityPy
import build_bots_v20 as bots
from build_environment_v21 import set_rgb_full_mips
PROFILES={1:'Curly',2:'Nerd',4:'Grandma',5:'Grandpa',6:'Side Quiff'}

def appearance_art(output=None):
    output=Path(output or R/'assets/bot-appearance-v21');output.mkdir(parents=True,exist_ok=True)
    original_a=bots.A;bots.A=output
    try:scope=bots.authoring()
    finally:bots.A=original_a
    scope['SHIRTS'][2]='#6b7951';scope['PANTS'][2]='#aa906c'
    scope['SHIRTS'][6]='#101114';scope['PANTS'][6]='#b69d7e'
    scope['HAIRS'][4]='#21121b'
    atlases={}
    for n in PROFILES:
        im=scope['atlas'](n);d=ImageDraw.Draw(im)
        if n==2:
            # Original scout outfit: khaki shirt, green scarf, red neck slide,
            # brown sash, simple round badges; no borrowed marks or lettering.
            d.rectangle((0,512,511,1023),fill=scope['SHIRTS'][n])
            d.polygon([(159,512),(256,611),(353,512),(314,681),(256,614),(198,681)],fill='#d6ba70')
            d.polygon([(197,559),(256,614),(315,559),(286,702),(256,659),(225,702)],fill='#345642')
            d.rounded_rectangle((239,616,274,651),radius=8,fill='#a04c38')
            d.polygon([(395,512),(458,512),(154,1024),(91,1024)],fill='#826342')
            for x,y,c in [(372,684,'#e2b449'),(329,757,'#486d95'),(286,830,'#baa77a')]:
                d.ellipse((x-17,y-17,x+17,y+17),fill=c,outline='#d9cd99',width=4)
            for x in (80,332):d.rectangle((x,750,x+95,829),outline='#aab18a',width=4)
            d.line((256,711,256,1023),fill='#4b5b3d',width=5)
        elif n==6:
            # Plain T-shirt, no chest graphic or previous beige seam accents.
            d.rectangle((0,512,511,1023),fill=scope['SHIRTS'][n]);d.arc((174,467,338,601),0,180,fill='#27282d',width=8)
        elif n==4:
            d.rectangle((640,128,767,255),fill='#38202e')
        im.save(output/f'bot-{n+1:02}-atlas.png');atlases[n]=im
    return scope,atlases

def apply_bot_appearance_v21(file,art=None):
    _,atlases=art or appearance_art();before={i:o.get_raw_data() for i,o in file.objects.items()};textures={}
    for o in file.objects.values():
        if o.type.name!='Material':continue
        d=o.read_typetree();name=d['m_Name']
        if not name.startswith('SimpleCitizens_'):continue
        n=bots.FAMILY[name.split('_')[1]]
        if n not in PROFILES:continue
        ref=next(v['m_Texture'] for k,v in d['m_SavedProperties']['m_TexEnvs'] if k=='_MainTex');assert ref['m_FileID']==0
        ident=ref['m_PathID'];assert ident not in textures or textures[ident]==n;textures[ident]=n
    for ident,n in textures.items():
        tex=file.objects[ident].read();set_rgb_full_mips(tex,atlases[n]);tex.save();bots.readable(file.objects[ident])
    changed=sorted(i for i,o in file.objects.items() if o.get_raw_data()!=before[i]);assert set(changed)<=set(textures)
    return dict(changed_object_ids=changed,texture_profiles=textures,profiles=PROFILES,format='RGB24 opaque lossless',
                resolution=1024,mip_levels=11,texture_bytes=sum(file.objects[i].read_typetree()['m_CompleteImageSize'] for i in textures),
                preserved=['BOT1 exact middle-part mesh and atlas','all other bot meshes','materials','rig','renderers','player face atlases','selection identity'])

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=R/'versions/cloudcourt-v20-1-antes-v21/sharedassets0.assets');p.add_argument('--output',type=Path,default=R/'visuals-v21-environment/sharedassets0.assets');a=p.parse_args()
    assert a.output.resolve()!=a.source.resolve() and 'working' not in a.output.parts
    art=appearance_art();f=UnityPy.load(str(a.source)).file;report=apply_bot_appearance_v21(f,art)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(f.save());(a.output.parent/'bot-appearance-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
