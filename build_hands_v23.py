"""v23 visual-only rounded hands; caller owns resource serialization and installation."""
from pathlib import Path
import sys,math,json,hashlib,argparse
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np
import UnityPy
from fix_gloves_v16 import _model_class,glove_model,hierarchy
from build_avatar_v21 import clone
from build_menu_v19 import save_tree,ptr
THICKNESS=.90
PALM_CENTER=(0,0,.045)
PALM_RADII=(.028*THICKNESS,.060,.067)
CUFF_CENTER=(0,0,-.025)
CUFF_RADII=(.032,.066,.023)

def rounded_digit(m,points,radius,tip_radius=None):
    """Single smooth bent capsule, with hemispherical ends and analytic normals.

    Cubic Bezier centerline; cap centers are actual digit endpoints. No extra
    axial ellipsoid radius can turn the thumb into the previous long wedge.
    """
    p=np.asarray(points,dtype=float);tip_radius=radius if tip_radius is None else tip_radius
    def curve(t):
        c=(1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3]
        d=3*(1-t)**2*(p[1]-p[0])+6*(1-t)*t*(p[2]-p[1])+3*t*t*(p[3]-p[2])
        return c,d/np.linalg.norm(d)
    rings=[]
    c,d=curve(0)
    for a in np.linspace(-math.pi/2,0,5)[:-1]:rings.append((c+d*radius*math.sin(a),d,radius*math.cos(a),math.sin(a),math.cos(a)))
    for t in np.linspace(0,1,17):
        c,d=curve(t);r=radius*(1-t)+tip_radius*t;rings.append((c,d,r,0,1))
    c,d=curve(1)
    for a in np.linspace(0,math.pi/2,5)[1:]:rings.append((c+d*tip_radius*math.sin(a),d,tip_radius*math.cos(a),math.sin(a),math.cos(a)))
    start=len(m.v);nseg=24;last_u=None
    for c,d,r,axial,radial in rings:
        # All digit paths are in an anatomical plane; this stable frame avoids twists.
        u=np.cross(d,[0,0,1] if abs(d[2])<.95 else [0,1,0]) if last_u is None else last_u-d*np.dot(last_u,d);u/=np.linalg.norm(u);last_u=u;v=np.cross(d,u)
        for a in np.linspace(0,2*math.pi,nseg+1):
            outward=u*math.cos(a)+v*math.sin(a);normal=outward*radial+d*axial
            m.v.append((c+r*outward).tolist());m.n.append((normal/np.linalg.norm(normal)).tolist());m.uv.append((.5625,.9375));m.b.append(0)
    for j in range(len(rings)-1):
        for i in range(nseg):
            a=start+j*(nseg+1)+i;b=a+nseg+1
            m.tri.extend([(a,a+1,b),(a+1,b+1,b)])

def hand_model_v23(pose,side):
    assert pose in ('Open','Closed','Thumb','Set') and side in ('L','R')
    if pose in ('Open','Closed'):
        m=glove_model(pose,'L')
        # The first two softboxes are palm and cuff. Cuff remains unchanged.
        cuff_start=25*17;cuff_end=cuff_start*2
        for i in list(range(cuff_start))+list(range(cuff_end,len(m.v))):
            m.v[i][0]*=THICKNESS
            n=np.asarray(m.n[i]);n[0]/=THICKNESS;m.n[i]=(n/np.linalg.norm(n)).tolist()
    else:
        m=_model_class()();m.softbox(PALM_CENTER,PALM_RADII,0,0);m.softbox(CUFF_CENTER,CUFF_RADII,0,1)
        if pose=='Thumb':
            for y in (-.046,-.015,.016,.047):
                rounded_digit(m,[(0,y,.094),(-.010,y,.153),(.075,y,.150),(.030,y,.075)],.016,.0145)
            m.ellipsoid((.004,.047,.047),(.026,.026,.033),0,0,segments=24,rings=16)
            rounded_digit(m,[(.004,.055,.051),(.007,.084,.055),(.009,.118,.059),(.010,.140,.062)],.021,.0175)
        else:
            for y,spread,end in [(-.046,-.029,.179),(-.015,-.010,.202),(.016,.010,.211),(.047,.028,.192)]:
                rounded_digit(m,[(0,y,.095),(-.004,y+spread*.25,.136),(.008,y+spread*.8,end-.007),(.031,y+spread,end)],.016,.014)
            m.ellipsoid((.004,.047,.033),(.026,.027,.033),0,0,segments=24,rings=16)
            rounded_digit(m,[(.004,.052,.035),(.006,.078,.039),(.016,.109,.054),(.031,.127,.071)],.021,.017)
    if side=='R':
        m.v=[[-x,y,z] for x,y,z in m.v];m.n=[[-x,y,z] for x,y,z in m.n];m.tri=[(a,c,b) for a,b,c in m.tri]
    return m

def build_resources_v23(file):
    before={i:o.get_raw_data() for i,o in file.objects.items()};g,t,p=hierarchy(file);records=[]
    for pose in ('Open','Closed','Thumb','Set'):
        for side in ('L','R'):
            suffix=f'Hand Root {side}/{pose}/Cloudcourt {pose} Glove' if pose in ('Open','Closed') else f'Hand Root {side}/'+('CC_ThumbsUp' if pose=='Thumb' else 'CC_SettingOpen')
            path=next(x for x in p if x.endswith(suffix));go=g[t[p[path]]['m_GameObject']['m_PathID']]
            filt=next(file.objects[c['component']['m_PathID']] for c in go['m_Component'] if file.objects[c['component']['m_PathID']].type.name=='MeshFilter')
            fd=filt.read_typetree();template=file.objects[fd['m_Mesh']['m_PathID']];name=f'Cloudcourt v23 {pose} {side}'
            obj=next((o for o in file.objects.values() if o.type.name=='Mesh' and o.read_typetree()['m_Name']==name),None)
            if obj is None:obj=clone(file,template)
            save_tree(obj,hand_model_v23(pose,side).serialize(template.read_typetree(),name,False));fd['m_Mesh']=ptr(obj.path_id);save_tree(filt,fd)
            records.append(dict(path=path,filter=filt.path_id,mesh=obj.path_id,pose=pose,side=side))
    right=next(r['mesh'] for r in records if r['pose']=='Thumb' and r['side']=='R');bots=[]
    for path,tid in p.items():
        if not path.endswith('/CC_WinThumb'):continue
        go=g[t[tid]['m_GameObject']['m_PathID']];filt=next(file.objects[c['component']['m_PathID']] for c in go['m_Component'] if file.objects[c['component']['m_PathID']].type.name=='MeshFilter')
        fd=filt.read_typetree();fd['m_Mesh']=ptr(right);save_tree(filt,fd);bots.append(dict(path=path,filter=filt.path_id,transform=tid))
    allowed={r['filter'] for r in records+bots};changed=sorted(i for i,raw in before.items() if raw!=file.objects[i].get_raw_data())
    assert set(changed)<=allowed
    return dict(hands=records,bots=bots,changed_existing_ids=changed,added_ids=sorted(set(file.objects)-set(before)),palm_thickness_factor=THICKNESS,palm_radii=PALM_RADII,cuff_unchanged=True,thumb_axis='+Y',finger_axis='+Z',bot_transform_unchanged=True,scope='Mesh geometry and MeshFilter links only; tracking, physics, materials, textures and activation unchanged')

def main():
    a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--output',type=Path,required=True);o=a.parse_args()
    assert o.source.resolve()!=o.output.resolve();assert 'working' not in o.output.resolve().relative_to(R.resolve()).parts
    o.output.mkdir(parents=True,exist_ok=True);src=o.source/'resources.assets';f=UnityPy.load(str(src)).file;report=build_resources_v23(f);data=f.save();(o.output/'resources.assets').write_bytes(data)
    report.update(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(data).hexdigest());(o.output/'hands-v23-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()




