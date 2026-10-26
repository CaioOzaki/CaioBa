"""v22 cosmetic-only binary asset audit and original native visibility ordering."""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy,numpy as np,pefile,capstone
from build_hands_v22 import build_resources_v22
from fix_gloves_v16 import hierarchy

def run():
 before=UnityPy.load(str(R/'versions/cloudcourt-v21-antes-v22/resources.assets')).file
 f=UnityPy.load(str(R/'visuals-v22-hands/resources.assets')).file
 report=json.loads((R/'visuals-v22-hands/hands-v22-report.json').read_text());allowed=set(report['changed_existing_ids'])
 for i,o in before.objects.items():
  if i not in allowed:assert o.get_raw_data()==f.objects[i].get_raw_data(),(i,o.type.name)
  else:assert o.type.name in ('MeshFilter','Transform'),(i,o.type.name)
 for typ in ('Texture2D','MonoBehaviour','Rigidbody','BoxCollider','SphereCollider','CapsuleCollider','MeshCollider','Material'):
  assert all(o.get_raw_data()==f.objects[i].get_raw_data() for i,o in before.objects.items() if o.type.name==typ),typ
 meshes={}
 for rec in report['hands']:
  d=f.objects[rec['mesh']].read_typetree();v=np.frombuffer(bytes(d['m_VertexData']['m_DataSize']),'<f4').reshape(-1,12);tr=np.frombuffer(bytes(d['m_IndexBuffer']),'<u2').reshape(-1,3)
  assert np.isfinite(v).all() and tr.max()<len(v);assert np.allclose(np.linalg.norm(v[:,3:6],axis=1),1,atol=1e-5)
  c=np.array([d['m_LocalAABB']['m_Center'][x] for x in 'xyz']);ex=np.array([d['m_LocalAABB']['m_Extent'][x] for x in 'xyz']);assert (np.abs(v[:,:3]-c)<=ex+1e-6).all()
  meshes[rec['pose'],rec['side']]=(v,tr)
 for pose in ('Thumb','Set'):
  l,lt=meshes[pose,'L'];r,rt=meshes[pose,'R'];assert np.allclose(l[:,0],-r[:,0]) and np.allclose(l[:,1:3],r[:,1:3]);assert np.array_equal(lt[:,[0,2,1]],rt)
 l,_=meshes['Thumb','L'];assert .125<l[:,1].max()<.14 and l[:,2].max()<.102,'thumb must stand on +Y and curled fingers stay short on +Z'
 l,_=meshes['Set','L'];assert l[:,2].max()>.17 and l[:,1].min()<-.06 and l[:,0].max()>.03,'splayed/curved distinct set silhouette'
 g,t,p=hierarchy(f)
 for rec in report['hands']:
  tid=p[rec['path']];d=t[tid];parent=d['m_Father']['m_PathID'];assert g[t[parent]['m_GameObject']['m_PathID']]['m_Name']==f'Hand Root {rec["side"]}'
  assert all(abs(d['m_LocalPosition'][x])<1e-7 for x in 'xyz');assert d['m_LocalRotation']['w']==1
  go=g[d['m_GameObject']['m_PathID']];assert not go['m_IsActive']
  renderer=next(f.objects[x['component']['m_PathID']] for x in go['m_Component'] if f.objects[x['component']['m_PathID']].type.name=='MeshRenderer');assert renderer.read_typetree()['m_Enabled']
  assert {f.objects[x['component']['m_PathID']].type.name for x in go['m_Component']}=={'Transform','MeshFilter','MeshRenderer'}
 snapshot={i:o.get_raw_data() for i,o in f.objects.items()};build_resources_v22(f);assert set(snapshot)==set(f.objects);assert all(snapshot[i]==o.get_raw_data() for i,o in f.objects.items()),'idempotency'
 native=pefile.PE(str(R/'backup/GameAssembly.dll'));md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64)
 hand=list(md.disasm(native.get_data(0x312f60,0x13d),0x312f60));assert not any(q.mnemonic=='call' and q.op_str=='0x94f700' for q in hand),'Hand.Update does not touch visual activation'
 src=(R/'comfort_v14.c').read_text();assert src.index('avatar_update_trampoline(body,m);')<src.index('avatar_hands_v21(body);')
 result=dict(passed=True,changed_existing_ids=sorted(allowed),added_meshes=len(report['added_ids']),original_physics_tracking_colliders_materials_textures_fist_byte_identical=True,mesh_normals_bounds_indices_valid=True,left_right_geometry_winding_mirrored=True,thumb_up_on_correct_anatomical_axis=True,setting_spread_cupped_silhouette=True,renderers_enabled_root_siblings=True,native_Hand_Update_does_not_toggle_visuals=True,cosmetic_override_after_PhysicalBody_Update=True,idempotent=True)
 (R/'analysis/v22-hands-assets-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
