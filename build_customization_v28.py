"""v28 camera-free same-mesh avatar preview, original procedural hats, controls.
Callable in-memory: apply_customization_v28(resources,level0). No shared writes.
"""
from pathlib import Path
import argparse,copy,hashlib,json,math,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from fix_gloves_v16 import hierarchy,_model_class
from build_avatar_v21 import clone
from build_menu_v19 import MenuEditor,IMAGE,RAW_IMAGE,save_tree,ptr
HATS=['Cap','Fedora','Cowboy','MotorcycleHelmet','Beanie','Crown','Visor']

def hat_model(kind):
    m=_model_class()()
    # All parts are authored here, never loaded from another game's assets.
    def ring(y,rx,rz,height,topscale=1.,segments=24,front_open=False):
        base=len(m.v)
        for yy,s in [(y,1),(y+height,topscale)]:
            for i in range(segments):
                a=2*math.pi*i/segments;c,sn=math.cos(a),math.sin(a)
                m.v.append((rx*c*s,yy,rz*sn*s));m.n.append((c,0,sn));m.uv.append((.5625,.9375));m.b.append(0)
        for i in range(segments):
            a=base+i;b=base+(i+1)%segments;c=a+segments;d=b+segments
            if not front_open or math.sin(2*math.pi*(i+.5)/segments)<.45:m.tri.extend([(a,c,b),(b,c,d)])
        m.tri.extend((base+segments,base+segments+i,base+segments+i+1) for i in range(1,segments-1))
    if kind=='Cap':
        ring(.24,.35,.34,.23,.65);m.softbox((0,.245,.31),(.30,.025,.23),0,0)
    elif kind=='Fedora':
        ring(.29,.49,.44,.035);ring(.325,.30,.28,.27,.78)
    elif kind=='Cowboy':
        ring(.28,.60,.45,.055,.94);ring(.335,.30,.28,.30,.72)
        m.softbox((-.48,.34,0),(.10,.035,.31),0,0);m.softbox((.48,.34,0),(.10,.035,.31),0,0)
    elif kind=='MotorcycleHelmet':
        ring(-.16,.39,.38,.48,.96,front_open=True);ring(.32,.375,.365,.17,.28)
        # Chin bar and side cheeks; the front remains open so the face is visible.
        m.softbox((0,-.12,.37),(.36,.075,.045),0,0)
    elif kind=='Beanie':ring(.18,.35,.34,.11);ring(.29,.35,.34,.28,.08)
    elif kind=='Crown':
        ring(.24,.36,.35,.10)
        for i in range(8):
            a=math.pi*i/4;m.softbox((.33*math.cos(a),.42,.32*math.sin(a)),(.04,.12,.04),0,0)
    elif kind=='Visor':ring(.20,.35,.34,.085);m.softbox((0,.20,.34),(.33,.025,.25),0,0)
    else:raise ValueError(kind)
    m.v=[list(v) for v in m.v];m.n=[list(v) for v in m.n];m.uv=[list(v) for v in m.uv]
    return m

def apply_customization_v28(resources,menu):
    before_r={i:o.get_raw_data() for i,o in resources.objects.items()};before_l={i:o.get_raw_data() for i,o in menu.objects.items()}
    g,t,p=hierarchy(resources)
    headpath=next(x for x in p if x.endswith('Physical Head/Visual Head Root/Head'))
    bodypath=next(x for x in p if x.endswith('Physical Torso/Scaler (1)/Body'))
    def components(file,tid):
        go=file.objects[file.objects[tid].read_typetree()['m_GameObject']['m_PathID']]
        return go,{file.objects[x['component']['m_PathID']].type.name:file.objects[x['component']['m_PathID']] for x in go.read_typetree()['m_Component']}
    def visual(file,sourcefile,sourceid,parent,name,position,scale,mesh=None,material=None,active=True,rotation=None):
        # A strictly graphical child: no scripts, colliders, joints or lights.
        gs,ts,ps=hierarchy(file);existing=next((i for x,i in ps.items() if ts[i]['m_Father']['m_PathID']==parent and gs[ts[i]['m_GameObject']['m_PathID']]['m_Name']==name),None)
        srcgo,comp=components(sourcefile,sourceid)
        if existing:
            go,cs=components(file,existing);tr=file.objects[existing];mf=cs['MeshFilter'];mr=cs['MeshRenderer']
        else:
            go=clone(file,srcgo);tr=clone(file,comp['Transform']);mf=clone(file,comp['MeshFilter']);mr=clone(file,comp['MeshRenderer'])
            if sourcefile is not file:
                for obj in (go,tr,mf,mr):
                    obj.type_id=next(i for i,typ in enumerate(file.types) if typ.class_id==obj.class_id)
                    obj.serialized_type=file.types[obj.type_id]
        gd=go.read_typetree();gd.update(m_Name=name,m_IsActive=active,m_Layer=5 if file is menu else gd['m_Layer']);gd['m_Component']=[{'component':ptr(x.path_id)} for x in (tr,mf,mr)];save_tree(go,gd)
        td=tr.read_typetree();td.update(m_GameObject=ptr(go.path_id),m_Father=ptr(parent),m_Children=td['m_Children'] if existing else [],m_LocalPosition=dict(zip('xyz',position)),m_LocalScale=dict(zip('xyz',scale)),m_LocalRotation=dict(zip('xyzw',rotation or (0,0,0,1))));save_tree(tr,td)
        fd=copy.deepcopy(comp['MeshFilter'].read_typetree());rd=copy.deepcopy(comp['MeshRenderer'].read_typetree())
        if sourcefile is not file:
            for tree in (fd,rd):
                def ext(v):
                    if isinstance(v,dict):
                        if set(v)=={'m_FileID','m_PathID'} and v['m_PathID']:
                            if v['m_FileID']==0:v['m_FileID']=4
                            else:
                                extpath=sourcefile.externals[v['m_FileID']-1].path
                                v['m_FileID']=next(i+1 for i,e in enumerate(file.externals) if e.path==extpath)
                        else:
                            for vv in v.values():ext(vv)
                    elif isinstance(v,list):
                        for vv in v:ext(vv)
                ext(tree)
        fd['m_GameObject']=ptr(go.path_id);rd['m_GameObject']=ptr(go.path_id)
        if mesh:fd['m_Mesh']=mesh
        if material:rd['m_Materials']=[material]
        rd['m_CastShadows']=0;rd['m_ReceiveShadows']=False;rd['m_Enabled']=True
        save_tree(mf,fd);save_tree(mr,rd)
        if not existing:
            par=file.objects[parent];pd=par.read_typetree();pd['m_Children'].append(ptr(tr.path_id));save_tree(par,pd)
        return tr.path_id
    named={o.read_typetree()['m_Name']:o for o in resources.objects.values() if o.type.name in ('Mesh','Material')}
    # A neutral hand-material texture has the original white palette swatch.
    material=named.get('Cloudcourt v28 Hats')
    if material is None:material=clone(resources,named['Cloudcourt v21 Skin Hands'])
    md=copy.deepcopy(named['Cloudcourt v21 Skin Hands'].read_typetree());md['m_Name']='Cloudcourt v28 Hats'
    for key,val in md['m_SavedProperties']['m_Colors']:
        if key=='_Color':val.update(r=.12,g=.20,b=.29,a=1.)
    save_tree(material,md)
    meshes={};hatids={}
    _,hc=components(resources,p[headpath]);source=resources.objects[hc['MeshFilter'].read_typetree()['m_Mesh']['m_PathID']]
    for kind in HATS:
        name='Cloudcourt v28 Hat '+kind;mesh=named.get(name)
        if mesh is None:mesh=clone(resources,source)
        save_tree(mesh,hat_model(kind).serialize(source.read_typetree(),name,False));meshes[kind]=mesh.path_id
        hatids[kind]=visual(resources,resources,p[headpath],p[headpath],'CC_Hat_'+kind,(0,0,0),(1,1,1),ptr(mesh.path_id),ptr(material.path_id),False)
    preview_hat=next((o for o in resources.objects.values() if o.type.name=='Material' and o.read_typetree()['m_Name']=='Cloudcourt v28 Mirror Hats'),None)
    if preview_hat is None:preview_hat=clone(resources,material)
    pd=copy.deepcopy(md);pd['m_Name']='Cloudcourt v28 Mirror Hats';pd['m_CustomRenderQueue']=4001;save_tree(preview_hat,pd)
    # Single panel page: left mirror, right controls, Done below all rows.
    e=MenuEditor(menu);panel='Menu/CC_Customization';panelid=e.find(panel);e.rect(panelid,0,0,900,450)
    e.label(panel+'/CC_CustomTitle','CUSTOMIZE',0,190,790,40,28)
    e.label(panel+'/CC_CustomHint','Your avatar. Your style.',0,152,790,28,17)
    for name in ['CC_FacePreview','CC_OutfitPreview']:e.active(e.find(panel+'/'+name),False)
    rows=[('Face',100),('Outfit',45),('HandTone',-10),('Hat',-65),('Arms',-120)]
    for stem,y in rows:
        title={'Face':'FACE','Outfit':'OUTFIT','HandTone':'HANDS','Hat':'HAT','Arms':'ARMS'}[stem]
        e.label(panel+'/CC_'+stem+'Title',title,-2,y,110,28,16)
        e.label(panel+'/CC_'+stem+'Label',{'Hat':'None','Arms':'Outfit Color'}.get(stem,{'Face':'Cool','Outfit':'Black Suit','HandTone':'Porcelain'}.get(stem,'')),198,y,230,28,18)
        e.button(panel+'/CC_'+stem+'Prev','<',67,y,50,38,22);e.button(panel+'/CC_'+stem+'Next','>',355,y,50,38,22)
    e.rect(e.find(panel+'/CC_HandToneSwatch'),-63,-10,26,26)
    e.rect(e.find(panel+'/CC_CustomizeBack'),0,-175,190,38);e.text(e.find(panel+'/CC_CustomizeBack/Text'),'Done',20)
    e.label(panel+'/CC_MirrorCaption','LIVE AVATAR',-255,-160,220,25,15)
    mh=visual(menu,resources,p[headpath],panelid,'CC_MirrorHead',(-255,88,-80),(220*.55757,)*3,rotation=(0,1,0,0))
    mb=visual(menu,resources,p[bodypath],panelid,'CC_MirrorBody',(-255,-7,-80),(220*.55757,)*3,rotation=(0,1,0,0))
    for kind in HATS:visual(menu,resources,p[headpath],mh,'CC_Hat_'+kind,(0,0,0),(1,1,1),dict(m_FileID=4,m_PathID=meshes[kind]),dict(m_FileID=4,m_PathID=preview_hat.path_id),False)
    armmaterial=named.get('Cloudcourt v28 Cloth Arms')
    if armmaterial is None:armmaterial=clone(resources,named['Cloudcourt v21 Skin Hands'])
    ad=copy.deepcopy(named['Cloudcourt v21 Skin Hands'].read_typetree());ad['m_Name']='Cloudcourt v28 Cloth Arms'
    for key,val in ad['m_SavedProperties']['m_TexEnvs']:
        val['m_Texture']=ptr(0)
    save_tree(armmaterial,ad)
    arms=[]
    for side,x in [('L',-323),('R',-187)]:
        for part,y in [('Upper',-12),('Lower',-78)]:
            path=next(x for x in p if x.endswith('Physical '+part+' Arm '+side))
            _,cs=components(resources,p[path]);rd=cs['MeshRenderer'].read_typetree();rd['m_Materials']=[ptr(armmaterial.path_id)];save_tree(cs['MeshRenderer'],rd)
            arms.append(visual(menu,resources,p[path],panelid,'CC_Mirror'+part+side,(x,y,-80),(22,32,22),material=dict(m_FileID=4,m_PathID=armmaterial.path_id)))
    hands=[]
    for side,x in [('L',-323),('R',-187)]:
        path=next(x for x in p if x.endswith('Hand Root '+side+'/Open/Cloudcourt Open Glove'))
        hands.append(visual(menu,resources,p[path],panelid,'CC_MirrorHand'+side,(x,-113,-80),(170,170,170),rotation=(.70710678,0,0,.70710678)))
    changed_r=[i for i in before_r if resources.objects[i].get_raw_data()!=before_r[i]]
    return dict(hats=meshes,hat_nodes=hatids,mirror_head=mh,mirror_body=mb,mirror_arms=arms,mirror_hands=hands,created_ui=e.created,changed_resources=changed_r,added_resources=sorted(set(resources.objects)-set(before_r)),added_menu=sorted(set(menu.objects)-set(before_l)),preview_camera_count=0,original_procedural_hats=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=R/'versions/cloudcourt-v27-antes-v28');ap.add_argument('--output',type=Path,default=R/'visuals-v28-customization');a=ap.parse_args()
    assert a.source.resolve()!=a.output.resolve() and 'working' not in a.output.resolve().parts
    resources=UnityPy.load(str(a.source/'resources.assets')).file;menu=UnityPy.load(str(a.source/'level0')).file
    report=apply_customization_v28(resources,menu);a.output.mkdir(exist_ok=True,parents=True)
    for name,f in [('resources.assets',resources),('level0',menu)]:
        data=f.save();(a.output/name).write_bytes(data);report[name]=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
    (a.output/'customization-v28-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()







