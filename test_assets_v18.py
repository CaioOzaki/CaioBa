"""Check serialized new map/audio and preserved unrelated objects after reload."""
from pathlib import Path
import sys,json,io,wave,hashlib,numpy as np
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy,fmod_toolkit
W=R/'working/VolleyballFever_Data';B=R/'versions/cloudcourt-v17-antes-v18';A=R/'assets/audio-v18'
inventory=json.loads((R/'analysis/v18-audio-inventory.json').read_text());clips=0
for name in sorted({x['asset'] for x in inventory}):
 f=UnityPy.load(str(W/name)).file;old=UnityPy.load(str(B/name)).file;ids={x['id'] for x in inventory if x['asset']==name}
 assert f.objects.keys()==old.objects.keys()
 for i in ids:
  d=f.objects[i].read_typetree();resource=d['m_Resource'];bank=(W/resource['m_Source']).read_bytes();start=resource['m_Offset'];size=resource['m_Size'];blob=bank[start:start+size];assert blob[:4]==b'FSB5' and len(blob)==size
  data=next(iter(fmod_toolkit.raw_to_wav(blob,'test',1,22050).values()))
  with wave.open(io.BytesIO(data)) as wav:
   assert wav.getframerate()==d['m_Frequency']==22050 and wav.getnchannels()==d['m_Channels']==1
   pcm=wav.readframes(wav.getnframes());assert abs(wav.getnframes()/22050-d['m_Length'])<1e-4
  assert pcm==(A/f'{Path(name).stem}-{i}.wav').read_bytes()[44:]
  assert old.objects[i].read_typetree()['m_Resource']!=resource;clips+=1
 for i,o in old.objects.items():
  # Beach art is also deliberately changed; audio module must preserve others.
  if name in ['resources.assets','sharedassets0.assets','sharedassets2.assets','sharedassets4.assets'] and i not in ids:assert o.get_raw_data()==f.objects[i].get_raw_data(),(name,i)
f=UnityPy.load(str(W/'sharedassets1.assets')).file;old=UnityPy.load(str(B/'sharedassets1.assets')).file
for i,o in old.objects.items():
 if o.type.name=='Shader':assert o.get_raw_data()==f.objects[i].get_raw_data()
mesh=f.objects[29].read_typetree();count=mesh['m_VertexData']['m_VertexCount'];assert count==261 and len(mesh['m_IndexBuffer'])//6==512
verts=np.frombuffer(mesh['m_VertexData']['m_DataSize'],dtype='<f4').reshape(count,12)[:,:3];assert np.isfinite(verts).all();assert verts[:,1].max()>5 and verts[:,1].min()>=0
indices=np.frombuffer(bytes(mesh['m_IndexBuffer']),dtype='<u2');assert indices.max()<count
for name in ['level1','level2']:
 sf=UnityPy.load(str(W/name)).file;before=UnityPy.load(str(B/name)).file
 for i,o in before.objects.items():
  if 'Collider' in o.type.name:assert o.get_raw_data()==sf.objects[i].get_raw_data(),(name,i)
 palms=[o.read_typetree() for o in sf.objects.values() if o.type.name=='GameObject' and o.read().m_Name.startswith('Cloudcourt Fan Palm')];assert len(palms)==17
 for go in palms:
  components=[sf.objects[x['component']['m_PathID']] for x in go['m_Component']]
  for c in components:
   if c.type.name=='MeshFilter':assert c.read_typetree()['m_Mesh']['m_PathID']==29
   if c.type.name=='Transform':assert all(np.isfinite(list(c.read_typetree()[k].values())).all() for k in ['m_LocalPosition','m_LocalRotation','m_LocalScale'])
report={'passed':True,'audio_clips':clips,'all_external_banks_decoded':True,'non_audio_objects_preserved':True,'palm_triangles':512,'beach_shader_binaries_and_colliders_preserved':True}
(R/'analysis/v18-assets-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
