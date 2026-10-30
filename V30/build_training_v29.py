"""Original mesh target rings for four offline guided drills.

apply_training_v29(resources, scene) modifies only supplied in-memory files.
Call for level1/2/3. Targets are visual only and initially disabled. Runtime
uses existing GameRules TMP instruction/score/set labels for an in-match HUD.
"""
from pathlib import Path
import argparse, copy, json, math, sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from PIL import Image
from fix_gloves_v16 import hierarchy, _model_class
from build_landing_v20 import clone, save, ptr, raw

def ring_model(radius=1.,width=.045,height=.045,segments=64):
    m=_model_class()()
    # Closed annular extrusion, visible above/below and from a low eye angle.
    for y in (-height/2,height/2):
        for r in (radius-width/2,radius+width/2):
            for i in range(segments):
                a=2*math.pi*i/segments
                m.v.append([r*math.cos(a),y,r*math.sin(a)])
                m.n.append([0,1 if y>0 else -1,0]);m.uv.append([.5,.5]);m.b.append(0)
    for i in range(segments):
        j=(i+1)%segments
        for a,b,c,d in [(i,j,segments+j,segments+i),
                        (2*segments+i,3*segments+i,3*segments+j,2*segments+j),
                        (i,2*segments+i,2*segments+j,j),
                        (segments+i,segments+j,3*segments+j,3*segments+i)]:
            m.tri.extend([(a,b,c),(a,c,d),(c,b,a),(d,c,a)])
    return m

def apply_training_v29(resources,scene):
    gs,ts,paths=hierarchy(scene)
    if 'CC_TrainingTargets' in paths:return {'created':False,'idempotent':True}
    before={i:o.get_raw_data() for i,o in scene.objects.items()}
    source_go=next(scene.objects[i] for i in gs)
    source_t=next(o for o in scene.objects.values() if o.type.name=='Transform')
    source_renderer=next(o for o in scene.objects.values() if o.type.name=='MeshRenderer')
    source_filter=next(o for o in scene.objects.values() if o.type.name=='MeshFilter')
    dependency=next(i for i,e in enumerate(scene.externals,1) if e.path.replace('\\','/').rsplit('/',1)[-1].lower()=='resources.assets')
    go=clone(scene,source_go);root=clone(scene,source_t)
    gd=go.read_typetree();gd.update(m_Name='CC_TrainingTargets',m_Component=[{'component':ptr(root.path_id)}],m_IsActive=True,m_Layer=0,m_TagString='Untagged',m_StaticEditorFlags=0);save(go,gd)
    td=root.read_typetree();td.update(m_GameObject=ptr(go.path_id),m_Father=ptr(0),m_Children=[],m_LocalPosition=dict(x=0.,y=0.,z=0.),m_LocalRotation=dict(x=0.,y=0.,z=0.,w=1.),m_LocalScale=dict(x=1.,y=1.,z=1.));save(root,td)
    model=ring_model();mesh=clone(scene,resources.objects[67],model.serialize(resources.objects[67].read_typetree(),'Cloudcourt Training Target Ring',False))
    origin_model=ring_model(.38,.055,.025,48);origin_mesh=clone(scene,resources.objects[67],origin_model.serialize(resources.objects[67].read_typetree(),'Cloudcourt Training Standing Ring',False))
    records=[]
    for name,color in [('GroundTarget',(255,199,53,255)),('AirTarget',(255,199,53,255)),('Origin',(54,196,255,255))]:
        texture=clone(scene,next(o for o in resources.objects.values() if o.type.name=='Texture2D'))
        tex=texture.read();tex.m_Name='Cloudcourt Training '+name;tex.set_image(Image.new('RGBA',(4,4),color),mipmap_count=1,target_format=4);tex.save();raw(texture,texture.data)
        md=copy.deepcopy(resources.objects[26].read_typetree());md.update(m_Name='Cloudcourt Training '+name,m_Shader=ptr(74,dependency),m_ShaderKeywords='',m_CustomRenderQueue=2001)
        md['m_SavedProperties']['m_TexEnvs']=[('_MainTex',dict(m_Texture=ptr(texture.path_id),m_Scale=dict(x=1.,y=1.),m_Offset=dict(x=0.,y=0.)))]
        md['m_SavedProperties']['m_Colors']=[('_Color',dict(r=1.,g=1.,b=1.,a=1.))]
        mat=clone(scene,resources.objects[26],md)
        child=clone(scene,source_go);tr=clone(scene,source_t);renderer=clone(scene,source_renderer);mf=clone(scene,source_filter)
        gd=child.read_typetree();gd.update(m_Name=name,m_Component=[{'component':ptr(o.path_id)} for o in (tr,renderer,mf)],m_IsActive=False,m_Layer=0,m_TagString='Untagged',m_StaticEditorFlags=0);save(child,gd)
        d=tr.read_typetree();d.update(m_GameObject=ptr(child.path_id),m_Father=ptr(root.path_id),m_Children=[],m_LocalPosition=dict(x=0.,y=.025,z=0.),m_LocalRotation=dict(x=0.,y=0.,z=0.,w=1.),m_LocalScale=dict(x=1.,y=1.,z=1.));save(tr,d)
        rd=renderer.read_typetree();rd.update(m_GameObject=ptr(child.path_id),m_Enabled=True,m_Materials=[ptr(mat.path_id)],m_CastShadows=0,m_ReceiveShadows=False,m_LightProbeUsage=0,m_ReflectionProbeUsage=0,m_LightmapIndex=65535,m_LightmapIndexDynamic=65535,m_StaticBatchInfo=dict(firstSubMesh=0,subMeshCount=0),m_StaticBatchRoot=ptr(0),m_ProbeAnchor=ptr(0),m_LightProbeVolumeOverride=ptr(0));save(renderer,rd)
        fd=mf.read_typetree();fd.update(m_GameObject=ptr(child.path_id),m_Mesh=ptr(origin_mesh.path_id if name=='Origin' else mesh.path_id));save(mf,fd)
        td['m_Children'].append(ptr(tr.path_id));records.append(dict(name=name,transform=tr.path_id,mesh=fd['m_Mesh']['m_PathID'],rgba=color))
    save(root,td)
    changed=[i for i,old in before.items() if scene.objects[i].get_raw_data()!=old]
    assert not changed,'Target authoring must only add objects, never edit existing court physics/art'
    return dict(created=True,root=root.path_id,markers=records,new_objects=len(scene.objects)-len(before),existing_objects_changed=changed,colliders_added=0,scripts_added=0,targets_initially_active=False,visual_radius_metres=1.,native_hud='GameRules.uiText/scoreText/setText')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=R/'versions/cloudcourt-v28-antes-v29');ap.add_argument('--output',type=Path,default=R/'visuals-v29-training');args=ap.parse_args()
    args.output.mkdir(exist_ok=True);resources=UnityPy.load(str(args.input/'resources.assets')).file;report=[]
    for name in ('level1','level2','level3'):
        scene=UnityPy.load(str(args.input/name)).file;result=apply_training_v29(resources,scene);(args.output/name).write_bytes(scene.save());report.append(dict(scene=name,**result))
    (R/'analysis/v29-training-assets.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
