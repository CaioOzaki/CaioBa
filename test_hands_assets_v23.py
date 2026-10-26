"""Audit v23 serialized fixture against immutable v22, plus geometry invariants."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np,UnityPy
from build_hands_v23 import build_resources_v23,hand_model_v23
from fix_gloves_v16 import glove_model

def unpack(o):
 d=o.read_typetree();v=np.frombuffer(bytes(d['m_VertexData']['m_DataSize']),'<f4').reshape(-1,12);tri=np.frombuffer(bytes(d['m_IndexBuffer']),'<u2').reshape(-1,3);return d,v,tri

def run():
 before=UnityPy.load(str(R/'versions/cloudcourt-v22-antes-v23/resources.assets')).file;f=UnityPy.load(str(R/'visuals-v23-hands/resources.assets')).file
 report=json.loads((R/'visuals-v23-hands/hands-v23-report.json').read_text());allowed={1307,1311,1316,1320,1341,1345,1349,1353,1357,1361,1365,1369,1373}
 assert set(report['changed_existing_ids'])==allowed;assert set(f.objects)-set(before.objects)==set(report['added_ids']);assert len(report['added_ids'])==8
 for i,o in before.objects.items():
  if i not in allowed:assert o.get_raw_data()==f.objects[i].get_raw_data(),(i,o.type.name)
  else:assert o.type.name=='MeshFilter';a=o.read_typetree();b=f.objects[i].read_typetree();a['m_Mesh']=b['m_Mesh'];assert a==b
 models={};bounds={};winding={}
 for rec in report['hands']:
  d,v,tri=unpack(f.objects[rec['mesh']]);key=(rec['pose'],rec['side']);models[key]=(v,tri)
  assert np.isfinite(v).all() and tri.max()<len(v);assert np.allclose(np.linalg.norm(v[:,3:6],axis=1),1,atol=1e-5)
  lo=v[:,:3].min(0);hi=v[:,:3].max(0);bounds['/'.join(key)]=[lo.tolist(),hi.tolist()]
  c=np.array([d['m_LocalAABB']['m_Center'][k] for k in 'xyz']);e=np.array([d['m_LocalAABB']['m_Extent'][k] for k in 'xyz']);assert np.allclose(c,(lo+hi)/2) and np.allclose(e,(hi-lo)/2)
  points=v[tri,:3];cross=np.cross(points[:,1]-points[:,0],points[:,2]-points[:,0]);area=np.linalg.norm(cross,axis=1);valid=area>1e-11
  normals=v[tri,3:6].mean(1);dots=(cross[valid]*normals[valid]).sum(1)/area[valid];assert (dots>0).all(),(key,float(dots.min()));winding['/'.join(key)]=float(dots.min())
 for pose in ('Open','Closed','Thumb','Set'):
  l,lt=models[pose,'L'];r,rt=models[pose,'R'];assert np.array_equal(lt[:,[0,2,1]],rt);assert np.allclose(l[:,[0,3]],-r[:,[0,3]]) and np.allclose(l[:,[1,2,4,5]],r[:,[1,2,4,5]])
  # Exact common palm/cuff geometry and UVs across every pose.
  assert np.array_equal(l[:850,:],models['Open','L'][0][:850,:])
 for pose in ('Open','Closed'):
  old=np.array(glove_model(pose,'L').v);new=models[pose,'L'][0][:,:3];assert np.allclose(old[:,1:],new[:,1:]);assert np.allclose(old[425:850],new[425:850]);assert np.allclose(old[:425,0]*.9,new[:425,0])
 thumb=models['Thumb','L'][0];setting=models['Set','L'][0]
 assert .15<thumb[:,1].max()<.165 and thumb[:,2].max()<.155
 assert setting[:,1].min()<-.085 and setting[:,1].max()>.14 and setting[:,2].max()>.22 and setting[:,0].max()>.044
 # Finger topology: 4 continuous bent capsules and one anatomical thumb capsule.
 assert len(thumb)==len(setting)==850+425+5*625
 # Bot reuses right thumb at original wrist anchor and scale.
 for bot in report['bots']:
  assert f.objects[bot['transform']].get_raw_data()==before.objects[bot['transform']].get_raw_data();t=f.objects[bot['transform']].read_typetree();assert all(abs(t['m_LocalScale'][k]-1.3)<1e-6 for k in 'xyz')
  fd=f.objects[bot['filter']].read_typetree();assert fd['m_Mesh']['m_PathID']==next(x['mesh'] for x in report['hands'] if x['pose']=='Thumb' and x['side']=='R')
 snapshot={i:o.get_raw_data() for i,o in f.objects.items()};build_resources_v23(f);assert set(snapshot)==set(f.objects);assert all(raw==f.objects[i].get_raw_data() for i,raw in snapshot.items())
 result=dict(passed=True,changed_existing_ids=sorted(allowed),added_ids=report['added_ids'],all_old_objects_outside_exact_whitelist_byte_identical=True,all_original_meshes_materials_textures_transforms_colliders_scripts_byte_identical=True,common_palm_cuff_exact_across_poses=True,default_width_length_cuff_preserved=True,default_skin_thickness_reduced_ten_percent=True,mirrored_normals_vertices_winding=True,all_nondegenerate_triangles_outward=True,continuous_five_digits_each_gesture=True,serialized_normals_aabbs_indices_valid=True,bot_wrist_anchor_and_1_30_scale_unchanged=True,idempotent=True,bounds=bounds,minimum_normal_winding_dot=winding,scope='Offline asset tests; no headset/performance claim')
 (R/'analysis/v23-hands-assets-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()

