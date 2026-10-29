"""Add two original disabled, outlined bot callout plaques to resources only.

The caller composes this with the v29 asset build. Never writes working/live or
an input file. Existing bones, scripts, art, materials and colliders are exact.
"""
from pathlib import Path
import copy, json, sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from PIL import Image,ImageDraw,ImageFont
from build_avatar_v21 import clone
from build_menu_v19 import ptr,save_tree,set_raw
from fix_gloves_v16 import hierarchy,_model_class


def callout_image(word):
    # Opaque navy card avoids alpha/fringe dependencies on a borrowed shader.
    # Artwork and wording are authored here; the game's original art is unused.
    im=Image.new('RGB',(512,192),'#11243b');d=ImageDraw.Draw(im)
    d.rounded_rectangle((8,8,503,183),radius=48,fill='#183650',outline='#76d9dc',width=5)
    font=ImageFont.truetype(str(R/'assets/shared/fonts/CloudcourtBubble.ttf'),104)
    d.text((256,94),word,font=font,anchor='mm',fill='#ffffff',stroke_width=6,stroke_fill='#051321')
    return im


def callout_mesh(template):
    m=_model_class()()
    m.v=[[-.39,-.146,0],[.39,-.146,0],[.39,.146,0],[-.39,.146,0]]
    m.n=[[0,0,1]]*4;m.uv=[[0,0],[1,0],[1,1],[0,1]];m.b=[0]*4
    m.tri=[(0,1,2),(0,2,3),(2,1,0),(3,2,0)]
    return m.serialize(template,'Cloudcourt Callout Quad v29',False)


def build_resources_v29(file,art_output=None):
    before={i:o.get_raw_data() for i,o in file.objects.items()}
    gs,ts,paths=hierarchy(file)
    existing=sorted(p for p in paths if p.endswith('/CC_CallMine_v29') or p.endswith('/CC_CallSet_v29'))
    if existing:
        assert len(existing)==10,'Incomplete v29 callout asset set'
        return dict(created=False,idempotent=True,callouts=existing)
    bot_paths=[p.rsplit('/',1)[0] for p in paths if p.endswith('/CC_WinThumb')]
    assert len(bot_paths)==5,bot_paths
    source=next(p for p in paths if p.endswith('/CC_WinThumb'));tr=paths[source]
    go=file.objects[ts[tr]['m_GameObject']['m_PathID']]
    components={file.objects[c['component']['m_PathID']].type.name:file.objects[c['component']['m_PathID']] for c in go.read_typetree()['m_Component']}
    mesh_template=file.objects[components['MeshFilter'].read_typetree()['m_Mesh']['m_PathID']]
    mesh=clone(file,mesh_template);save_tree(mesh,callout_mesh(mesh_template.read_typetree()))
    texture_template=next(o for o in file.objects.values() if o.type.name=='Texture2D')
    material_template=file.objects[26] # existing Unlit/Texture shader74 binding
    mats={};images={}
    for tag,word in [('Mine','Mine!'),('Set','Set!')]:
        texture=clone(file,texture_template);t=texture.read();t.m_Name='Cloudcourt '+word+' v29'
        im=callout_image(word);images[tag]=im;t.set_image(im,target_format=3,mipmap_count=1);t.save();set_raw(texture,texture.data)
        mat=clone(file,material_template);d=mat.read_typetree();d['m_Name']='Cloudcourt '+word+' v29'
        d['m_Shader']=ptr(74);d['m_ShaderKeywords']='';d['m_CustomRenderQueue']=2001
        d['m_SavedProperties']['m_TexEnvs']=[('_MainTex',dict(m_Texture=ptr(texture.path_id),m_Scale=dict(x=1.,y=1.),m_Offset=dict(x=0.,y=0.)))]
        d['m_SavedProperties']['m_Colors']=[('_Color',dict(r=1.,g=1.,b=1.,a=1.))]
        save_tree(mat,d);mats[tag]=mat.path_id
    records=[]
    for bot in bot_paths:
        parent=file.objects[paths[bot]];pd=parent.read_typetree()
        for tag in ('Mine','Set'):
            originals=[go,file.objects[tr],components['MeshFilter'],components['MeshRenderer']]
            added=[clone(file,o) for o in originals];mapping={a.path_id:b.path_id for a,b in zip(originals,added)}
            def remap(v):
                if isinstance(v,dict):
                    if set(v)=={'m_FileID','m_PathID'} and v['m_FileID']==0 and v['m_PathID'] in mapping:return ptr(mapping[v['m_PathID']])
                    return {k:remap(x) for k,x in v.items()}
                if isinstance(v,list):return [remap(x) for x in v]
                return v
            for original,new in zip(originals,added):save_tree(new,remap(original.read_typetree()))
            cg,ct,cf,cr=added;gd=cg.read_typetree();gd['m_Name']='CC_Call'+tag+'_v29';gd['m_IsActive']=False;gd['m_Layer']=0;save_tree(cg,gd)
            td=ct.read_typetree();td.update(m_Father=ptr(parent.path_id),m_Children=[],m_LocalPosition=dict(x=0.,y=2.4,z=0.),m_LocalScale=dict(x=1.,y=1.,z=1.),m_LocalRotation=dict(x=0.,y=0.,z=0.,w=1.),m_RootOrder=len(pd['m_Children']));save_tree(ct,td)
            fd=cf.read_typetree();fd['m_Mesh']=ptr(mesh.path_id);save_tree(cf,fd)
            rd=cr.read_typetree();rd.update(m_Materials=[ptr(mats[tag])],m_CastShadows=0,m_ReceiveShadows=False,m_LightProbeUsage=0,m_ReflectionProbeUsage=0);save_tree(cr,rd)
            pd['m_Children'].append(ptr(ct.path_id));records.append(dict(bot=bot,tag=tag,transform=ct.path_id))
        save_tree(parent,pd)
    changed=sorted(i for i,raw in before.items() if file.objects[i].get_raw_data()!=raw)
    assert set(changed)=={paths[p] for p in bot_paths},changed
    if art_output:
        art_output=Path(art_output);art_output.mkdir(parents=True,exist_ok=True)
        for tag,im in images.items():im.save(art_output/(tag.lower()+'-callout.png'))
    return dict(created=True,callouts=records,changed_existing_ids=changed,added_ids=sorted(set(file.objects)-set(before)),
                added_colliders=0,added_scripts=0,disabled_initially=True,wording=['Mine!','Set!'],
                existing_meshes_textures_materials_bones_scripts_exact=True)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert a.source.resolve()!=a.output.resolve() and 'working' not in a.output.parts
    f=UnityPy.load(str(a.source)).file;report=build_resources_v29(f,a.output.parent/'bot-callouts-v29')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(f.save())
    (a.output.parent/'bots-v29-assets.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
