"""Narrow, in-memory v21 venue artwork. No live installation or legacy rebuild.

All mesh positions and artwork below are original procedural Cloudcourt work.
Call build_environment_assets(files); caller owns serialization and integration.
"""
from pathlib import Path
import ast, copy, json, math, struct, sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import numpy as np, UnityPy
from PIL import Image, ImageDraw
from build_bots_v20 import put, readable
from fix_gloves_v16 import hierarchy

def ptr(i,f=0):return dict(m_FileID=f,m_PathID=i)
def vec(x,y,z):return dict(x=float(x),y=float(y),z=float(z))
def rgba(s):return dict(zip('rgba',[int(s[k:k+2],16)/255 for k in (1,3,5)]+[1.]))
def snapshot(f):return {i:o.get_raw_data() for i,o in f.objects.items()}
def delta(f,b):return sorted(i for i,o in f.objects.items() if i not in b or o.get_raw_data()!=b[i])
def set_rgb_full_mips(texture,image):
    """UnityPy stops at 4x4 even for RGB24; explicitly encode 2x2 and 1x1."""
    from UnityPy.export import Texture2DConverter
    image=image.convert('RGB');texture.set_image(image,target_format=3,mipmap_count=1)
    data=texture.image_data;w,h=image.size;count=1
    while w>1 or h>1:
        w,h=max(1,w//2),max(1,h//2)
        level=image.resize((w,h),Image.Resampling.LANCZOS)
        data+=Texture2DConverter.image_to_texture2d(level,3)[0];count+=1
    texture.image_data=data;texture.m_CompleteImageSize=len(data);texture.m_MipCount=count
    if texture.m_MipMap is not None:texture.m_MipMap=True
def geometry_class():
    tree=ast.parse((R/'build_caioba_maps.py').read_text())
    tree.body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ('Geometry','aabb','vec')]
    scope=dict(np=np,copy=copy,struct=struct,A=R/'assets/environment-v21')
    exec(compile(tree,'own_cloudcourt_geometry','exec'),scope)
    return scope['Geometry']
def clone(f,source,data):
    o=copy.copy(source);o.assets_file=f;o.path_id=max(f.objects)+1
    o.set_raw_data(source.get_raw_data());readable(o);f.objects[o.path_id]=o;put(o,data);return o.path_id
def material(f,template,name,color,shader=None,texture=0):
    d=copy.deepcopy(template.read_typetree());d['m_Name']=name
    if shader:d['m_Shader']=shader
    d['m_ShaderKeywords']='';d['m_CustomRenderQueue']=-1
    d['m_SavedProperties']={'m_TexEnvs':[('_MainTex',dict(m_Texture=ptr(texture),m_Scale=dict(x=1.,y=1.),m_Offset=dict(x=0.,y=0.)))],
      'm_Floats':[('_Glossiness',0.),('_Metallic',0.),('_Mode',0.),('_SrcBlend',1.),('_DstBlend',0.),('_ZWrite',1.)],
      'm_Colors':[('_Color',rgba(color)),('_EmissionColor',rgba('#000000'))]}
    return d
def visual(f,name,mesh,materials,templates=None):
    gs,ts,paths=hierarchy(f)
    existing=paths.get(name)
    if existing:
        g=gs[ts[existing]['m_GameObject']['m_PathID']]
        mf=next(f.objects[c['component']['m_PathID']] for c in g['m_Component'] if f.objects[c['component']['m_PathID']].type.name=='MeshFilter')
        mr=next(f.objects[c['component']['m_PathID']] for c in g['m_Component'] if f.objects[c['component']['m_PathID']].type.name=='MeshRenderer')
        d=mf.read_typetree();d['m_Mesh']=ptr(mesh);put(mf,d)
        d=mr.read_typetree();d['m_Materials']=[ptr(i) for i in materials];put(mr,d)
        return [g['m_Component'][0]['component']['m_PathID'],mf.path_id,mr.path_id]
    if templates is None:
        t=next(i for i,d in ts.items() if f.objects[i].type.name=='Transform' and any(f.objects[c['component']['m_PathID']].type.name=='MeshFilter' for c in gs[d['m_GameObject']['m_PathID']]['m_Component']))
        g=gs[ts[t]['m_GameObject']['m_PathID']]
        templates=[f.objects[ts[t]['m_GameObject']['m_PathID']],f.objects[t]]+[next(f.objects[c['component']['m_PathID']] for c in g['m_Component'] if f.objects[c['component']['m_PathID']].type.name==typ) for typ in ('MeshFilter','MeshRenderer')]
    go,tr,mf,mr=templates;d=copy.deepcopy(go.read_typetree());d.update(m_Name=name,m_IsActive=True,m_Component=[])
    gid=clone(f,go,d);t=copy.deepcopy(tr.read_typetree());t.update(m_GameObject=ptr(gid),m_Father=ptr(0),m_Children=[],m_LocalPosition=vec(0,0,0),m_LocalScale=vec(1,1,1),m_LocalRotation=dict(x=0.,y=0.,z=0.,w=1.))
    tid=clone(f,tr,t);ids=[tid]
    m=copy.deepcopy(mf.read_typetree());m.update(m_GameObject=ptr(gid),m_Mesh=ptr(mesh));ids.append(clone(f,mf,m))
    r=copy.deepcopy(mr.read_typetree());r.update(m_GameObject=ptr(gid),m_Materials=[ptr(i) for i in materials],m_Enabled=True,m_CastShadows=0,m_ReceiveShadows=1,m_StaticBatchInfo=dict(firstSubMesh=0,subMeshCount=0),m_StaticBatchRoot=ptr(0),m_LightmapIndex=65535)
    ids.append(clone(f,mr,r));d['m_Component']=[{'component':ptr(i)} for i in ids];put(f.objects[gid],d);return [gid]+ids
def named(f,typ,name):return next((o for o in f.objects.values() if o.type.name==typ and o.read_typetree().get('m_Name')==name),None)
def owned_mesh(f,template,model,name):
    old=named(f,'Mesh',name)
    data=model.serial((old or template).read_typetree(),name)
    # Geometry writes 56-byte P/N/tangent/UV0/UV1 vertices. The palm schema
    # has only UV0 (48 bytes); explicitly declare UV1 before reusing it.
    data['m_VertexData']['m_Channels'][5]=dict(stream=0,offset=48,format=0,dimension=2)
    if old:put(old,data);return old.path_id
    return clone(f,template,data)
def owned_material(f,template,name,color,shader=None,texture=0):
    d=material(f,template,name,color,shader,texture);old=named(f,'Material',name)
    if old:put(old,d);return old.path_id
    return clone(f,template,d)

def skyline_geometry():
    """Single shared 4-material mesh: promenade and landward skyline, no colliders."""
    g=geometry_class()(4)
    # Ocean remains east (+X). City and broad promenade are landward (-X),
    # beyond the existing flat play/runoff rectangle |X|<=12, |Z|<=18.
    g.box(0,(-36,.16,0),(7,.24,132))
    for x in (-39.7,-32.3):g.box(1,(x,.38,0),(.25,.35,132))
    blocks=[]
    for i in range(17):
        z=-64+i*8;w=4.5+(i%3)*1.1;h=9+(i*7%15);x=-43-(i%3)*2.8
        g.box(2,(x,h/2-.8,z),(w,h,5.7));g.box(1,(x,h-.55,z),(w+.35,.35,6.05))
        # Windows are merged strips, not individual objects or transparent cards.
        for y in np.arange(2,h-1,2.6):g.box(3,(x+w/2+.025,y-.8,z),(.04,.8,4.6))
        blocks.append(dict(center=[x,h/2-.8,z],size=[w,h,5.7]))
    # Low quiet pavilion silhouettes at the city ends; no animated scene props.
    for z in (-54,54):
        g.box(1,(-36,1.6,z),(3,.2,3));g.box(2,(-36,.85,z),(2.5,1.5,2.5))
    # Bake four colors into one palette texture/one submesh: one draw per scene.
    parts=g.parts;g.parts=[[]]
    for i,part in enumerate(parts):
        uv=[((i+.5)/4,.5)]*4
        g.parts[0].extend((points,normal,uv) for points,normal,_ in part)
    return g,blocks

def fix_palms(f):
    before=snapshot(f);d=material(f,f.objects[3],'Cloudcourt Static Palm','#ffffff',ptr(148,4),16)
    put(f.objects[3],d)
    return dict(changed_object_ids=delta(f,before),previous_shader='Custom/Vegetation',static_shader='Standard',
                material_id=3,shader_reference=ptr(148,4),shader_binaries_unchanged=True)

def add_orla(scene,shared):
    before=snapshot(scene);g,blocks=skyline_geometry()
    # Scene has an ordinary standard material only in resources/sharedassets0;
    # existing palm renderer resolves the shared material and mesh references.
    gs,ts,paths=hierarchy(scene);t=next(i for p,i in paths.items() if '/Cloudcourt Fan Palm ' in p)
    go=gs[ts[t]['m_GameObject']['m_PathID']]
    templates=[scene.objects[ts[t]['m_GameObject']['m_PathID']],scene.objects[t]]+[next(scene.objects[c['component']['m_PathID']] for c in go['m_Component'] if scene.objects[c['component']['m_PathID']].type.name==typ) for typ in ('MeshFilter','MeshRenderer')]
    # Clone the mesh schema in its owning file then reference it externally;
    # each beach scene gets one visual renderer with four opaque material slots.
    mesh=named(shared,'Mesh','Cloudcourt Orla Skyline')
    if mesh is None:mid=owned_mesh(shared,shared.objects[29],g,'Cloudcourt Orla Skyline')
    else:mid=mesh.path_id
    palette=Image.new('RGB',(64,16));draw=ImageDraw.Draw(palette)
    for i,c in enumerate(('#d4c7ab','#e7dfc9','#d5e0e2','#528497')):draw.rectangle((i*16,0,i*16+15,15),fill=c)
    tex=named(shared,'Texture2D','Cloudcourt Orla Palette')
    if tex is None:
        data=shared.objects[16].read_typetree();data['m_Name']='Cloudcourt Orla Palette';tex=shared.objects[clone(shared,shared.objects[16],data)]
    texp=tex.read();texp.set_image(palette,target_format=3,mipmap_count=1);texp.save();readable(tex)
    mats=[owned_material(shared,shared.objects[3],'Cloudcourt Orla Palette','#ffffff',ptr(148,4),tex.path_id)]
    shared_index=next(i+1 for i,e in enumerate(scene.externals) if e.path.endswith('sharedassets1.assets'))
    ids=visual(scene,'Cloudcourt Orla Skyline',mid,mats,templates)
    _,_,ps=hierarchy(scene);tt=ps['Cloudcourt Orla Skyline'];gg=scene.objects[scene.objects[tt].read_typetree()['m_GameObject']['m_PathID']].read_typetree()
    for c in gg['m_Component']:
        ob=scene.objects[c['component']['m_PathID']]
        if ob.type.name=='MeshFilter':d=ob.read_typetree();d['m_Mesh']=ptr(mid,shared_index);put(ob,d)
        if ob.type.name=='MeshRenderer':d=ob.read_typetree();d['m_Materials']=[ptr(i,shared_index) for i in mats];put(ob,d)
    return dict(changed_object_ids=delta(scene,before),buildings=blocks,triangles=sum(len(p)*2 for p in g.parts),
                vertices=sum(len(p)*4 for p in g.parts),new_renderers=1,opaque_materials=1,no_colliders=True)

def fix_arena(scene,shared):
    before=snapshot(scene);sbefore=snapshot(shared);G=geometry_class();roof=G(2)
    for points in [[(-12,14,-18),(0,16,-18),(0,16,18),(-12,14,18)],[(0,16,-18),(12,14,-18),(12,14,18),(0,16,18)]]:
        roof.quad(1,points);roof.quad(1,list(reversed(points)))
    for z in (-18.,18.):
        points=[(-12,13.96,z),(12,13.96,z),(0,16.02,z),(0,16.02,z)]
        roof.quad(1,points);roof.quad(1,[points[2],points[1],points[0],points[0]])
    for z in range(-16,17,4):roof.box(0,(0,13.8,z),(24,.16,.18))
    # Collider224 references mesh7. Keep that mesh byte-identical and attach
    # the closed roof to MeshFilter199 only, so collision topology is preserved.
    roof_id=owned_mesh(scene,scene.objects[7],roof,'Cloudcourt closed double-sided roof')
    d=scene.objects[199].read_typetree();d['m_Mesh']=ptr(roof_id);put(scene.objects[199],d)
    put(shared.objects[3],material(shared,shared.objects[3],'Cloudcourt Black Beams','#08090b'))
    # The roof renderer's first material previously referenced resources27,
    # independently of the vertical frame material. Bind both to the black frame.
    d=scene.objects[164].read_typetree();d['m_Materials'][0]=ptr(3,4);put(scene.objects[164],d)
    gs,ts,paths=hierarchy(scene)
    # Move each flag to the middle of a panel bay: no vertical column overlap.
    # The previous x-only clearance fix still left the z=0 and +/-8 flags on posts.
    banner_t=paths['Cloudcourt Arena Banners'];go=gs[ts[banner_t]['m_GameObject']['m_PathID']]
    mf=next(scene.objects[c['component']['m_PathID']] for c in go['m_Component'] if scene.objects[c['component']['m_PathID']].type.name=='MeshFilter')
    mesh=scene.objects[mf.read_typetree()['m_Mesh']['m_PathID']]
    from build_scene_v20 import _vertices,_mesh_components
    vertices=_vertices(mesh);updated=vertices.copy();moves=[]
    for indices in _mesh_components(mesh):
        center=vertices[indices].mean(axis=0)
        if abs(center[0])>11 and 5<center[1]<8.1:
            z=min((-14,-6,2,10,14),key=lambda z:abs(center[2]-z));x=math.copysign(11.25 if center[1]<7 else 11.13,center[0])
            updated[indices,0]+=x-center[0];updated[indices,2]+=z-center[2];moves.append([center.tolist(),[x,float(center[1]),z]])
    d=mesh.read_typetree();vd=d['m_VertexData'];raw=bytearray(vd['m_DataSize']);stride=len(raw)//len(vertices)
    np.ndarray((len(vertices),3),dtype='<f4',buffer=raw,offset=vd['m_Channels'][0]['offset'],strides=(stride,4))[:]=updated
    vd['m_DataSize']=bytes(raw)
    for bound,points in [(d,updated)]+[(s,updated[s['firstVertex']:s['firstVertex']+s['vertexCount']]) for s in d['m_SubMeshes']]:
        b=dict(m_Center=vec(*((points.min(0)+points.max(0))/2)),m_Extent=vec(*((points.max(0)-points.min(0))/2)))
        bound['m_LocalAABB' if bound is d else 'localAABB']=b
    put(mesh,d)
    # Add genuine square backing boards behind the existing UI labels.
    board=G(2)
    for sign in (-1,1):
        z=sign*17.77;board.box(0,(0,6.8,z),(9.8,9.8,.12));board.box(1,(0,6.8,z-sign*.075),(9.5,9.5,.06))
    mid=owned_mesh(scene,scene.objects[14],board,'Cloudcourt Scoreboard Square Backings')
    black=owned_material(scene,scene.objects[264],'Cloudcourt Board Black Border','#060708')
    white=owned_material(scene,scene.objects[264],'Cloudcourt Board White','#ffffff')
    visual(scene,'Cloudcourt Scoreboard Square Backings',mid,[black,white])
    # Old rounded UI image would cover the plain white board. Only this
    # decorative image is disabled; score paths/events/font lookup stay intact.
    for i in (280,316):
        raw=bytearray(scene.objects[i].get_raw_data());raw[12]=0;scene.objects[i].set_raw_data(bytes(raw));readable(scene.objects[i])
    return dict(changed_object_ids=delta(scene,before),shared_changed_object_ids=delta(shared,sbefore),
                roof_double_sided=True,gable_caps=2,roof_triangles=sum(len(p)*2 for p in roof.parts),
                black_beams=True,banner_moves=moves,square_boards=2,board_outer_size_m=9.8,board_border_m=.15)

def ball_art():
    # Original curved yellow/blue panel arrangement, free of logos and lettering.
    n=1024;y,x=np.mgrid[:n,:n];im=Image.new('RGB',(n,n),'#f5cb08');d=ImageDraw.Draw(im)
    islands=[(0,120,350,350,False),(0,472,350,350,False),(358,280,322,364,False),(658,110,366,367,True),(690,475,334,364,False),(330,638,364,361,True)]
    for ix,iy,w,h,horizontal in islands:
        points=[]
        for k in range(65):
            t=k/64;offset=.36+.09*math.sin(t*math.pi)
            points.append((ix+w*t,iy+h*offset) if horizontal else (ix+w*offset,iy+h*t))
        for k in reversed(range(65)):
            t=k/64;offset=.70+.09*math.sin(t*math.pi)
            points.append((ix+w*t,iy+h*offset) if horizontal else (ix+w*offset,iy+h*t))
        d.polygon(points,fill='#153b9c')
    a=np.asarray(im).astype(np.int16);grain=np.random.default_rng(21).normal(0,.7,(n,n,1));dimples=((x%9-4)**2+(y%9-4)**2<1.8)*2
    return Image.fromarray(np.clip(a+grain-dimples[:,:,None],0,255).astype('uint8'))

def fix_net_and_ball(f):
    before=snapshot(f)
    # Material-level flat colors prevent any normal/printed post detail.
    for i in (7,8):put(f.objects[i],material(f,f.objects[i],'Cloudcourt Plain Black Post','#050607'))
    for i in (5,6):put(f.objects[i],material(f,f.objects[i],'Cloudcourt White Net Tape','#ffffff',ptr(148,2)))
    # resources42 is also used by legacy detail palettes. Do not repaint it.
    im=ball_art();t=f.objects[40].read();set_rgb_full_mips(t,im);t.save();readable(f.objects[40])
    return dict(changed_object_ids=delta(f,before),post_materials=[7,8],white_tape_materials=[5,6],ball_texture=40,ball_text_or_logo=False)

def build_environment_assets(files):
    report={'palms':fix_palms(files['sharedassets1.assets'])}
    report['beach_scenes']={n:add_orla(files[n],files['sharedassets1.assets']) for n in ('level1','level2')}
    report['arena']=fix_arena(files['level3'],files['sharedassets3.assets'])
    report['net_ball']=fix_net_and_ball(files['resources.assets'])
    return report

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,default=R/'versions/cloudcourt-v20-1-antes-v21');p.add_argument('--output',type=Path,default=R/'visuals-v21-environment');a=p.parse_args()
    assert a.output.resolve()!=a.source_dir.resolve() and 'working' not in a.output.parts
    names=['resources.assets','sharedassets1.assets','sharedassets3.assets','level1','level2','level3']
    files={n:UnityPy.load(str(a.source_dir/n)).file for n in names};before={n:snapshot(f) for n,f in files.items()}
    report=build_environment_assets(files);a.output.mkdir(parents=True,exist_ok=True)
    for n,f in files.items():
        report.setdefault('changed_objects',{})[n]=delta(f,before[n]);(a.output/n).write_bytes(f.save())
    ball_art().save(a.output/'yellow-blue-ball-atlas.png')
    (a.output/'environment-report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'changed_objects':report['changed_objects'],'skyline_triangles':report['beach_scenes']['level1']['triangles']},indent=2))
