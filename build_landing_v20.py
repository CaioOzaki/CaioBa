"""Two tiny original annulus renderers per court; never add gameplay colliders."""
from pathlib import Path
import copy,json,math,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from UnityPy.streams import EndianBinaryReader
from PIL import Image
from fix_gloves_v16 import _model_class,hierarchy

def ptr(i,f=0):return dict(m_FileID=f,m_PathID=i)
def raw(obj,data):
 obj.set_raw_data(bytes(data));obj.reader=EndianBinaryReader(bytes(data),endian=obj.reader.endian);obj.byte_start=0;obj.byte_size=len(data)
def save(obj,data):obj.save_typetree(data);raw(obj,obj.data)
def clone(dest,source,data=None):
 obj=copy.copy(source);obj.assets_file=dest;obj.path_id=max(dest.objects)+1
 match=next((i for i,t in enumerate(dest.types) if t.class_id==source.class_id and t.script_type_index==source.serialized_type.script_type_index and getattr(t,'script_id',None)==getattr(source.serialized_type,'script_id',None)),None)
 if match is None:match=len(dest.types);dest.types.append(copy.deepcopy(source.serialized_type))
 obj.type_id=match;obj.serialized_type=dest.types[match];raw(obj,source.get_raw_data());dest.objects[obj.path_id]=obj
 if data is not None:save(obj,data)
 return obj

def annulus():
 model=_model_class()()
 for i in range(49):
  a=2*math.pi*i/48
  for radius in (.22,.29):
   model.v.append([radius*math.cos(a),0,radius*math.sin(a)])
   model.n.append([0,1,0]);model.uv.append([.5,.5]);model.b.append(0)
 for i in range(48):
  a=2*i;model.tri.extend([(a,a+2,a+1),(a+1,a+2,a+3)])
 return model

def external_index(scene,name,template_file=None):
 for i,e in enumerate(scene.externals,1):
  if e.path.replace('\\','/').rsplit('/',1)[-1].lower()==name.lower():return i
 assert template_file is not None
 entry=next(e for e in template_file.externals if e.path.replace('\\','/').rsplit('/',1)[-1].lower()==name.lower())
 scene.externals.append(copy.deepcopy(entry));return len(scene.externals)

def add_landing_marks(scene,resources):
 gs,ts,paths=hierarchy(scene)
 if 'CC_LandingMarks' in paths:return {'created':False,'idempotent':True}
 first_go=next(scene.objects[i] for i in gs)
 first_t=next(o for o in scene.objects.values() if o.type.name=='Transform')
 first_renderer=next(o for o in scene.objects.values() if o.type.name=='MeshRenderer')
 first_filter=next(o for o in scene.objects.values() if o.type.name=='MeshFilter')
 root_go=clone(scene,first_go);root_t=clone(scene,first_t)
 gd=root_go.read_typetree();gd.update(m_Name='CC_LandingMarks',m_Component=[{'component':ptr(root_t.path_id)}],m_IsActive=True,m_Layer=0,m_TagString='Untagged',m_StaticEditorFlags=0);save(root_go,gd)
 td=root_t.read_typetree();td.update(m_GameObject=ptr(root_go.path_id),m_Father=ptr(0),m_Children=[],m_LocalPosition=dict(x=0.,y=0.,z=0.),m_LocalRotation=dict(x=0.,y=0.,z=0.,w=1.),m_LocalScale=dict(x=1.,y=1.,z=1.));save(root_t,td)
 model=annulus();mesh=clone(scene,resources.objects[67],model.serialize(resources.objects[67].read_typetree(),'Cloudcourt Landing Ring',False))
 dependency=external_index(scene,'resources.assets',UnityPy.load(str(R/'versions/cloudcourt-v19-antes-v20/level0')).file)
 records=[]
 for name,color in [('In',(34,222,96,255)),('Out',(248,55,64,255))]:
  texture=clone(scene,next(o for o in resources.objects.values() if o.type.name=='Texture2D'))
  tex=texture.read();tex.m_Name='Cloudcourt Landing '+name;tex.set_image(Image.new('RGBA',(4,4),color),mipmap_count=1,target_format=4);tex.save();raw(texture,texture.data)
  md=copy.deepcopy(resources.objects[26].read_typetree());md['m_Name']='Cloudcourt Landing '+name;md['m_Shader']=ptr(74,dependency);md['m_ShaderKeywords']='';md['m_CustomRenderQueue']=2001
  md['m_SavedProperties']['m_TexEnvs']=[('_MainTex',dict(m_Texture=ptr(texture.path_id),m_Scale=dict(x=1.,y=1.),m_Offset=dict(x=0.,y=0.)))]
  md['m_SavedProperties']['m_Colors']=[('_Color',dict(r=1.,g=1.,b=1.,a=1.))]
  mat=clone(scene,resources.objects[26],md)
  go=clone(scene,first_go);t=clone(scene,first_t);renderer=clone(scene,first_renderer);mf=clone(scene,first_filter)
  gd=go.read_typetree();gd.update(m_Name=name,m_Component=[{'component':ptr(o.path_id)} for o in (t,renderer,mf)],m_IsActive=False,m_Layer=0,m_TagString='Untagged',m_StaticEditorFlags=0);save(go,gd)
  d=t.read_typetree();d.update(m_GameObject=ptr(go.path_id),m_Father=ptr(root_t.path_id),m_Children=[],m_LocalPosition=dict(x=0.,y=.014,z=0.),m_LocalRotation=dict(x=0.,y=0.,z=0.,w=1.),m_LocalScale=dict(x=1.,y=1.,z=1.));save(t,d)
  rd=renderer.read_typetree();rd.update(m_GameObject=ptr(go.path_id),m_Enabled=True,m_Materials=[ptr(mat.path_id)],m_CastShadows=0,m_ReceiveShadows=False,m_LightProbeUsage=0,m_ReflectionProbeUsage=0,m_LightmapIndex=65535,m_LightmapIndexDynamic=65535,m_StaticBatchInfo=dict(firstSubMesh=0,subMeshCount=0),m_StaticBatchRoot=ptr(0),m_ProbeAnchor=ptr(0),m_LightProbeVolumeOverride=ptr(0));save(renderer,rd)
  fd=mf.read_typetree();fd.update(m_GameObject=ptr(go.path_id),m_Mesh=ptr(mesh.path_id));save(mf,fd)
  td['m_Children'].append(ptr(t.path_id));records.append({'name':name,'transform':t.path_id,'material':mat.path_id,'rgba':color})
 save(root_t,td)
 return {'created':True,'root':root_t.path_id,'markers':records,'vertices':len(model.v),'triangles':len(model.tri),'colliders_added':0,'active_markers_initial':0,'shared_mesh':mesh.path_id}

if __name__=='__main__':
 resources=UnityPy.load(str(R/'versions/cloudcourt-v19-antes-v20/resources.assets')).file
 out=R/'visuals-v20-landing';out.mkdir(exist_ok=True);reports=[]
 for name in ['level1','level2','level3']:
  scene=UnityPy.load(str(R/'versions/cloudcourt-v19-antes-v20'/name)).file
  report=add_landing_marks(scene,resources);(out/name).write_bytes(scene.save());reports.append({'scene':name,**report})
 (R/'analysis/v20-landing-assets.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
