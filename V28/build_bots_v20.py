"""Nine original rounded bot identities and continuous cartoon hair meshes.

Narrow upgrade of the v19 shared character asset: no reconstruction from an old
game baseline. Player atlases, menus, rig transforms, animation bindings and
physics components are deliberately left untouched.
"""
from pathlib import Path
import ast,copy,hashlib,json,math,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy,numpy as np
from PIL import Image,ImageDraw,ImageFont
from UnityPy.streams import EndianBinaryReader
A=R/'assets/bots-v20'
DATABASE_INDICES=[39,12,30,21,15,18,0,45,6]
FAMILY={'Runner':0,'Footballer':1,'Nerd':2,'Hippie':3,'Grandma':4,'Grandpa':5,'Biker':6,
        'Tourist':7,'Clown':8,'Emo':3,'Mountie':5,'ShopKeeper':6,'Racer':1,'Prisoner':2,
        'Luchador':6,'Cheerleader':4}
NAMES=['Middle Part','Curly','Nerd','Long Hair','Grandma','Grandpa','Side Quiff','Curtain Streak','Tall Middle Part']


def authoring():
    """Load own drawing/mesh definitions without running legacy asset builders."""
    source=ast.parse((R/'create_puloviva_characters.py').read_text(encoding='utf-8'))
    functions={'font','face','atlas','uv_palette','v3','aabb','render_model','Model'}
    source.body=[node for node in source.body if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in functions]
    # The user prefers BOT1's original middle part. Keep its exact pre-v20
    # authoring function available without executing the legacy asset builder.
    legacy=next(node for node in ast.parse((R/'create_puloviva_characters.py').read_text(encoding='utf-8')).body
                if isinstance(node,ast.FunctionDef) and node.name=='character')
    legacy.name='legacy_character_v19';source.body.append(legacy)
    scope=dict(Path=Path,np=np,copy=copy,struct=struct,math=math,Image=Image,ImageDraw=ImageDraw,ImageFont=ImageFont,A=A)
    scope.update(SKINS=['#e9b98d','#f0c5a6','#b98055','#f0c3a2','#e7b589','#744a39','#edbb9b','#f0c5ae','#ecc3a7'],
        HAIRS=['#171b24','#5a3929','#30261e','#342b27','#171b24','#f1f0e9','#392820','#111723','#302a2b'],
        SHIRTS=['#171d27','#f1f0e9','#537c79','#404d65','#762f49','#263b4b','#426178','#141922','#161c25'],
        PANTS=['#141922','#20242c','#aa906c','#293e59','#435a61','#29323b','#aa9276','#191e28','#213d59'],
        SHOES=['#2466d3','#141a20','#624a38','#f0e6d6','#762f49','#4c3329','#293a49','#151a22','#26303f'])
    exec(compile(source,'cloudcourt_original_bot_authoring','exec'),scope)
    original_face=scope['face']
    def face(n,emoji=False):
        if n<7:return original_face(n,emoji)
        im=Image.new('RGB',(1024,1024),scope['SKINS'][n]);d=ImageDraw.Draw(im)
        def box(v):return tuple(round(x*2) for x in v)
        ink='#252a32';hair=scope['HAIRS'][n]
        if n==7:
            # Parted curtain bangs frame the face; one blonde streak is repeated
            # in the volume mesh so it stays visible from other viewing angles.
            d.polygon([tuple(round(v*2) for v in p) for p in [(0,0),(512,0),(512,185),(431,122),(295,47),(256,108),(216,45),(95,126),(0,193)]],fill=hair)
            d.polygon([tuple(round(v*2) for v in p) for p in [(91,68),(125,65),(103,171),(72,246),(52,451),(18,460),(38,238)]],fill='#e4bf62')
            for x in (174,338):
                d.ellipse(box((x-35,200,x+35,255)),fill='#fff8ef')
                d.ellipse(box((x-17,205,x+17,254)),fill='#28242b')
                d.ellipse(box((x-7,209,x+2,220)),fill='white')
                d.arc(box((x-36,197,x+36,256)),186,350,fill=ink,width=9)
                d.line(box((x-43,174,x+33,168)),fill=hair,width=15)
            d.line(box((256,245,242,284,268,290)),fill='#b67e66',width=11)
            d.arc(box((236,283,277,326)),3,178,fill='#cbd3df',width=14)
            d.arc(box((236,283,277,326)),3,178,fill='#6a727e',width=5)
            d.arc(box((201,326,312,386)),3,177,fill='#954f57',width=13)
            d.ellipse(box((113,281,160,308)),fill='#e8a39b');d.ellipse(box((352,281,399,308)),fill='#e8a39b')
        else:
            d.polygon([tuple(round(v*2) for v in p) for p in [(0,0),(512,0),(512,101),(381,88),(276,46),(256,95),(232,46),(108,91),(0,111)]],fill=hair)
            for x in (174,338):
                d.ellipse(box((x-28,201,x+28,249)),fill='#fff8ed');d.ellipse(box((x-12,208,x+12,244)),fill='#3d3029')
                d.rounded_rectangle(box((x-65,177,x+65,277)),radius=22,outline=ink,width=18)
                d.line(box((x-40,155,x+35,159)),fill=hair,width=16)
            d.line(box((239,222,273,222)),fill=ink,width=16)
            d.line(box((256,244,243,285,268,292)),fill='#ba8063',width=11)
            d.arc(box((203,316,313,385)),3,177,fill='#815344',width=13)
        return im.resize((512,512),Image.Resampling.LANCZOS)
    scope['face']=face
    return scope


def scalp(m,front=1.0,back=1.8,color=4):
    """Connected ellipsoid shell with a shorter forehead edge and full nape."""
    start=len(m.v);segments=32;rings=12
    c=np.array([0.,2.55,0.]);r=np.array([.518,.535,.458])
    for j in range(rings+1):
        for i in range(segments+1):
            theta=2*math.pi*i/segments;f=(math.sin(theta)+1)/2
            phi=(front*f+back*(1-f))*j/rings
            q=np.array([math.sin(phi)*math.cos(theta),math.cos(phi),math.sin(phi)*math.sin(theta)])
            n=q/r;n/=np.linalg.norm(n)
            m.v.append((c+q*r).tolist());m.n.append(n.tolist());m.uv.append(((512+(color%4)*128+64)/1024,1-((color//4)*128+64)/1024));m.b.append(12)
    for j in range(rings):
        for i in range(segments):
            a=start+j*(segments+1)+i;b=a+segments+1;m.tri.extend([(a,a+1,b),(a+1,b+1,b)])


def strand(m,points,radius=.06,color=4):
    """Smooth tapered curved locks, with shared rings rather than loose spheres."""
    points=np.array(points);start=len(m.v);slices=12;around=10
    for j in range(slices+1):
        t=j/slices
        p=(1-t)**2*points[0]+2*(1-t)*t*points[1]+t*t*points[2]
        tangent=2*(1-t)*(points[1]-points[0])+2*t*(points[2]-points[1]);tangent/=np.linalg.norm(tangent)
        axis=np.array([0.,0.,1.]) if abs(tangent[2])<.9 else np.array([1.,0.,0.])
        x=np.cross(tangent,axis);x/=np.linalg.norm(x);y=np.cross(tangent,x)
        width=radius*(.12+.88*math.sin(math.pi*t)**.45)
        for k in range(around+1):
            a=2*math.pi*k/around;n=x*math.cos(a)+y*math.sin(a)
            m.v.append((p+n*width).tolist());m.n.append(n.tolist());m.uv.append(((512+(color%4)*128+64)/1024,1-((color//4)*128+64)/1024));m.b.append(12)
    for j in range(slices):
        for k in range(around):
            a=start+j*(around+1)+k;b=a+around+1;m.tri.extend([(a,a+1,b),(a+1,b+1,b)])
    for end in (0,1):
        p=points[0 if not end else 2];n=(points[0]-points[1]) if not end else (points[2]-points[1]);n=n/np.linalg.norm(n)
        center=len(m.v);m.v.append(p.tolist());m.n.append(n.tolist());m.uv.append(((512+(color%4)*128+64)/1024,1-((color//4)*128+64)/1024));m.b.append(12)
        ring=start+(slices if end else 0)*(around+1)
        for k in range(around):m.tri.append((center,ring+k,ring+k+1) if end else (center,ring+k+1,ring+k))


def character(scope,n):
    m=scope['Model']();m.softbox((0,1.50,0),(.43,.52,.25),1,1,'shirt');m.softbox((0,1.03,0),(.38,.23,.25),17,2)
    for side,upper,lower,foot,ua,la,hand in [(-1,3,4,7,9,10,11),(1,2,5,6,14,15,16)]:
        x=side*.222;m.limb((x,.99,0),(x,.64,0),.18,.20,upper,2)
        m.limb((x,.60,0),(x,.17,0),.125,.13,lower,0 if n in (0,1) else 2)
        m.softbox((x,.13,.10),(.18,.13,.30),foot,3)
        m.limb((side*.38,1.94,0),(side*.78,1.94,0),.18,.18,ua,0 if n==0 else 1)
        m.limb((side*.78,1.94,0),(side*1.04,1.94,0),.13,.14,ua,0 if n in (0,1,7,8) else 1)
        m.limb((side*1.04,1.94,0),(side*1.45,1.94,0),.125,.13,la,0 if n in (0,1,7,8) else 1)
        m.softbox((side*1.51,1.94,0),(.14,.12,.13),hand,0)
        m.ellipsoid((side*1.51,1.85,.10),(.09,.09,.07),hand,0,segments=12,rings=8)
    m.ellipsoid((0,2.08,0),(.18,.22,.18),12,0)
    m.ellipsoid((0,2.55,0),(.50,.51,.44),12,0,'face',segments=32,rings=20)
    for x in (-.49,.49):m.ellipsoid((x,2.53,0),(.07,.11,.07),12,0,segments=12,rings=8)
    hair_start=len(m.v)
    if n==0:return scope['legacy_character_v19'](0),hair_start
    scalp(m,.82 if n==5 else .95,2.08 if n in (3,7) else 1.72)
    if n in (0,8):
        for side in (-1,1):
            strand(m,[(side*.04,3.02,.15),(side*.20,3.00,.38),(side*.39,2.79,.26)],.085)
            if n==8:strand(m,[(side*.10,3.04,.22),(side*.28,3.025,-.08),(side*.27,2.91,-.34)],.045,5)
    elif n==1:
        for x,z in [(-.3,0),(-.15,.17),(0,.23),(.15,.17),(.3,0),(-.15,-.16),(0,-.22),(.15,-.16),(0,0)]:
            y=3.02+.06*(1-abs(x)/.35);m.ellipsoid((x,y,z),(.13,.12,.13),12,4,segments=12,rings=8)
    elif n==2:
        strand(m,[(-.30,2.96,.14),(-.05,3.15,.31),(.25,3.03,.22)],.085)
    elif n==3:
        m.ellipsoid((0,2.35,-.34),(.43,.53,.17),12,4)
        for x in (-.24,0,.24):strand(m,[(x*.7,2.92,-.34),(x,2.48,-.52),(x*.8,1.98,-.34)],.017,5)
        for side in (-1,1):
            strand(m,[(side*.24,2.97,-.10),(side*.49,2.65,-.05),(side*.42,1.98,-.19)],.13)
            strand(m,[(side*.14,3.03,.25),(side*.37,2.80,.34),(side*.42,2.38,.12)],.09)
    elif n==4:
        m.ellipsoid((0,2.76,-.43),(.20,.22,.18),12,4)
        for side in (-1,1):strand(m,[(side*.18,3.01,.18),(side*.50,2.93,.05),(side*.42,2.58,-.10)],.09)
    elif n==5:
        for side in (-1,1):strand(m,[(side*.28,2.96,.05),(side*.47,2.78,-.10),(side*.33,2.55,-.31)],.075)
    elif n==6:
        strand(m,[(.29,2.94,.24),(-.09,3.30,.27),(-.39,2.97,.03)],.145)
        strand(m,[(.30,2.93,.05),(.09,3.15,-.09),(-.29,3.02,-.29)],.095)
    elif n==7:
        m.ellipsoid((0,2.28,-.34),(.45,.59,.18),12,4)
        for side in (-1,1):
            strand(m,[(side*.10,3.06,.23),(side*.34,2.92,.47),(side*.43,2.14,.04)],.12)
        strand(m,[(-.13,3.05,.30),(-.35,2.83,.49),(-.40,2.17,.14)],.040,7)
    # Root-owned tall/slender request is visual only: no rig or physics edit.
    if n==8:
        m.v=[(np.array(v)*[.82,1.10,.86]).tolist() for v in m.v]
        inv=np.array([1/.82,1/1.10,1/.86]);m.n=[((np.array(v)*inv)/np.linalg.norm(np.array(v)*inv)).tolist() for v in m.n]
    return m,hair_start


def create_art():
    A.mkdir(parents=True,exist_ok=True);scope=authoring();models=[];atlases=[];hair_ranges=[]
    highlights=['#3b424f','#8a5e40','#5a5149','#695146','#3b424f','#b9c1cc','#69513b','#cbd3df','#67606a']
    for n in range(9):
        im=scope['atlas'](n);d=ImageDraw.Draw(im);d.rectangle((640,128,767,255),fill=highlights[n])
        if n==7:d.rectangle((896,128,1023,255),fill='#e4bf62')
        im.save(A/f'bot-{n+1:02d}-atlas.png');model,start=character(scope,n)
        models.append(model);atlases.append(im);hair_ranges.append([start,len(model.v)])
        front=copy.deepcopy(model);front.v=(np.array(model.v)*.94).tolist()
        scope['render_model'](front,im,500).save(A/f'bot-{n+1:02d}-modelo.png')
        back=copy.deepcopy(model);back.v=[[-x*.94,y*.94,-z*.94] for x,y,z in model.v];back.n=[[-x,y,-z] for x,y,z in model.n]
        scope['render_model'](back,im,400).save(A/f'bot-{n+1:02d}-costas.png')
    gallery=Image.new('RGB',(1500,1800),'#e4ebed');draw=ImageDraw.Draw(gallery)
    titlefont=ImageFont.truetype(str(R/'assets/shared/fonts/CloudcourtBubble.ttf'),24)
    for i in range(9):
        x=(i%3)*500;y=(i//3)*600;gallery.paste(Image.open(A/f'bot-{i+1:02d}-modelo.png'),(x,y))
        draw.text((x+250,y+535),f'{i+1}. {NAMES[i]}',font=titlefont,fill='#172b46',anchor='mm')
    gallery.save(A/'bots-gallery.png')
    report=dict(count=9,names=NAMES,database_indices=DATABASE_INDICES,hair_vertex_ranges=hair_ranges,
                vertices=[len(x.v) for x in models],triangles=[len(x.tri) for x in models],
                grandma_hair=scope['HAIRS'][4],grandma_shirt=scope['SHIRTS'][4],
                new_profiles={'8':'Light skin, long black curtain bangs, blonde streak, dark eyes, septum, black tee and trousers',
                              '9':'Tall slender young light-skinned man, black square glasses, swept-back middle part, dark-blue jeans and black tee'},
                provenance='Original procedural Cloudcourt artwork; rig bindings retained only for animation compatibility.')
    (A/'catalog.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return scope,models,atlases,report


def readable(obj):
    raw=getattr(obj,'data',None)
    if raw is not None:obj.reader=EndianBinaryReader(raw,endian=obj.reader.endian);obj.byte_start=0;obj.byte_size=len(raw)


def put(obj,data):obj.save_typetree(data);readable(obj)


def apply_bots_assets_v20(file,art=None):
    scope,models,atlases,report=art or create_art();mesh_ids=[];changed=set();textures={};renderers=[]
    for i,model in enumerate(models):
        obj=next((o for o in file.objects.values() if o.type.name=='Mesh' and o.read_typetree()['m_Name']==f'Cloudcourt_Bot_{i+1}'),None)
        if obj is None:
            obj=copy.copy(file.objects[4322]);obj.path_id=max(file.objects)+1;obj.assets_file=file
            obj.set_raw_data(file.objects[4322].get_raw_data());readable(obj);file.objects[obj.path_id]=obj
        put(obj,model.serialize(obj.read_typetree(),f'Cloudcourt_Bot_{i+1}',True));mesh_ids.append(obj.path_id);changed.add(obj.path_id)
    material_profiles={}
    for obj in list(file.objects.values()):
        if obj.type.name!='Material':continue
        material=obj.read_typetree();name=material['m_Name']
        if not name.startswith('SimpleCitizens_'):continue
        profile=FAMILY[name.split('_')[1]];material_profiles[obj.path_id]=profile
        tex=next(v['m_Texture'] for k,v in material['m_SavedProperties']['m_TexEnvs'] if k=='_MainTex')
        assert tex['m_FileID']==0;ident=tex['m_PathID']
        if ident in textures:assert textures[ident]==profile
        else:
            textures[ident]=profile;t=file.objects[ident].read()
            # Opaque BC1 avoids the BC7 encoder's alpha issue and cuts the
            # previous RGB24 character texture budget despite adding mipmaps.
            t.set_image(atlases[profile].convert('RGBA'),target_format=10,mipmap_count=9)
            t.save();readable(file.objects[ident]);changed.add(ident)
    for obj in list(file.objects.values()):
        if obj.type.name!='SkinnedMeshRenderer':continue
        data=obj.read_typetree();materials=data['m_Materials'];old=data['m_Mesh']
        if not data['m_Enabled'] or old['m_FileID']!=0 or old['m_PathID'] not in set(mesh_ids):continue
        assert materials and materials[0]['m_FileID']==0
        profile=material_profiles[materials[0]['m_PathID']]
        data['m_Mesh']=dict(m_FileID=0,m_PathID=mesh_ids[profile]);data['m_AABB']=scope['aabb'](models[profile].v)
        data['m_UpdateWhenOffscreen']=True;put(obj,data);changed.add(obj.path_id);renderers.append(obj.path_id)
    assert len(renderers)==48 and len(textures)==48,(len(renderers),len(textures))
    report={**report,'mesh_ids':mesh_ids,'texture_profiles':textures,'renderer_ids':renderers,
            'changed_object_ids':sorted(changed),'materials_and_rig_transforms_unchanged':True,
            'texture_format':'BC1/DXT1 opaque','mip_levels':9,
            'character_texture_bytes':sum(file.objects[i].read_typetree()['m_CompleteImageSize'] for i in textures)}
    (A/'unity-bindings.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path);parser.add_argument('--output',type=Path);args=parser.parse_args()
    art=create_art()
    if args.input:
        assert args.output and args.input.resolve()!=args.output.resolve(),'Write a separate fixture file.'
        file=UnityPy.load(str(args.input)).file;report=apply_bots_assets_v20(file,art)
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(file.save())
    else:report=art[3]
    print(json.dumps(report,indent=2))
