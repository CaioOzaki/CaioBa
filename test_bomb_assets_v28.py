"""Isolated Bomb roster builder: serialized geometry, ownership and budget."""
from pathlib import Path
import hashlib,json,struct,sys,tempfile
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from build_bomb_v28 import apply_bomb_v28

def run():
 source=R/'versions/cloudcourt-v27-antes-v28/resources.assets'
 if not source.exists():source=R/'working/VolleyballFever_Data/resources.assets'
 f=UnityPy.load(str(source)).file;before={i:o.get_raw_data() for i,o in f.objects.items()};report=apply_bomb_v28(f)
 assert report['original_rules_visuals_and_serve_points_identical']
 assert sorted(report['changed_existing_ids'])==[502,508,512,521,541,1209,1212,1221,1242]
 assert len(report['added_ids'])==30
 assert all(f.objects[i].type.name in ('GameObject','Transform','MonoBehaviour') for i in report['added_ids'])
 assert all(f.objects[i].type.name not in ('MeshRenderer','MeshFilter','SphereCollider','BoxCollider','Rigidbody') for i in report['added_ids'])
 def pptr(b,o):assert struct.unpack_from('<i',b,o)[0]==0;return struct.unpack_from('<q',b,o+4)[0]
 for team in report['teams']:
  areas=team['areas'];assert len(set(areas))==4
  for slot,aid in enumerate(areas):
   b=f.objects[aid].get_raw_data();assert pptr(b,44)==areas[(slot+1)%4]
   assert struct.unpack_from('<3f',b,32)==(2.,2.,2.25) and b[68]==(slot==0)
   go=f.objects[pptr(b,0)].read_typetree();tid=next(c['component']['m_PathID'] for c in go['m_Component'] if f.objects[c['component']['m_PathID']].type.name=='Transform')
   t=f.objects[tid].read_typetree();parent=f.objects[t['m_Father']['m_PathID']].read_typetree();world_z=t['m_LocalPosition']['z']+parent['m_LocalPosition']['z']
   assert abs(world_z)<4.5 and abs(t['m_LocalPosition']['x'])<2
   d=f.objects[pptr(b,56)].read_typetree();assert d['m_Father']['m_PathID']==tid
   assert abs(d['m_LocalPosition']['x'])<.001 and abs(d['m_LocalPosition']['z'])<.001
 # Rerunning is idempotent, and a serialized reload preserves every added node.
 first=f.save();again=apply_bomb_v28(f);assert not again['changed_existing_ids'] and not again['added_ids']
 loaded=UnityPy.load(first).file
 assert set(loaded.objects)==set(f.objects)
 assert all(loaded.objects[i].get_raw_data()==o.get_raw_data() for i,o in f.objects.items())
 result=dict(passed=True,report=report,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),checks=['original Bomb field visuals/serve points unchanged','nine permitted existing Bomb nodes only','30 new GO/Transform/area nodes','zero new renderer/collider/rigidbody','four distinct owned area slots per team','closed four-position rotation cycle','serving slot retained','all initial/default positions within compact field','serialized roundtrip','idempotent second build'],scope='Serialized asset inspection, not live Unity scene/VR playtesting.')
 (R/'analysis/v28-bomb-assets-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
