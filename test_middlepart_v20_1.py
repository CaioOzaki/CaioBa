"""Exact pre-v20 BOT1 geometry, narrow asset delta and unchanged release files."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from restore_middlepart_v20_1 import restore
H=lambda data:hashlib.sha256(data).hexdigest()
prior=R/'versions/cloudcourt-v20-antes-middlepart';target=R/'working/VolleyballFever_Data/sharedassets0.assets'
before=UnityPy.load(str(prior/'sharedassets0.assets')).file;after=UnityPy.load(str(target)).file
legacy=UnityPy.load(str(R/'versions/cloudcourt-v19-antes-v20/sharedassets0.assets')).file
assert set(before.objects)==set(after.objects)
changes=sorted(i for i,o in before.objects.items() if o.get_raw_data()!=after.objects[i].get_raw_data())
assert changes==[3569,4235,4243,4322],changes
new=after.objects[4322].read_typetree();old=legacy.objects[4322].read_typetree();v20=before.objects[4322].read_typetree()
for key in ('m_VertexData','m_IndexBuffer','m_SubMeshes','m_LocalAABB','m_BindPose','m_BonesAABB','m_StreamData'):
 assert new[key]==old[key],key
stride=len(new['m_VertexData']['m_DataSize'])//new['m_VertexData']['m_VertexCount']
assert new['m_VertexData']['m_DataSize'][:6194*stride]==v20['m_VertexData']['m_DataSize'][:6194*stride],'Body changed.'
for ident in (3569,4235,4243):
 a=after.objects[ident].read_typetree();b=before.objects[ident].read_typetree();a.pop('m_AABB');b.pop('m_AABB');assert a==b
assert all(after.objects[i].get_raw_data()==o.get_raw_data() for i,o in before.objects.items() if o.type.name in ('Texture2D','Material','Transform','MonoBehaviour') or 'Collider' in o.type.name)
snapshot=after.save();assert not restore(after)['changed_ids'] and after.save()==snapshot
manifest=json.loads((R/'distribution/Cloudcourt-v20-personagens-menu/patch.json').read_text())
unchanged=[]
for row in manifest['files']:
 if Path(row['path']).name=='sharedassets0.assets':continue
 assert H((R/'working'/row['path']).read_bytes())==row['modified_sha256'],row['path'];unchanged.append(row['path'])
report=dict(passed=True,changed_ids=changes,pre_v20_mesh_byte_fields_exact=True,body_vertex_bytes_unchanged=True,
 textures_materials_physics_rig_unchanged=True,idempotent=True,other_release_files_unchanged=len(unchanged),
 native_DLL_unchanged=True,online_namespace='Cloudcourt-2v2-v20 / Cloudcourt-4v4-v20',VR_playtest=False)
(R/'analysis/v20-1-middlepart-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
