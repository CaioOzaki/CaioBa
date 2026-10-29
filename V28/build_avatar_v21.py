"""Build isolated v21 hand visuals and tone controls; never write working/live.

Original tracking roots, colliders, scripts and all existing textures stay byte
identical. Replaces only four glove meshes/material references; new bot thumbs
are independent decorative children and default inactive.
"""
from pathlib import Path
import argparse,copy,hashlib,json,struct,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from PIL import Image,ImageDraw
from fix_gloves_v16 import _model_class,hierarchy
from build_menu_v19 import MenuEditor,IMAGE,save_tree,set_raw,ptr

def hand_model(state,side):
    assert state in ('Open','Closed') and side in ('L','R')
    m=_model_class()()
    m.softbox((0,0,.041),(.027,.055,.062),0,0)
    m.softbox((0,0,-.025),(.031,.062,.022),0,1)
    if state=='Open':
        for y,length in [(-.043,.151),(-.014,.183),(.015,.192),(.044,.176)]:
            m.limb((0,y,.083),(.004,y,length),.014,.015,0,0)
        m.limb((.002,.043,.025),(.028,.102,.085),.021,.023,0,0)
    else:
        # Four rounded curled fingers form a fist; the thumb stands clear at
        # the rig's +Y thumb edge. Mirror X and winding for the right hand.
        for y in (-.042,-.014,.014,.042):
            m.softbox((.006,y,.101),(.031,.014,.032),0,0)
        m.limb((.012,.046,.043),(.028,.076,.187),.021,.023,0,0)
    if side=='R':
        m.v=[[-x,y,z] for x,y,z in m.v];m.n=[[-x,y,z] for x,y,z in m.n]
        m.tri=[(a,c,b) for a,b,c in m.tri]
    return m

def clone(file,source):
    o=copy.copy(source);o.path_id=max(file.objects)+1;o.assets_file=file
    set_raw(o,source.get_raw_data());file.objects[o.path_id]=o
    return o

def build_resources(file):
    before={i:o.get_raw_data() for i,o in file.objects.items()}
    objects,transforms,paths=hierarchy(file)
    named={o.read_typetree().get('m_Name'):o for o in file.objects.values() if o.type.name in ('Texture2D','Material')}
    tex=named.get('Cloudcourt v21 Neutral Hands')
    if tex is None:
        tex=clone(file,file.objects[1302]);t=tex.read();t.m_Name='Cloudcourt v21 Neutral Hands'
        im=Image.new('RGBA',(1024,1024),'#252b35');ImageDraw.Draw(im).rectangle((512,0,639,127),fill='white')
        t.set_image(im,target_format=12,mipmap_count=9);t.save();set_raw(tex,tex.data)
    mat=named.get('Cloudcourt v21 Skin Hands')
    if mat is None:
        mat=clone(file,file.objects[1303]);d=mat.read_typetree();d['m_Name']='Cloudcourt v21 Skin Hands'
        d['m_SavedProperties']['m_TexEnvs'][0][1]['m_Texture']=ptr(tex.path_id)
        save_tree(mat,d)
    records=[];templates={};new_meshes={}
    for side in ('L','R'):
        for state in ('Open','Closed'):
            path=next(p for p in paths if p.endswith(f'Hand Root {side}/{state}/Cloudcourt {state} Glove'))
            tid=paths[path];go=objects[transforms[tid]['m_GameObject']['m_PathID']]
            comps={file.objects[x['component']['m_PathID']].type.name:file.objects[x['component']['m_PathID']] for x in go['m_Component']}
            original=file.objects[comps['MeshFilter'].read_typetree()['m_Mesh']['m_PathID']]
            meshname=f'Cloudcourt v21 {side} {state}'
            mesh=next((o for o in file.objects.values() if o.type.name=='Mesh' and o.read_typetree()['m_Name']==meshname),None)
            if mesh is None:mesh=clone(file,original)
            save_tree(mesh,hand_model(state,side).serialize(original.read_typetree(),meshname,False))
            d=comps['MeshRenderer'].read_typetree();d['m_Materials']=[ptr(mat.path_id)];save_tree(comps['MeshRenderer'],d)
            templates[side,state]=(tid,comps);new_meshes[side,state]=mesh
            records.append(dict(side=side,state=state,mesh=mesh.path_id,original_mesh=original.path_id))
    def add_visual(path,side,state,scale,position):
        if path in paths:return paths[path]
        parent_path,name=path.rsplit('/',1)
        tid,comps=templates[side,state]
        originals=[file.objects[transforms[tid]['m_GameObject']['m_PathID']],file.objects[tid],comps['MeshFilter'],comps['MeshRenderer']]
        clones=[clone(file,x) for x in originals];mapping={x.path_id:y.path_id for x,y in zip(originals,clones)}
        def remap(d):
            if isinstance(d,dict):
                if set(d)=={'m_FileID','m_PathID'} and d['m_FileID']==0 and d['m_PathID'] in mapping:return ptr(mapping[d['m_PathID']])
                return {k:remap(v) for k,v in d.items()}
            if isinstance(d,list):return [remap(v) for v in d]
            return d
        for old,new in zip(originals,clones):save_tree(new,remap(old.read_typetree()))
        go,tr,filt,_=clones;d=go.read_typetree();d['m_Name']=name;d['m_IsActive']=False;save_tree(go,d)
        d=filt.read_typetree();d['m_Mesh']=ptr(new_meshes[side,state].path_id);save_tree(filt,d)
        d=tr.read_typetree();d['m_Father']=ptr(paths[parent_path]);d['m_LocalPosition']=dict(zip('xyz',position))
        d['m_LocalScale']=dict(x=scale,y=scale,z=scale);d['m_LocalRotation']=dict(x=0.,y=0.,z=0.,w=1.);d['m_Children']=[]
        parent=file.objects[paths[parent_path]];pd=parent.read_typetree();d['m_RootOrder']=len(pd['m_Children']);save_tree(tr,d)
        pd['m_Children'].append(ptr(tr.path_id));save_tree(parent,pd);return tr.path_id
    hand_visuals=[]
    for side in ('L','R'):
        root=next(p for p in paths if p.endswith(f'/Hand Root {side}'))
        for state,name in [('Open','CC_SettingOpen'),('Closed','CC_ThumbsUp')]:
            hand_visuals.append(add_visual(root+'/'+name,side,state,1.,(0.,0.,0.)))
    bot_visuals=[add_visual(bot+'/CC_WinThumb','R','Closed',1.7,(.35,1.3,0.))
                 for bot in ('BotRedPro','BotBluePro','BotRed','BotRedBomb','BotBlue')]
    changed=[i for i,raw in before.items() if file.objects[i].get_raw_data()!=raw]
    return dict(hand_meshes=records,material=mat.path_id,texture=tex.path_id,bot_visuals=bot_visuals,hand_visuals=hand_visuals,
                changed_existing_ids=changed,added_ids=sorted(set(file.objects)-set(before)),
                original_textures_unchanged=all(file.objects[i].get_raw_data()==raw for i,raw in before.items() if file.objects[i].type.name=='Texture2D'))

def build_menu(file):
    e=MenuEditor(file);p='Menu/CC_Customization'
    e.rect(e.find(p),0,0,800,490)
    e.label(p+'/CC_CustomHint','Pick a face. Mix an outfit. Choose your hand tone.',0,115,720,27,16)
    e.label(p+'/CC_HandToneTitle','HANDS',-190,-157,130,28,18)
    e.label(p+'/CC_HandToneLabel','Porcelain',70,-157,220,28,18)
    e.button(p+'/CC_HandTonePrev','<',-70,-157,60,36,22)
    e.button(p+'/CC_HandToneNext','>',260,-157,60,36,22)
    s=e.ensure(p+'/CC_HandToneSwatch','Menu/Pages/Alert/Background');e.rect(s,-245,-157,34,28);e.color(s,(1,.85,.74,1));e.active(s,True)
    image=e.component(s,IMAGE);raw=bytearray(image.get_raw_data());raw[60]=0
    # The backdrop template carries a hollow border sprite. A null sprite
    # makes Image draw a solid colored quad, so the selected tone is visible.
    struct.pack_into('<iq',raw,84,0,0);set_raw(image,raw)
    e.rect(e.find(p+'/CC_CustomizeBack'),0,-213,180,40)
    return dict(created=e.created,tones=6)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=R/'working/VolleyballFever_Data');ap.add_argument('--output',type=Path,default=R/'visuals-v21-avatar');a=ap.parse_args()
    assert a.output.resolve()!=a.source.resolve() and 'working' not in a.output.relative_to(R).parts
    a.output.mkdir(parents=True,exist_ok=True);report={}
    for name,builder in [('resources.assets',build_resources),('level0',build_menu)]:
        source=a.source/name;file=UnityPy.load(str(source)).file;report[name]=builder(file);payload=file.save();(a.output/name).write_bytes(payload)
        report[name].update(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(payload).hexdigest())
    (a.output/'avatar-v21-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
