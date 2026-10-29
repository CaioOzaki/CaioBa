"""Split only player cuff triangles into independently colored decorative children.

Original v23 meshes, including the shared bot thumb, remain byte identical.
No tracking root, collider, texture or script changes. Caller owns serialization.
"""
from pathlib import Path
import argparse,copy,hashlib,json,struct,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np
import UnityPy
from fix_gloves_v16 import hierarchy,_model_class
from build_avatar_v21 import clone
from build_menu_v19 import save_tree,ptr
PATHS=['Hand Root L/Open/Cloudcourt Open Glove','Hand Root L/Closed/Cloudcourt Closed Glove','Hand Root R/Open/Cloudcourt Open Glove','Hand Root R/Closed/Cloudcourt Closed Glove','Hand Root L/CC_ThumbsUp','Hand Root R/CC_ThumbsUp','Hand Root L/CC_SettingOpen','Hand Root R/CC_SettingOpen']
CUFF_FIRST,CUFF_END=425,850
# Samples from the delivered compressed outfit atlas, palette1 center (cloth).
OUTFIT_RGB=[(16,28,41),(247,243,239),(16,28,41),(239,235,231),(247,243,239),(16,28,41),(33,134,206),(24,81,66),(115,44,74)]

def outfit_colors(file):
    tex=next(o for o in file.objects.values() if o.type.name=='Texture2D' and o.read_typetree()['m_Name']=='Cloudcourt v19 Outfits 3x3')
    im=tex.read().image.convert('RGB');w,h=im.size
    return [im.getpixel((int(((i%3)+.6875)*w/3),int(((i//3)+.0625)*h/3))) for i in range(9)]

def build_resources_v24(file):
    before={i:o.get_raw_data() for i,o in file.objects.items()};g,t,p=hierarchy(file)
    colors=outfit_colors(file);assert colors==OUTFIT_RGB,('Outfit atlas changed: update native sample colors',colors)
    named={o.read_typetree()['m_Name']:o for o in file.objects.values() if o.type.name in ('Mesh','Material')}
    def ensure(name,source,tree):
        obj=named.get(name)
        if obj is None:obj=clone(file,source);named[name]=obj
        tree['m_Name']=name;save_tree(obj,tree);return obj
    skin=named['Cloudcourt v21 Skin Hands'];md=skin.read_typetree()
    # Every instance obtains Renderer.material at runtime, never sharedMaterial.
    for key,value in md['m_SavedProperties']['m_Colors']:
        if key=='_Color':value.update(r=1.,g=1.,b=1.,a=1.)
    material=ensure('Cloudcourt v24 Sleeve',skin,md);records=[]
    for suffix in PATHS:
        path=next(x for x in p if x.endswith(suffix));tid=p[path];goid=t[tid]['m_GameObject']['m_PathID'];go=g[goid]
        comps={file.objects[c['component']['m_PathID']].type.name:file.objects[c['component']['m_PathID']] for c in go['m_Component']}
        # Always derive from the approved immutable-named v23 mesh, even on reapply.
        side='L' if 'Hand Root L/' in suffix else 'R'
        pose='Thumb' if 'ThumbsUp' in suffix else 'Set' if 'SettingOpen' in suffix else 'Closed' if '/Closed/' in suffix else 'Open'
        source=named[f'Cloudcourt v23 {pose} {side}'];sd=source.read_typetree()
        tri=np.frombuffer(bytes(sd['m_IndexBuffer']),'<u2').reshape(-1,3)
        cuff=np.all((tri>=CUFF_FIRST)&(tri<CUFF_END),axis=1)
        assert cuff.any() and not np.any(np.any((tri>=CUFF_FIRST)&(tri<CUFF_END),axis=1)&~cuff)
        hd=copy.deepcopy(sd);kept=tri[~cuff];hd['m_IndexBuffer']=kept.astype('<u2').tobytes();hd['m_SubMeshes'][0]['indexCount']=int(kept.size)
        hand=ensure(f'Cloudcourt v24 Bare {pose} {side}',source,hd)
        fd=comps['MeshFilter'].read_typetree();fd['m_Mesh']=ptr(hand.path_id);save_tree(comps['MeshFilter'],fd)
        vertices=np.frombuffer(bytes(sd['m_VertexData']['m_DataSize']),'<f4').reshape(-1,12)[CUFF_FIRST:CUFF_END]
        m=_model_class()();m.v=vertices[:,:3].tolist();m.n=vertices[:,3:6].tolist();m.uv=[(.5625,.9375)]*len(vertices);m.b=[0]*len(vertices);m.tri=(tri[cuff]-CUFF_FIRST).tolist()
        sleeve=ensure(f'Cloudcourt v24 Sleeve {side}',source,m.serialize(sd,f'Cloudcourt v24 Sleeve {side}',False))
        childpath=path+'/CC_Sleeve'
        if childpath not in p:
            originals=[file.objects[goid],file.objects[tid],comps['MeshFilter'],comps['MeshRenderer']]
            copies=[clone(file,o) for o in originals];mapping={a.path_id:b.path_id for a,b in zip(originals,copies)}
            def remap(d):
                if isinstance(d,dict):
                    if set(d)=={'m_FileID','m_PathID'} and d['m_FileID']==0 and d['m_PathID'] in mapping:return ptr(mapping[d['m_PathID']])
                    return {k:remap(v) for k,v in d.items()}
                return [remap(v) for v in d] if isinstance(d,list) else d
            for old,new in zip(originals,copies):save_tree(new,remap(old.read_typetree()))
            cg,ct,cf,cr=copies;d=cg.read_typetree();d['m_Name']='CC_Sleeve';d['m_IsActive']=True;save_tree(cg,d)
            d=ct.read_typetree();d.update(m_Father=ptr(tid),m_Children=[],m_LocalPosition=dict(x=0.,y=0.,z=0.),m_LocalRotation=dict(x=0.,y=0.,z=0.,w=1.),m_LocalScale=dict(x=1.,y=1.,z=1.))
            pd=file.objects[tid].read_typetree();d['m_RootOrder']=len(pd['m_Children']);save_tree(ct,d);pd['m_Children'].append(ptr(ct.path_id));save_tree(file.objects[tid],pd)
        else:
            ct=file.objects[p[childpath]];cg=file.objects[ct.read_typetree()['m_GameObject']['m_PathID']]
            cc={file.objects[c['component']['m_PathID']].type.name:file.objects[c['component']['m_PathID']] for c in cg.read_typetree()['m_Component']};cf=cc['MeshFilter'];cr=cc['MeshRenderer']
        d=cf.read_typetree();d['m_Mesh']=ptr(sleeve.path_id);save_tree(cf,d)
        d=cr.read_typetree();d['m_Materials']=[ptr(material.path_id)];save_tree(cr,d)
        records.append(dict(path=path,transform=tid,filter=comps['MeshFilter'].path_id,original_mesh=source.path_id,mesh=hand.path_id,sleeve_transform=ct.path_id,sleeve_mesh=sleeve.path_id))
    changed=sorted(i for i,b in before.items() if b!=file.objects[i].get_raw_data());allowed={r[k] for r in records for k in ('transform','filter')}
    assert set(changed)<=allowed
    return dict(hands=records,changed_existing_ids=changed,added_ids=sorted(set(file.objects)-set(before)),outfit_rgb=colors,material=material.path_id)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=R/'versions/cloudcourt-v23-antes-v24');ap.add_argument('--output',type=Path,default=R/'visuals-v24-sleeves');a=ap.parse_args()
    assert a.source.resolve()!=a.output.resolve() and 'working' not in a.output.resolve().relative_to(R.resolve()).parts
    f=UnityPy.load(str(a.source/'resources.assets')).file;report=build_resources_v24(f);data=f.save();a.output.mkdir(exist_ok=True,parents=True);(a.output/'resources.assets').write_bytes(data)
    report['sha256']=hashlib.sha256(data).hexdigest();(a.output/'sleeves-v24-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
