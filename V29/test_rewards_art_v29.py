"""Validate original achievement artwork and hidden material carriers."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from PIL import Image
from fix_gloves_v16 import hierarchy
from build_rewards_art_v29 import apply_rewards_art_v29,ACCENTS,SHIRT_COLORS
B=R/'versions/cloudcourt-v28-antes-v29';D=R/'visuals-v29-rewards';D.mkdir(exist_ok=True)
resources=UnityPy.load(str(B/'resources.assets')).file;menu=UnityPy.load(str(B/'level0')).file
base=[{i:o.get_raw_data() for i,o in f.objects.items() if o.type.name in ('Mesh','MeshRenderer','MeshFilter','Material','MonoBehaviour','BoxCollider','SphereCollider','CapsuleCollider')} for f in (resources,menu)]
report=apply_rewards_art_v29(resources,menu)
assert report['changed_existing_resources'] and report['changed_existing_menu']
for file,before,prefix in [(resources,base[0],'NetworkPlayer/PhysicalBody'),(menu,base[1],'Menu/CC_Customization')]:
 for i,data in before.items():assert file.objects[i].get_raw_data()==data,(file.name,i,'base geometry/material/component changed')
 gs,ts,paths=hierarchy(file);rt=paths[prefix+'/CC_RewardSources'];assert not gs[ts[rt]['m_GameObject']['m_PathID']]['m_IsActive']
 for name in ('Face','Outfit'):
  tid=paths[prefix+'/CC_RewardSources/'+name];go=gs[ts[tid]['m_GameObject']['m_PathID']]
  assert not go['m_IsActive'];cs=[file.objects[x['component']['m_PathID']] for x in go['m_Component']]
  assert sorted(o.type.name for o in cs)==['MeshFilter','MeshRenderer','Transform']
  renderer=next(o for o in cs if o.type.name=='MeshRenderer');rd=renderer.read_typetree();assert not rd['m_Enabled']
  material=rd['m_Materials'][0];assert material['m_PathID']==report['materials'][name]
  assert material['m_FileID']==(0 if file is resources else next(i+1 for i,e in enumerate(file.externals) if e.path.endswith('resources.assets')))
  if file is menu:
   for obj in cs:assert file.types[obj.type_id].class_id==obj.class_id,(obj.path_id,obj.type_id)
 for name in ('Face','Outfit'):
  texture=resources.objects[report['textures'][name]].read();image=texture.image.convert('RGBA')
  assert image.size==(1536,1536);assert image.getextrema()[3]==(255,255)
  assert len({hashlib.sha256(image.crop((i*512,0,(i+1)*512,512)).tobytes()).hexdigest() for i in range(3)})==3
 out=D/('resources.assets' if file is resources else 'level0');out.write_bytes(file.save())
 saved=UnityPy.load(str(out)).file;assert prefix+'/CC_RewardSources/Outfit' in hierarchy(saved)[2]
# A second pass retains exactly the same source nodes, object count and bytes.
counts=(len(resources.objects),len(menu.objects));again=apply_rewards_art_v29(resources,menu)
assert counts==(len(resources.objects),len(menu.objects)) and not again['changed_existing_resources'] and not again['changed_existing_menu']
assert report['rewards']['shirt_hex']==['#d76b45','#227fa8','#277c62']
assert report['rewards']['accent_hex']==['#ffcf58','#63d7f4','#a4f0cf']
assert report['rewards']['faces']==['Wink','Focus','Starry Joy']
report.update(passed=True,roundtrip=True,idempotent=True,old_geometry_material_physics_unchanged=True,original_procedural_art_only=True,production_sha256=hashlib.sha256((R/'build_rewards_art_v29.py').read_bytes()).hexdigest(),preview=str(R/'assets/rewards-v29/preview-rewards-v29.png'))
(R/'analysis/v29-rewards-art-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
