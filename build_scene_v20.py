"""In-memory v20 Settings layout and gym banner clearance; isolated fixtures.

Does not write working/, install, rebuild the global menu, or change colliders.
Score outlines need score_outline_v20.c after runtime cartoon-font assignment.
"""
from pathlib import Path
import argparse, hashlib, json, math, struct, sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import numpy as np
import UnityPy
from build_menu_v19 import MenuEditor, hierarchy, save_tree, set_raw
from UnityPy.helpers.MeshHelper import MeshHandler

SETTINGS_ROWS=[
 ('Movement Button','Aim Assist Button'),
 ('Jump Button','Friend Bot Pro Button'),
 ('Jump Height Button','Opponent Bot Pro Button'),
 ('Snap Turn Button','Music Button'),
 ('Front Row Only Button','Resolution Button'),
 ('Movement Speed Slider','Region Button')]

def _digest(raw):return hashlib.sha256(raw).hexdigest()
def _snapshot(f):return {i:o.get_raw_data() for i,o in f.objects.items()}
def _changed(f,before):return sorted(i for i,o in f.objects.items() if i not in before or before[i]!=o.get_raw_data())

def reorder_settings(menu):
    before=_snapshot(menu);editor=MenuEditor(menu);gs,ts,paths=hierarchy(menu)
    base='Menu/Pages/Settings';rows=[];ordered=[]
    for row,names in enumerate(SETTINGS_ROWS):
        y=132-row*44
        for column,name in enumerate(names):
            path=base+'/'+name;t=paths[path];x=-124 if column==0 else 124
            rows.append({'path':path,'transform_id':t,'before':ts[t]['m_AnchoredPosition'],
                         'after':{'x':x,'y':y},'size':[216,36]})
            editor.rect(t,x,y,216,36);ordered.append(t)
            # Retain the original labels/events and the authored cartoon font.
            child=paths.get(path+'/Text')
            if child:
                text=editor.component(child,572);raw=bytearray(text.get_raw_data())
                struct.pack_into('<i',raw,84,16);struct.pack_into('<i',raw,100,16);raw[60]=0;set_raw(text,raw)
    back=paths[base+'/Back Button'];editor.rect(back,0,-154,216,38);ordered.append(back)
    version=paths[base+'/Version'];editor.rect(version,0,-194,450,24);ordered.append(version)
    # The slider remains a Slider with its original target, events and value.
    label=paths[base+'/Movement Speed Slider/Movement Speed Label']
    editor.rect(label,0,12,216,18)
    label_text=editor.component(label,572);raw=bytearray(label_text.get_raw_data())
    struct.pack_into('<i',raw,84,15);struct.pack_into('<i',raw,100,15);raw[60]=0;set_raw(label_text,raw)
    editor.rect(paths[base+'/Movement Speed Slider/Background'],0,-8,192,6)
    for child,height in (('Fill Area',6),('Handle Slide Area',20)):
        obj=menu.objects[paths[base+'/Movement Speed Slider/'+child]];d=obj.read_typetree()
        d['m_AnchorMin'],d['m_AnchorMax']=dict(x=0.,y=.5),dict(x=1.,y=.5)
        d['m_AnchoredPosition']=dict(x=0.,y=-8.);d['m_LocalPosition']=dict(x=0.,y=-8.,z=0.)
        d['m_SizeDelta']=dict(x=-24.,y=float(height));save_tree(obj,d)
    for name in ('Sets Button','Points Button'):editor.active(paths[base+'/'+name],False)
    parent=paths[base];d=menu.objects[parent].read_typetree()
    rest=[p['m_PathID'] for p in d['m_Children'] if p['m_PathID'] not in ordered]
    children=ordered+rest;d['m_Children']=[{'m_FileID':0,'m_PathID':i} for i in children]
    save_tree(menu.objects[parent],d)
    for index,t in enumerate(children):
        d=menu.objects[t].read_typetree();d['m_RootOrder']=index;save_tree(menu.objects[t],d)
    return {'settings_rows':rows,'changed_object_ids':_changed(menu,before),
            'hidden_options':['Sets Button','Points Button'],
            'original_events_and_controller_preserved':True}

def _matrix(t):
    x,y,z,w=[t['m_LocalRotation'][k] for k in 'xyzw'];s=t['m_LocalScale'];p=t['m_LocalPosition']
    rotation=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                       [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                       [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    result=np.eye(4);result[:3,:3]=rotation@np.diag([s[k] for k in 'xyz']);result[:3,3]=[p[k] for k in 'xyz'];return result
def _world(ts,i):
    t=ts[i];p=t['m_Father']['m_PathID'];m=_matrix(t)
    return _world(ts,p)@m if p in ts else m
def _apply(matrix,vertices):return (matrix@np.c_[vertices,np.ones(len(vertices))].T).T[:,:3]
def _vertices(mesh):
    handler=MeshHandler(mesh.read());handler.process();return np.array(handler.m_Vertices,float)
def _bounds(vertices):return np.array([vertices.min(axis=0),vertices.max(axis=0)])
def _bounds_dict(b):return {'min':b[0].tolist(),'max':b[1].tolist()}
def _overlap(a,b):return bool(np.all(a[0]<b[1]-1e-5) and np.all(b[0]<a[1]-1e-5))
def _distance(a,b):return float(np.linalg.norm(np.maximum(np.maximum(a[0]-b[1],b[0]-a[1]),0)))

def _mesh_components(mesh):
    d=mesh.read_typetree();n=d['m_VertexData']['m_VertexCount'];parent=list(range(n))
    def find(a):
        while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
        return a
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[b]=a
    triangles=np.frombuffer(bytes(d['m_IndexBuffer']),dtype='<u2').reshape(-1,3)
    for a,b,c in triangles:union(int(a),int(b));union(int(a),int(c))
    groups={}
    for i in range(n):groups.setdefault(find(i),[]).append(i)
    return [np.array(ids) for ids in groups.values()]

def scene_structural_boxes(scene):
    """Exact boxes from the existing arena frame, plus conservative roof bounds."""
    gs,ts,paths=hierarchy(scene);boxes=[]
    for path,t in paths.items():
        go=gs[ts[t]['m_GameObject']['m_PathID']]
        filters=[scene.objects[c['component']['m_PathID']] for c in go['m_Component']
                 if scene.objects[c['component']['m_PathID']].type.name=='MeshFilter']
        for mf in filters:
            reference=mf.read_typetree()['m_Mesh']
            if reference['m_FileID'] or reference['m_PathID'] not in (7,14):continue
            mesh=scene.objects[reference['m_PathID']];data=mesh.read_typetree();vertices=_vertices(mesh);matrix=_world(ts,t)
            if reference['m_PathID']==14:
                # Part 3 is made entirely from the authored 24-vertex frame boxes.
                part=data['m_SubMeshes'][3];start,count=part['firstVertex'],part['vertexCount'];assert count%24==0
                for k in range(start,start+count,24):
                    b=_bounds(_apply(matrix,vertices[k:k+24]));boxes.append({'mesh':14,'vertex_start':k,'path':path,'bounds':b})
            else:
                for k,part in enumerate(data['m_SubMeshes']):
                    start,count=part['firstVertex'],part['vertexCount']
                    b=_bounds(_apply(matrix,vertices[start:start+count]));boxes.append({'mesh':7,'part':k,'path':path,'bounds':b})
    assert len(boxes)>20
    return boxes

def relocate_banners(scene):
    before=_snapshot(scene);gs,ts,paths=hierarchy(scene);t=paths['Cloudcourt Arena Banners']
    go=gs[ts[t]['m_GameObject']['m_PathID']]
    assert all(scene.objects[c['component']['m_PathID']].type.name in ('Transform','MeshFilter','MeshRenderer') for c in go['m_Component'])
    mf=next(scene.objects[c['component']['m_PathID']] for c in go['m_Component']
            if scene.objects[c['component']['m_PathID']].type.name=='MeshFilter')
    reference=mf.read_typetree()['m_Mesh'];assert reference['m_FileID']==0
    mesh=scene.objects[reference['m_PathID']];vertices=_vertices(mesh);updated=vertices.copy()
    groups=_mesh_components(mesh);matrix=_world(ts,t);boxes=scene_structural_boxes(scene);rows=[]
    for index,indices in enumerate(groups):
        local=_bounds(vertices[indices]);center=local.mean(axis=0)
        if not (abs(center[0])>11 and 5<center[1]<8.1):continue
        kind='banner' if center[1]<7.0 else 'hanger'
        desired=math.copysign(11.25 if kind=='banner' else 11.13,center[0]);delta=desired-center[0]
        if abs(delta)>1e-5:updated[indices,0]+=delta
        old=_bounds(_apply(matrix,vertices[indices]));new=_bounds(_apply(matrix,updated[indices]))
        intersections=[{'mesh':b['mesh'],'vertex_start':b.get('vertex_start'),'part':b.get('part')}
                       for b in boxes if _overlap(old,b['bounds'])]
        assert not any(_overlap(new,b['bounds']) for b in boxes),'New banner intersects arena structure'
        rows.append({'component':index,'kind':kind,'vertex_count':len(indices),'before':_bounds_dict(old),'after':_bounds_dict(new),
                     'old_intersections':intersections,'minimum_structure_clearance_m':min(_distance(new,b['bounds']) for b in boxes)})
    assert len(rows)==20 and sum(row['kind']=='banner' for row in rows)==10
    d=mesh.read_typetree();vd=d['m_VertexData'];raw=bytearray(vd['m_DataSize']);count=vd['m_VertexCount'];stride=len(raw)//count
    assert len(raw)==count*stride and vd['m_Channels'][0]['stream']==0 and vd['m_Channels'][0]['dimension']==3
    view=np.ndarray((count,3),dtype='<f4',buffer=raw,offset=vd['m_Channels'][0]['offset'],strides=(stride,4));view[:]=updated
    vd['m_DataSize']=bytes(raw)
    def aabb(v):
        b=_bounds(v);return {'m_Center':dict(zip('xyz',map(float,b.mean(axis=0)))),'m_Extent':dict(zip('xyz',map(float,(b[1]-b[0])/2)))}
    d['m_LocalAABB']=aabb(updated)
    for part in d['m_SubMeshes']:
        first,n=part['firstVertex'],part['vertexCount'];part['localAABB']=aabb(updated[first:first+n])
    save_tree(mesh,d)
    return {'mesh_id':mesh.path_id,'transform_id':t,'components':rows,'changed_object_ids':_changed(scene,before),
            'structural_boxes_checked':len(boxes),'old_intersections':sum(bool(row['old_intersections']) for row in rows),
            'new_intersections':0,'colliders_unchanged':True}

def build_scene_assets(files):
    return {'level0':reorder_settings(files['level0']), 'level3':relocate_banners(files['level3']),
            'score_outline':{'helper':'score_outline_v20.c','runtime_font_preserved':True,
                             'TMP_outline_rgba':[0,0,0,255],'TMP_outline_width':.18,
                             'UI_Text_outline_distance':[2.5,2.5],'decorative_raycast':False}}

def preview_settings(menu,path):
    from PIL import Image,ImageDraw,ImageFont
    _,ts,paths=hierarchy(menu);image=Image.new('RGB',(1100,940),'#172b46');draw=ImageDraw.Draw(image)
    font=R/'assets/shared/fonts/CloudcourtBubble.ttf'
    draw.text((550,55),'CLOUDCOURT',font=ImageFont.truetype(str(font),54),anchor='mm',fill='#fff1dc')
    draw.text((550,112),'SETTINGS',font=ImageFont.truetype(str(font),30),anchor='mm',fill='#ffcf58')
    for names in SETTINGS_ROWS:
        for name in names:
            data=ts[paths['Menu/Pages/Settings/'+name]];x,y=data['m_AnchoredPosition'].values();cx,cy=550+x*2,450-y*2
            label=name.replace(' Button','').replace(' Slider','').upper()
            if name.endswith('Slider'):
                draw.text((cx,cy-24),label,font=ImageFont.truetype(str(font),23),anchor='mm',fill='#fff1dc')
                draw.rounded_rectangle((cx-192,cy+10,cx+192,cy+22),radius=6,fill='#8197ae')
                draw.rounded_rectangle((cx-192,cy+10,cx+12,cy+22),radius=6,fill='#ffcf58')
                draw.ellipse((cx-4,cy-2,cx+32,cy+34),fill='#fff1dc',outline='#172b46',width=2)
            else:
                draw.rounded_rectangle((cx-216,cy-36,cx+216,cy+36),radius=16,fill='#243c58',outline='#ffcf58',width=3)
                draw.text((cx,cy),label,font=ImageFont.truetype(str(font),26),anchor='mm',fill='#fff1dc')
    draw.rounded_rectangle((334,720,766,796),radius=16,fill='#ffcf58');draw.text((550,758),'BACK',font=ImageFont.truetype(str(font),28),anchor='mm',fill='#172b46')
    draw.text((550,893),'Layout de referencia — nao e captura VR',font=ImageFont.truetype(str(font),20),anchor='mm',fill='#a9bccb')
    image.save(path)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source-dir',type=Path,default=R/'versions/cloudcourt-v19-antes-v20')
    parser.add_argument('--output',type=Path,default=R/'visuals-v20-scene');args=parser.parse_args()
    assert args.output.resolve()!=args.source_dir.resolve() and 'working' not in args.output.parts
    files={name:UnityPy.load(str(args.source_dir/name)).file for name in ('level0','level3')}
    report=build_scene_assets(files);args.output.mkdir(parents=True,exist_ok=True)
    for name,file in files.items():(args.output/name).write_bytes(file.save())
    preview_settings(files['level0'],args.output/'settings-preview.png')
    (args.output/'scene-report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'output':str(args.output),'settings_objects_changed':len(report['level0']['changed_object_ids']),
                      'banner_objects_changed':report['level3']['changed_object_ids'],
                      'banner_old_intersections':report['level3']['old_intersections'],'banner_new_intersections':0},indent=2))
