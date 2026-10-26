"""Restore only BOT1's preferred pre-v20 geometry, retaining v20 everywhere else."""
from pathlib import Path
import copy,hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from PIL import Image,ImageDraw,ImageFont
from build_bots_v20 import authoring,character,put,A,NAMES

def restore(file):
 scope=authoring();model,hair_start=character(scope,0)
 mesh=next(o for o in file.objects.values() if o.type.name=='Mesh' and o.read_typetree()['m_Name']=='Cloudcourt_Bot_1')
 before={i:o.get_raw_data() for i,o in file.objects.items()}
 put(mesh,model.serialize(mesh.read_typetree(),'Cloudcourt_Bot_1',True));renderers=[]
 for obj in file.objects.values():
  if obj.type.name!='SkinnedMeshRenderer':continue
  data=obj.read_typetree()
  if data['m_Mesh']==dict(m_FileID=0,m_PathID=mesh.path_id):
   data['m_AABB']=scope['aabb'](model.v);put(obj,data);renderers.append(obj.path_id)
 changed=sorted(i for i,o in file.objects.items() if o.get_raw_data()!=before[i])
 assert set(changed).issubset({mesh.path_id,*renderers}) and len(renderers)==3
 return dict(mesh_id=mesh.path_id,renderer_ids=renderers,changed_ids=changed,
  vertices=len(model.v),triangles=len(model.tri),hair_vertex_range=[hair_start,len(model.v)])

def previews(report):
 scope=authoring();model,_=character(scope,0);atlas=Image.open(A/'bot-01-atlas.png').convert('RGB')
 front=copy.deepcopy(model);front.v=[[x*.94,y*.94,z*.94] for x,y,z in model.v]
 scope['render_model'](front,atlas,500).save(A/'bot-01-modelo.png')
 back=copy.deepcopy(model);back.v=[[-x*.94,y*.94,-z*.94] for x,y,z in model.v];back.n=[[-x,y,-z] for x,y,z in model.n]
 scope['render_model'](back,atlas,400).save(A/'bot-01-costas.png')
 gallery=Image.new('RGB',(1500,1800),'#e4ebed');draw=ImageDraw.Draw(gallery)
 font=ImageFont.truetype(str(R/'assets/cloudcourt-v16/CloudcourtBubble.ttf'),24)
 for i in range(9):
  x=i%3*500;y=i//3*600;gallery.paste(Image.open(A/f'bot-{i+1:02d}-modelo.png'),(x,y))
  draw.text((x+250,y+535),f'{i+1}. {NAMES[i]}',font=font,fill='#172b46',anchor='mm')
 gallery.save(A/'bots-gallery.png')
 for name in ('catalog.json','unity-bindings.json'):
  path=A/name;data=json.loads(path.read_text());data['vertices'][0]=report['vertices'];data['triangles'][0]=report['triangles'];data['hair_vertex_ranges'][0]=report['hair_vertex_range'];data['bot_1_hair_reference']='Pre-v20 middle part restored at user request'
  path.write_text(json.dumps(data,indent=2),encoding='utf-8')

if __name__=='__main__':
 target=R/'working/VolleyballFever_Data/sharedassets0.assets';file=UnityPy.load(str(target)).file
 report=restore(file);target.write_bytes(file.save());previews(report)
 report.update(sha256=hashlib.sha256(target.read_bytes()).hexdigest(),live_game_modified=False)
 (R/'analysis/v20-1-middlepart-build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
