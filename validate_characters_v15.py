import pathlib,sys,struct,json,math,shutil
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import UnityPy
f=UnityPy.load(str(R/'visuals-v15/sharedassets0.assets')).file
report=[]
for ident in json.loads((R/'visuals-v15/characters.json').read_text())['bot_mesh_ids']:
 d=f.objects[ident].read_typetree();v=d['m_VertexData'];count=v['m_VertexCount'];data=bytes(v['m_DataSize']);assert len(data)==count*80
 indices=struct.unpack('<'+'H'*(len(d['m_IndexBuffer'])//2),bytes(d['m_IndexBuffer']));assert max(indices)<count
 for i in range(count):
  row=struct.unpack_from('<16f4I',data,i*80);assert all(math.isfinite(x) for x in row[:16]);assert abs(sum(x*x for x in row[3:6])-1)<.01
  assert row[12:16]==(1.,0.,0.,0.) and row[16]<len(d['m_BindPose'])
 report.append({'mesh':ident,'vertices':count,'triangles':len(indices)//3})
for o in f.objects.values():
 if o.type.name=='SkinnedMeshRenderer':
  d=o.read_typetree()
  if d['m_Mesh']['m_PathID'] in [r['mesh'] for r in report]:assert d['m_AABB']['m_Extent']['y']>1.4
for source in (R/'visuals-v15').iterdir():
 if source.suffix=='.assets' or source.name.startswith('level'):shutil.copyfile(source,R/'working/VolleyballFever_Data'/source.name)
(R/'analysis/v15-character-validation.json').write_text(json.dumps({'passed':True,'meshes':report},indent=2))
print('Seven meshes validated; visual assets copied to working game.')
