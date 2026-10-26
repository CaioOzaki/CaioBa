"""v22 cosmetic hand meshes. Input and output must be isolated; synced sources stay read-only."""
from pathlib import Path
import sys,copy,json,hashlib,argparse,math
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np
import UnityPy
from build_avatar_v21 import clone
from build_menu_v19 import save_tree,ptr
from fix_gloves_v16 import _model_class,hierarchy

def segment(m,a,b,r):
    # Endpoints are actual cap centers; v21 limb() incorrectly added another
    # axial radius to a very long thumb and obscured the anatomical silhouette.
    a=np.asarray(a);b=np.asarray(b);v=b-a;length=np.linalg.norm(v);y=v/length
    x=np.cross(y,[0,0,1] if abs(y[2])<.95 else [0,1,0]);x=x/np.linalg.norm(x)
    z=np.cross(x,y)
    m.ellipsoid((a+b)/2,(r,length/2+r,r*.9),0,0,axis=np.stack([x,y,z],axis=1),segments=16,rings=12)

def hand_model_v22(pose,side):
    assert pose in ('Thumb','Set') and side in ('L','R')
    m=_model_class()()
    m.softbox((0,0,.032),(.025,.047,.044),0,0)
    m.softbox((0,0,-.020),(.028,.050,.016),0,1)
    if pose=='Thumb':
        # Four digits bend over the knuckles and return into the palm. The
        # thumb follows +Y (verified original thumb edge), not finger +Z.
        for y in (-.036,-.012,.012,.036):
            segment(m,(-.004,y,.061),(.014,y,.087),.012)
            segment(m,(.014,y,.087),(.033,y,.071),.012)
            segment(m,(.033,y,.071),(.033,y,.045),.011)
        m.ellipsoid((.006,.038,.039),(.027,.025,.030),0,0,segments=20,rings=12)
        segment(m,(.005,.048,.041),(.010,.080,.045),.017)
        segment(m,(.010,.080,.045),(.011,.115,.047),.015)
    else:
        # Cupped setting hand: fingers splay in the palm plane, flex toward
        # palm +X near their tips, and thumb/index leave an inward window.
        for y,spread,length in [(-.035,-.026,.133),(-.011,-.009,.157),(.013,.008,.163),(.036,.024,.148)]:
            mid=(.001,y+spread*.55,.095+(length-.133)*.45)
            tip=(.022,y+spread,length)
            segment(m,(0,y,.060),mid,.011)
            segment(m,mid,tip,.010)
        m.ellipsoid((.005,.038,.025),(.025,.025,.031),0,0,segments=20,rings=12)
        segment(m,(.005,.040,.026),(.010,.075,.037),.016)
        segment(m,(.010,.075,.037),(.022,.108,.050),.014)
    if side=='R':
        m.v=[[-x,y,z] for x,y,z in m.v];m.n=[[-x,y,z] for x,y,z in m.n];m.tri=[(a,c,b) for a,b,c in m.tri]
    return m

def build_resources_v22(file):
    before={i:o.get_raw_data() for i,o in file.objects.items()}
    g,t,p=hierarchy(file);records=[]
    for pose,name in [('Thumb','CC_ThumbsUp'),('Set','CC_SettingOpen')]:
        for side in ('L','R'):
            path=next(x for x in p if x.endswith(f'Hand Root {side}/{name}'));tr=p[path]
            go=g[t[tr]['m_GameObject']['m_PathID']]
            filt=next(file.objects[x['component']['m_PathID']] for x in go['m_Component'] if file.objects[x['component']['m_PathID']].type.name=='MeshFilter')
            fd=filt.read_typetree();template=file.objects[fd['m_Mesh']['m_PathID']]
            meshname=f'Cloudcourt v22 {pose} {side}'
            mesh=next((o for o in file.objects.values() if o.type.name=='Mesh' and o.read_typetree()['m_Name']==meshname),None)
            if mesh is None:mesh=clone(file,template)
            save_tree(mesh,hand_model_v22(pose,side).serialize(template.read_typetree(),meshname,False))
            fd['m_Mesh']=ptr(mesh.path_id);save_tree(filt,fd)
            records.append(dict(path=path,filter=filt.path_id,mesh=mesh.path_id,pose=pose,side=side))
    # Bot overlay receives the current character's own atlas at bind time.
    # Its UV palette 0 is skin, palette 1 is that bot's sleeve/cuff.
    right=next(x['mesh'] for x in records if x['pose']=='Thumb' and x['side']=='R')
    for path,tr in p.items():
        if path.endswith('/CC_WinThumb'):
            go=g[t[tr]['m_GameObject']['m_PathID']]
            filt=next(file.objects[x['component']['m_PathID']] for x in go['m_Component'] if file.objects[x['component']['m_PathID']].type.name=='MeshFilter')
            fd=filt.read_typetree();fd['m_Mesh']=ptr(right);save_tree(filt,fd)
            d=file.objects[tr].read_typetree();d['m_LocalScale']=dict(x=1.30,y=1.30,z=1.30);d['m_LocalPosition']=dict(x=0.,y=0.,z=0.);save_tree(file.objects[tr],d)
    changed=[i for i,raw in before.items() if file.objects[i].get_raw_data()!=raw]
    allowed={x['filter'] for x in records}
    for path,tr in p.items():
        if path.endswith('/CC_WinThumb'):
            allowed.add(tr)
            allowed.update(x['component']['m_PathID'] for x in g[t[tr]['m_GameObject']['m_PathID']]['m_Component'] if file.objects[x['component']['m_PathID']].type.name=='MeshFilter')
    assert set(changed)<=allowed,(set(changed)-allowed)
    return dict(hands=records,changed_existing_ids=changed,added_ids=sorted(set(file.objects)-set(before)),original_tracking_colliders_fist_and_textures_unchanged=True,thumb_axis='+Y',finger_axis='+Z',setting='spread, cupped, flexed fingertips and inward thumb/index window')

def main():
    a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--output',type=Path,required=True);o=a.parse_args()
    assert o.source.resolve()!=o.output.resolve();assert 'working' not in o.output.resolve().relative_to(R.resolve()).parts
    o.output.mkdir(parents=True,exist_ok=True);src=o.source/'resources.assets';f=UnityPy.load(str(src)).file
    report=build_resources_v22(f);data=f.save();(o.output/'resources.assets').write_bytes(data)
    report.update(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(data).hexdigest())
    (o.output/'hands-v22-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
