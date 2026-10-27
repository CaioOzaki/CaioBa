"""Texture40-only v27 ball artwork. No changes to game scripts, meshes or materials.

Analytic sphere/cube panels are authored as native pixels for the existing UV atlas.
No photos, labels, logos, fonts or badge geometry enter the artwork.
"""
from pathlib import Path
import sys, math, json, hashlib
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np
from PIL import Image
import UnityPy
from build_environment_v21 import set_rgb_full_mips, snapshot, delta, readable
A=R/'assets/cloudcourt-v27'
OUTPUT=R/'visuals-v27-balls/resources.assets'
SOURCE=R/'versions/cloudcourt-v27-antes-sem-escrita/resources.assets'

def indoor_art():
    # Exactly v26's existing panel surface, with the badge drawing omitted.
    n=1024;y,x=np.mgrid[:n,:n];u=x/n;v=y/n
    panel=np.floor((u+.045*np.sin(v*math.pi*2))*8).astype(int)%8
    rgb=np.array([[250,211,20],[22,73,164]]*4)[panel].astype(np.uint8)
    phase=((u+.045*np.sin(v*math.pi*2))*8)%1
    rgb[(phase<.009)|(phase>.991)]=[23,43,66]
    dots=((x%9-4)**2+(y%9-4)**2)<1.8
    rgb[dots]=np.maximum(rgb[dots].astype(int)-9,0)
    return Image.fromarray(rgb)

def beach_art():
    """Six curved panel groups, each split into three broad perpendicular strips.

    Cube projection gives the familiar classic volleyball panel layout on a sphere;
    the adjacent groups turn ninety degrees instead of running pole to pole.
    """
    n=1024;y,x=np.mgrid[:n,:n];u=x/n;v=y/n
    a=2*math.pi*(1-u);t=math.pi*v
    p=np.stack([np.sin(t)*np.cos(a),np.cos(t),np.sin(t)*np.sin(a)],axis=-1)
    ab=np.abs(p);axis=np.argmax(ab,axis=-1);major=np.max(ab,axis=-1)
    # Cyclic local axes make neighboring face groups run perpendicular.
    across=np.choose(axis,[p[...,1],p[...,2],p[...,0]])/major
    along=np.choose(axis,[p[...,2],p[...,0],p[...,1]])/major
    face=axis*2+(np.take_along_axis(p,axis[...,None],axis=-1)[...,0]<0)
    band=np.clip(np.floor((across+1)*1.5).astype(int),0,2)
    # RGB palette: broad whites, saturated royal blue, warm yellow.
    palette=np.array([[246,245,236],[249,205,18],[21,78,177]],dtype=float)
    groups=np.array([[2,0,2],[2,0,2],[1,2,1],[1,2,1],[0,1,0],[0,1,0]])
    color=groups[face,band];rgb=palette[color]
    # Orange/red fades and halftone accents confined to colored end panels.
    # The white leather is left clean, matching the supplied physical references.
    fade=np.clip((along-.05)/.95,0,1)
    yellow=(color==1);blue=(color==2)
    mix=np.where(yellow,fade**1.6*.9,0)
    rgb=rgb*(1-mix[...,None])+np.array([234,62,53])*mix[...,None]
    # Dot pitch is defined in sphere space, independent of camera view.
    q1=(np.arctan(across)*48/math.pi)%1
    q2=(np.arctan(along)*48/math.pi)%1
    dot=((q1-.5)**2+(q2-.5)**2)<(.12+.18*fade)**2
    accent=dot&(fade>.15)&(yellow|blue)
    rgb[accent]=rgb[accent]*.28+np.array([248,153,71])*.72
    # Recessed seams: face boundaries plus the two internal panel boundaries.
    sortedab=np.sort(ab,axis=-1)
    edge=(sortedab[...,-1]-sortedab[...,-2])/major
    inner=np.minimum(np.abs(across-1/3),np.abs(across+1/3))
    seam=(edge<.009)|(inner<.009)
    rim=((edge<.019)|(inner<.018))&~seam
    rgb[rim]*=.86;rgb[seam]=[113,122,126]
    # Fine low-contrast pebble texture follows the v26 texel scale.
    pebble=((x%9-4)**2+(y%9-4)**2)<1.8
    rgb[pebble]=np.maximum(rgb[pebble]-8,0)
    return Image.fromarray(np.clip(rgb,0,255).astype(np.uint8))

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build_plain_balls_v27(f,write_art=True):
    before=snapshot(f)
    indoor=indoor_art();beach=beach_art()
    dual=Image.new('RGB',(2048,1024));dual.paste(indoor,(0,0));dual.paste(beach,(1024,0))
    old=f.objects[40].read_typetree()
    tex=f.objects[40].read();set_rgb_full_mips(tex,dual);tex.save();readable(f.objects[40])
    new=f.objects[40].read_typetree()
    assert delta(f,before)==[40],delta(f,before)
    allowed={'image data','m_ImageData','m_CompleteImageSize'}
    fields=[k for k in old if old[k]!=new[k]]
    assert set(fields)<=allowed,fields
    assert tex.m_Width==2048 and tex.m_Height==1024 and tex.m_TextureFormat==3 and tex.m_MipCount==12
    assert len(tex.image_data)==old['m_CompleteImageSize']
    if write_art:
        A.mkdir(parents=True,exist_ok=True)
        for name,im in [('ball-indoor',indoor),('ball-beach',beach),('ball-dual-atlas',dual)]:im.save(A/(name+'.png'))
    return dict(changed_objects=[40],changed_texture_fields=fields,atlas_size=[2048,1024],format=3,mip_count=12,gpu_bytes=len(tex.image_data),no_lettering_or_logos=True,indoor_v26_surface_preserved=True,beach_panel_groups=6,beach_panel_count=18)

def main():
    A.mkdir(parents=True,exist_ok=True)
    f=UnityPy.load(str(SOURCE)).file;b=snapshot(f)
    report=build_plain_balls_v27(f)
    out=OUTPUT;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(f.save())
    again=UnityPy.load(str(out)).file
    assert delta(again,b)==[40]
    assert set(again.objects)==set(b)
    report.update(source_path=str(SOURCE),source_sha256=sha(SOURCE),output_path=str(out),output_sha256=sha(out),builder_sha256=sha(__file__),serialized_object_delta=[40],all_other_object_bytes_identical=True,texture_data_sha256=hashlib.sha256(again.objects[40].read().image_data).hexdigest())
    (A/'plain-balls-report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
