from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy,numpy as np
from build_art_v26 import *
from UnityPy.helpers.MeshHelper import MeshHandler
D=R/'versions/cloudcourt-v25-antes-v26';names=['resources.assets','level1','level2','level3']
f={n:UnityPy.load(str(D/n)).file for n in names}
b={n:snapshot(o) for n,o in f.items()};report=build_art_assets_v26(f)
for n,o in f.items():
 for i,data in b[n].items():
  if o.objects[i].type.name in ['MonoBehaviour','Transform','RectTransform','Rigidbody','BoxCollider','CapsuleCollider','SphereCollider','MeshCollider']:
   assert o.objects[i].get_raw_data()==data,(n,i,o.objects[i].type.name)
 # Roundtrip serialized data and all owned changed meshes.
 data=o.save();t=UnityPy.load(data).file
 for i in report['changed_objects'][n]:
  ob=t.objects[i]
  if ob.type.name=='Mesh':
   h=MeshHandler(ob.read());h.process();v=np.array(h.m_Vertices);assert np.isfinite(v).all()
   for part in h.get_triangles():
    for tri in part:assert all(0<=x<len(v) for x in tri)
# Real serialized ball UV and material readback (indoor / runtime-selected beach).
m=f['resources.assets'].objects[62];h=MeshHandler(m.read());h.process();uv=np.array(h.m_UV0);assert uv[:,0].min()==0 and uv[:,0].max()==.5
assert f['resources.assets'].objects[40].read().image.size==(2048,1024)
v=np.array(h.m_Vertices);tri=np.array([tri for part in h.get_triangles() for tri in part]);pts=v[tri];normal=np.cross(pts[:,1]-pts[:,0],pts[:,2]-pts[:,0]);valid=np.linalg.norm(normal,axis=1)>1e-5;assert (np.einsum('ij,ij->i',normal[valid],pts[valid].mean(1))>0).all()
assert np.isfinite(np.array(h.m_Normals)).all()
report['validation']={'script_transform_physics_collider_bytes_preserved':True,'roundtrip_all_changed_meshes_valid':True,'actual_ball_uv_range': [uv.min(0).tolist(),uv.max(0).tolist()], 'runtime_vr_tested':False}
(A/'art-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))


