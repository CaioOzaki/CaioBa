"""Targeted in-memory corrective environment deltas from delivered v21.
No installation, colliders, collision meshes, native code or legacy rebuild.
"""
from pathlib import Path
import copy,json,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np,UnityPy
from PIL import ImageFont
from build_environment_v21 import (ptr,vec,rgba,snapshot,delta,put,readable,material,named,
 owned_mesh,owned_material,visual,geometry_class,skyline_geometry)
from fix_gloves_v16 import hierarchy
from build_scene_v20 import _vertices,_world
NAMES=['resources.assets','sharedassets1.assets','sharedassets3.assets','level1','level2','level3']

def skyline_geometry_v22():
    # Enlarge the actual existing skyline boxes in place, keep 1 draw/1572 triangles.
    g,blocks=skyline_geometry()
    # Global expansion in Z causes appropriate gaps and a broader coast silhouette;
    # X stays landward. Scale Y about ground -.8 instead of floating foundations.
    for part in g.parts:
        for j,(points,normal,uv) in enumerate(part):
            p=np.array(points,float);p[:,0]=-36+(p[:,0]+36)*1.30
            p[:,1]=-.8+(p[:,1]+.8)*1.55;p[:,2]*=1.24
            part[j]=(p.tolist(),normal,uv)
    for b in blocks:
        b['center']=[-36+(b['center'][0]+36)*1.30,-.8+(b['center'][1]+.8)*1.55,b['center'][2]*1.24]
        b['size']=[b['size'][0]*1.30,b['size'][1]*1.55,b['size'][2]*1.24]
    return g,blocks

def scoreboard_bounds():
    # Real font glyph bounds for maximum two-digit score + existing title/set,
    # transformed using the serialized 0.013 world-space canvas scale.
    font=R/'assets/cloudcourt-v16/CloudcourtBubble.ttf';bounds=[]
    for text,size,y in [('99 : 99',76,-6.10000944),('CLOUDCOURT VR',28,71),('0 - 0',40,-73.80001068)]:
        bb=ImageFont.truetype(str(font),size).getbbox(text,anchor='mm')
        # Unity Y points up; PIL Y points down. Include runtime Outline +/-2.5px.
        bounds.append([[(bb[0]-2.5)*.013,(y-bb[3]-2.5)*.013],[(bb[2]+2.5)*.013,(y-bb[1]+2.5)*.013]])
    b=np.array(bounds);lo=b[:,0].min(0)-.18;hi=b[:,1].max(0)+.18
    return lo,hi

def fix_arena_v22(scene,shared):
    before=snapshot(scene);sb=snapshot(shared)
    put(shared.objects[3],material(shared,shared.objects[3],'Cloudcourt Gray Beams','#777e86'))
    # Rewrite only owned visual board mesh, preserving label hierarchy and UI data.
    old=named(scene,'Mesh','Cloudcourt Scoreboard Square Backings') or named(scene,'Mesh','Cloudcourt Scoreboard Rectangle Backings')
    assert old is not None
    lo,hi=scoreboard_bounds();size=hi-lo;center=(lo+hi)/2;g=geometry_class()(2)
    for sign in (-1,1):
        z=sign*17.77
        g.box(0,(center[0],6.8+center[1],z),(size[0],size[1],.12))
        g.box(1,(center[0],6.8+center[1],z-sign*.075),(size[0]-.08,size[1]-.08,.06))
    data=g.serial(old.read_typetree(),'Cloudcourt Scoreboard Rectangle Backings')
    data['m_VertexData']['m_Channels'][5]=dict(stream=0,offset=48,format=0,dimension=2);put(old,data)
    gs,ts,ps=hierarchy(scene)
    path='Cloudcourt Scoreboard Square Backings' if 'Cloudcourt Scoreboard Square Backings' in ps else 'Cloudcourt Scoreboard Rectangle Backings'
    go=scene.objects[ts[ps[path]]['m_GameObject']['m_PathID']];d=go.read_typetree();d['m_Name']='Cloudcourt Scoreboard Rectangle Backings';put(go,d)
    return dict(changed_object_ids=delta(scene,before),shared_changed_object_ids=delta(shared,sb),beams_color='#777e86',
                board_outer_size_m=size.tolist(),board_center_y_m=float(6.8+center[1]),border_m=.04,
                glyph_bounds_source='CloudcourtBubble.ttf / 99 : 99, CLOUDCOURT VR, 0 - 0 + 2.5px outline',
                glyph_to_board_padding_m=.18,live_score_labels_unchanged=True)

def fix_posts_v22(f):
    before=snapshot(f)
    # resources7 is the broad polySurface15 padding; 8 is cylindrical metal hardware.
    for i,name,color in [(7,'Cloudcourt Dark Gray Padding','#353a40'),(8,'Cloudcourt Silver Post Metal','#bfc5cb')]:
        d=material(f,f.objects[i],name,color)
        floats=dict(d['m_SavedProperties']['m_Floats']);floats['_Metallic']=.45 if i==8 else 0.;floats['_Glossiness']=.35 if i==8 else .05
        d['m_SavedProperties']['m_Floats']=list(floats.items());put(f.objects[i],d)
    return dict(changed_object_ids=delta(f,before),padding_material=7,metal_material=8,padding_color='#353a40',metal_color='#bfc5cb',all_branding_textures_absent=True)

def clean_ground(scene,shared):
    before=snapshot(scene)
    # Existing terrain is already unlightmapped. Keep real-time light/shadows;
    # isolate the gameplay region from legacy terrain/probe/splat rendering.
    G=geometry_class();g=G(1)
    pts=[(-12,.004,-18),(-12,.004,18),(12,.004,18),(12,.004,-18)]
    g.quad(0,pts,[(0,0),(0,7.2),(4.8,7.2),(4.8,0)])
    mesh=owned_mesh(shared,shared.objects[29],g,'Cloudcourt Dry Sand Runoff')
    mat=owned_material(shared,shared.objects[3],'Cloudcourt Dry Sand','#ffffff',ptr(148,4),26)
    # Direct Standard material with explicit dry-sand settings; no stale cubemap sampling.
    d=shared.objects[mat].read_typetree();d['m_ShaderKeywords']='_GLOSSYREFLECTIONS_OFF _SPECULARHIGHLIGHTS_OFF'
    d['m_SavedProperties']['m_Floats'] += [('_GlossyReflections',0.),('_SpecularHighlights',0.)];put(shared.objects[mat],d)
    visual(scene,'Cloudcourt Dry Sand Runoff',mesh,[mat])
    gs,ts,ps=hierarchy(scene);go=gs[ts[ps['Cloudcourt Dry Sand Runoff']]['m_GameObject']['m_PathID']]
    idx=next(i+1 for i,e in enumerate(scene.externals) if e.path.endswith('sharedassets1.assets'))
    for c in go['m_Component']:
        ob=scene.objects[c['component']['m_PathID']]
        if ob.type.name=='MeshFilter':d=ob.read_typetree();d['m_Mesh']=ptr(mesh,idx);put(ob,d)
        if ob.type.name=='MeshRenderer':
            d=ob.read_typetree();d.update(m_Materials=[ptr(mat,idx)],m_CastShadows=0,m_ReceiveShadows=1,m_LightProbeUsage=0,m_ReflectionProbeUsage=0,m_LightmapIndex=65535);put(ob,d)
    return dict(changed_object_ids=delta(scene,before),surface_y_m=.004,bounds_xz=[[-12,-18],[12,18]],triangles=2,draws=1,
        realtime_shadow_receiving=True,legacy_ground_lightmap=False,legacy_ground_probes=False,
        sun_and_baked_lighting_assets_unchanged=True,terrain_and_collision_unchanged=True)

def build_environment_assets_v22(files):
    before={n:snapshot(files[n]) for n in NAMES}
    s=files['sharedassets1.assets'];old=named(s,'Mesh','Cloudcourt Orla Skyline');assert old
    g,blocks=skyline_geometry_v22();owned_mesh(s,old,g,'Cloudcourt Orla Skyline')
    report={'arena':fix_arena_v22(files['level3'],files['sharedassets3.assets']),
            'posts':fix_posts_v22(files['resources.assets']),
            'skyline':dict(buildings=blocks,triangles=sum(len(p)*2 for p in g.parts),draws_per_scene=1,height_scale=1.55,width_scale=1.30,coast_scale=1.24),
            'beach':{n:clean_ground(files[n],s) for n in ['level1','level2']}}
    report['changed_objects']={n:delta(files[n],before[n]) for n in NAMES}
    return report

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,default=R/'working/VolleyballFever_Data');p.add_argument('--output',type=Path,default=R/'visuals-v22-environment');a=p.parse_args()
    assert a.output.resolve()!=a.source_dir.resolve() and 'working' not in a.output.parts
    files={n:UnityPy.load(str(a.source_dir/n)).file for n in NAMES};report=build_environment_assets_v22(files)
    a.output.mkdir(exist_ok=True,parents=True)
    for n,f in files.items():(a.output/n).write_bytes(f.save())
    (a.output/'environment-report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report['changed_objects'],indent=2))
