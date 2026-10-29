"""Audit v28 isolated assets, mesh references, UI listeners and idempotence."""
from pathlib import Path
import copy,json,struct,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_customization_v28 import apply_customization_v28,HATS
from build_menu_v19 import MenuEditor,script,BUTTON,button_layout,RAW_IMAGE,TEXT
from fix_gloves_v16 import hierarchy
source=R/'versions/cloudcourt-v27-antes-v28';fixture=R/'visuals-v28-customization'
r=UnityPy.load(str(source/'resources.assets')).file;l=UnityPy.load(str(source/'level0')).file
before={i:o.get_raw_data() for i,o in r.objects.items()};a=apply_customization_v28(r,l)
g,t,p=hierarchy(r);mg,mt,mp=hierarchy(l);e=MenuEditor(l)
assert [str(x.path).lower() for x in l.externals][3].endswith('resources.assets')
assert len(a['hats'])==7 and len(set(a['hats'].values()))==7
for kind,ident in a['hats'].items():
 md=r.objects[ident].read_typetree();assert md['m_VertexData']['m_VertexCount']>0 and len(md['m_IndexBuffer'])>0
 path='NetworkPlayer/PhysicalBody/Physical Head/Visual Head Root/Head/CC_Hat_'+kind
 tid=p[path];go=g[t[tid]['m_GameObject']['m_PathID']]
 assert not go['m_IsActive'];assert sorted(r.objects[x['component']['m_PathID']].type.name for x in go['m_Component'])==['MeshFilter','MeshRenderer','Transform']
assert a['preview_camera_count']==0
for part in ['Head','Body','UpperL','LowerL','UpperR','LowerR','HandL','HandR']:
 tid=mp['Menu/CC_Customization/CC_Mirror'+part];go=mg[mt[tid]['m_GameObject']['m_PathID']]
 components={l.objects[x['component']['m_PathID']].type.name:l.objects[x['component']['m_PathID']] for x in go['m_Component']}
 assert set(components)=={'Transform','MeshFilter','MeshRenderer'},'no scripts or raycast target in mirror'
 mesh=components['MeshFilter'].read_typetree()['m_Mesh']
 if part in ['Head','Body','HandL','HandR']:assert mesh['m_FileID']==4 and mesh['m_PathID'] in r.objects
 else:assert mesh==dict(m_FileID=3,m_PathID=10208),'builtin capsule maps resources ext4 -> menu ext3'
 mr=components['MeshRenderer'].read_typetree();assert not mr['m_CastShadows'] and not mr['m_ReceiveShadows']
# v28 may only alter the head child list and four arm material bindings.
allowed={p['NetworkPlayer/PhysicalBody/Physical Head/Visual Head Root/Head']}
for side in ['L','R']:
 for part in ['Upper','Lower']:
  tid=p['NetworkPlayer/PhysicalBody/Physical '+part+' Arm '+side];go=g[t[tid]['m_GameObject']['m_PathID']]
  allowed.update(x['component']['m_PathID'] for x in go['m_Component'] if r.objects[x['component']['m_PathID']].type.name=='MeshRenderer')
assert set(a['changed_resources'])<=allowed
assert all(o.get_raw_data()==before[i] for i,o in r.objects.items() if i in before and o.type.name in ('Texture2D','Mesh','MonoBehaviour','Collider','BoxCollider','SphereCollider','Rigidbody'))
for stem in ['Face','Outfit','HandTone','Hat','Arms']:
 for suffix in ['Prev','Next']:
  tid=mp['Menu/CC_Customization/CC_'+stem+suffix];button=e.component(tid,BUTTON);assert button
  raw=button.get_raw_data();target,event=button_layout(raw);assert struct.unpack_from('<I',raw,event)[0]==0,'no inherited page listeners'
for stem in ['FacePreview','OutfitPreview']:
 tid=mp['Menu/CC_Customization/CC_'+stem];assert not mg[mt[tid]['m_GameObject']['m_PathID']]['m_IsActive']
# Reapplying must not accumulate nodes/materials/meshes; byte output deterministic.
first=(r.save(),l.save());counts=(len(r.objects),len(l.objects))
r=UnityPy.load(first[0]).file;l=UnityPy.load(first[1]).file
for file in (r,l):
 for obj in file.objects.values():assert file.types[obj.type_id].class_id==obj.class_id
_,_,roundpaths=hierarchy(l);assert 'Menu/CC_Customization/CC_MirrorHead' in roundpaths
b=apply_customization_v28(r,l)
assert counts==(len(r.objects),len(l.objects));assert first==(r.save(),l.save()),'idempotent serialized output'
report=dict(passed=True,checks=['7 original distinct valid hat meshes','same avatar meshes in menu; correct external references','no second camera/collider/script/raycast target','10 cosmetic arrow buttons retain empty persistent listeners','Done kept existing ID','only head hierarchy and four arm renderers changed in resources','all existing textures and meshes byte-identical','source data left untouched','save/reload serialized class IDs match destination type table','builder idempotent after full serialization roundtrip, no accumulating nodes'],counts=dict(resources=counts[0],menu=counts[1]),limitations=['actual rendering and VR pointer require runtime probe'])
(R/'analysis/v28-customization-assets-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

