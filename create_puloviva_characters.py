"""Original procedural character artwork and rounded rig-compatible geometry.
No original game texture or mesh vertices are used to draw these characters.
Unity bind matrices are retained only to connect the new geometry to animations.
"""
from pathlib import Path
import sys,math,json,copy,struct,hashlib
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import UnityPy
A=R/'assets/cloudcourt-v16';A.mkdir(parents=True,exist_ok=True)
OUT=R/'characters-v16';OUT.mkdir(exist_ok=True)
BASE=R/'versions/v13-antes-personagens'
SKINS=['#e9b98d','#f0c5a6','#b98055','#f0c3a2','#e7b589','#744a39','#edbb9b']
HAIRS=['#171b24','#5a3929','#30261e','#342b27','#e4dfd9','#f1f0e9','#392820']
SHIRTS=['#171d27','#f1f0e9','#537c79','#404d65','#762f49','#263b4b','#426178']
PANTS=['#141922','#20242c','#aa906c','#293e59','#435a61','#29323b','#aa9276']
SHOES=['#2466d3','#141a20','#624a38','#f0e6d6','#762f49','#4c3329','#293a49']
def font(n,bold=False):return ImageFont.truetype('C:/Windows/Fonts/arial'+('bd' if bold else '')+'.ttf',n)
def face(n,emoji=False):
    im=Image.new('RGB',(512,512),'#ffca46' if emoji else SKINS[n]);d=ImageDraw.Draw(im)
    ink='#252d39';eye='#513827' if n==6 and not emoji else ink
    if emoji:
        if n==0:
            d.rounded_rectangle((94,171,239,273),24,fill=ink);d.rounded_rectangle((273,171,418,273),24,fill=ink);d.line((235,192,277,192),fill=ink,width=16)
            d.line((115,189,145,189),fill='#607489',width=10);d.line((294,189,324,189),fill='#607489',width=10)
        elif n==1:
            for x in (173,339):d.ellipse((x-69,161,x+69,299),outline=ink,width=15);d.ellipse((x-13,216,x+13,251),fill=ink)
            d.line((242,224,270,224),fill=ink,width=12)
        elif n==2:
            d.arc((109,187,224,261),185,335,fill=ink,width=14);d.arc((286,174,405,248),185,335,fill=ink,width=14)
            d.line((109,160,218,173),fill=ink,width=13);d.line((288,151,400,138),fill=ink,width=13)
        else:
            for x,y in ((175,226),(336,203)):
                d.ellipse((x-49,y-58,x+49,y+58),fill='white');d.ellipse((x-10,y-11,x+17,y+24),fill=ink)
        if n==2:d.arc((160,273,379,373),10,160,fill=ink,width=15)
        else:
            d.pieslice((160,267,355,409),0,180,fill=ink)
            if n==1:d.rectangle((224,315,254,352),fill='white');d.rectangle((259,315,289,352),fill='white')
            elif n==3:d.ellipse((269,349,322,399),fill='#f18d91')
            else:d.rectangle((194,318,324,330),fill='white')
        return im
    # Hairline is original artwork; volumetric hair is added to each mesh.
    hair=HAIRS[n]
    if n==0:
        d.polygon([(0,0),(512,0),(512,124),(382,99),(273,47),(256,97),(229,47),(119,109),(0,128)],fill=hair)
    elif n==1:
        d.rectangle((0,0,512,72),fill=hair)
        for x in range(16,512,48):d.ellipse((x-33,23,x+39,101+(x%3)*4),fill=hair)
    elif n==3:d.rectangle((0,0,512,65),fill=hair);d.rectangle((0,0,55,480),fill=hair);d.rectangle((457,0,512,480),fill=hair)
    elif n in (4,5):pass # White hair is geometry; no painted arc across the face.
    else:d.polygon([(0,0),(512,0),(512,76),(344,50),(103,116),(0,79)],fill=hair)
    for x in (171,341):
        if n==4:d.arc((x-32,192,x+32,239),180,355,fill=ink,width=7)
        else:
            d.ellipse((x-26,202,x+26,245),fill='#fff8ed');d.ellipse((x-12,210,x+12,242),fill=eye);d.ellipse((x-4,214,x+2,222),fill='white')
        d.line((x-40,176,x+33,170 if n==6 else 176),fill=hair,width=14 if n==6 else 9)
    if n<6:
        for x in (171,341):
            if n in (2,3):d.rounded_rectangle((x-65,176,x+65,278),radius=13,outline=ink,width=10)
            else:d.ellipse((x-64,166,x+64,294),outline=ink,width=9)
        d.line((236,221,276,221),fill=ink,width=9)
    d.line((255,242,241,291,266,296),fill='#b67a5a' if n!=5 else '#52342c',width=7)
    if n in (4,5):
        for x in (105,377):d.arc((x-30,287,x+30,321),5,170,fill='#b88068' if n==4 else '#9b6e54',width=4)
        d.arc((190,330,322,411),0,180,fill=ink,width=8)
        if n==4:d.ellipse((90,287,154,329),fill='#e99d91');d.ellipse((358,287,422,329),fill='#e99d91')
    elif n==6:
        d.arc((136,243,378,454),0,180,fill=hair,width=27)
        d.arc((205,303,307,356),180,360,fill=hair,width=15)
        for x,y in ((155,302),(163,323),(353,306),(345,326)):d.ellipse((x,y,x+5,y+7),fill=hair)
        d.arc((210,324,305,369),5,174,fill='#aa6864',width=9)
    else:d.arc((197,313,317,385),0,180,fill='#764937',width=8)
    return im
def atlas(n,emoji=False):
    im=Image.new('RGB',(1024,1024),'#1c2430');im.paste(face(n,emoji),(0,0));d=ImageDraw.Draw(im)
    palette=['#ffca46' if emoji else SKINS[n], '#171d2b' if emoji else SHIRTS[n], '#222b3b' if emoji else PANTS[n], '#161d29' if emoji else SHOES[n], '#332b25' if emoji else HAIRS[n], '#e9e8df','#263340','#ca9e60']
    for i,c in enumerate(palette):
        x=512+(i%4)*128;y=(i//4)*128;d.rectangle((x,y,x+127,y+127),fill=c)
    # Front of clothing, with fabric seams; occupies lower-left quadrant.
    d.rectangle((0,512,511,1023),fill=palette[1]);d.line((42,548,42,1023),fill=palette[2],width=5);d.line((470,548,470,1023),fill=palette[2],width=5)
    if emoji or n==5:
        d.polygon([(181,512),(331,512),(256,839)],fill='#f8f3e9')
        d.polygon([(160,512),(224,604),(187,667),(256,845),(117,632)],fill='#3c4d63')
        d.polygon([(352,512),(288,604),(325,667),(256,845),(395,632)],fill='#3c4d63')
        d.polygon([(242,555),(269,555),(280,704),(256,744),(232,704)],fill=['#3f8db4','#b86d67','#b18c49','#6d9c82'][n%4])
        d.line((256,847,256,1023),fill='#0b121d',width=5)
        for y in (877,957):d.ellipse((270,y,281,y+11),fill='#c8af77')
    elif n==2:
        d.polygon([(154,512),(358,512),(256,625)],fill='#f1e9d8');d.polygon([(214,562),(256,583),(298,562),(298,605),(256,583),(214,605)],fill='#bc694c')
        for x in range(15,512,72):d.line((x,620,x,1023),fill='#91a9a0',width=3)
        for y in range(640,1024,70):d.line((0,y,512,y),fill='#91a9a0',width=3)
        d.rectangle((333,706,423,798),outline='#d5dfcc',width=5);d.line((353,689,353,748),fill='#24354b',width=8)
    elif n==4:
        d.polygon([(183,512),(329,512),(256,694)],fill='#f3dfcc');d.line((256,692,256,1024),fill='#a65367',width=8)
        for y in range(730,1000,75):d.ellipse((268,y,281,y+13),fill='#efd0a8')
        for x,y in [(91,771),(384,869),(101,941)]:
            for dx,dy in [(-10,0),(10,0),(0,-10),(0,10)]:d.ellipse((x+dx-9,y+dy-9,x+dx+9,y+dy+9),fill='#f5cbb8')
    elif n==0:
        d.arc((159,451,353,640),0,180,fill='#505e71',width=9);d.line((27,512,74,683),fill='#505e71',width=8);d.line((485,512,438,683),fill='#505e71',width=8)
    else:d.arc((174,467,338,601),0,180,fill='#bcbfc0' if n==1 else '#253c50',width=8)
    name=('player' if emoji else 'bot')+f'-{n+1:02d}'
    im.save(A/(name+'-atlas.png'));face(n,emoji).save(A/(name+'-rosto.png'))
    return im
ATLASES=[atlas(i) for i in range(7)];PLAYERS=[atlas(i,True) for i in range(4)]
def uv_palette(i):return ((512+(i%4)*128+64)/1024,1-((i//4)*128+64)/1024)
def v3(x,y,z):return dict(x=float(x),y=float(y),z=float(z))
def aabb(v):v=np.asarray(v);return {'m_Center':v3(*((v.min(0)+v.max(0))/2)),'m_Extent':v3(*((v.max(0)-v.min(0))/2))}
class Model:
    def __init__(self):self.v=[];self.n=[];self.uv=[];self.b=[];self.tri=[]
    def ellipsoid(self,center,radius,bone=0,color=0,mapping=None,axis=None,segments=20,rings=12):
        c=np.array(center);rad=np.array(radius);start=len(self.v);rot=np.eye(3) if axis is None else axis
        for j in range(rings+1):
            phi=math.pi*j/rings
            for i in range(segments+1):
                theta=2*math.pi*i/segments;q=np.array([math.sin(phi)*math.cos(theta),math.cos(phi),math.sin(phi)*math.sin(theta)])
                p=rot@(q*rad)+c;n=rot@(q/rad);n/=np.linalg.norm(n)
                uv=uv_palette(color)
                if mapping=='face' and q[2]>.1:uv=(.25-q[0]*.245,.75+q[1]*.245)
                if mapping=='shirt' and q[2]>.1:uv=(.25-q[0]*.245,.25+q[1]*.245)
                self.v.append(p.tolist());self.n.append(n.tolist());self.uv.append(uv);self.b.append(bone)
        for j in range(rings):
            for i in range(segments):
                a=start+j*(segments+1)+i;b=a+segments+1
                # Correct outward winding (Unity front faces follow this convention).
                self.tri.extend([(a,a+1,b),(a+1,b+1,b)])
    def limb(self,a,b,width,depth,bone,color):
        a=np.array(a);b=np.array(b);direction=b-a;length=np.linalg.norm(direction);y=direction/length
        x=np.cross(y,np.array([0,1,0] if abs(y[2])>.95 else [0,0,1]));x/=np.linalg.norm(x);z=np.cross(x,y);rot=np.stack([x,y,z],axis=1)
        start=len(self.v);center=(a+b)/2
        self.ellipsoid(center,(width,width,depth),bone,color,axis=rot,segments=16,rings=12)
        for k in range(start,len(self.v)):
            v=np.array(self.v[k]);h=np.dot(v-center,y)
            self.v[k]=(v+y*(length/2)*(1 if h>1e-6 else -1 if h< -1e-6 else 0)).tolist()
    def softbox(self,c,r,bone,color,mapping=None):
        start=len(self.v);self.ellipsoid(c,r,bone,color,mapping,segments=24,rings=16)
        for k in range(start,len(self.v)):
            q=(np.array(self.v[k])-c)/r;v=np.sign(q)*np.abs(q)**.45
            self.v[k]=(np.array(c)+v*r).tolist()
            n=np.sign(q)*np.abs(q)**1.55/r;n/=np.linalg.norm(n);self.n[k]=n.tolist()
    def serialize(self,template,name,skin=True):
        d=copy.deepcopy(template);count=len(self.v);assert count<65536
        channels=[dict(stream=0,offset=0,format=0,dimension=0) for _ in range(14)]
        for channel,offset,fmt,dim in [(0,0,0,3),(1,12,0,3),(2,24,0,4),(4,40,0,2)]+([(12,48,0,4),(13,64,10,4)] if skin else []):channels[channel]=dict(stream=0,offset=offset,format=fmt,dimension=dim)
        data=[]
        for p,n,uv,b in zip(self.v,self.n,self.uv,self.b):
            data.append(struct.pack('<12f',*(p+n+[1,0,0,1]+list(uv))))
            if skin:data.append(struct.pack('<4f4I',1,0,0,0,b,0,0,0))
        d['m_Name']=name;d['m_VertexData']={'m_VertexCount':count,'m_Channels':channels,'m_DataSize':b''.join(data)}
        d['m_IndexFormat']=0;d['m_IndexBuffer']=struct.pack('<'+'H'*(len(self.tri)*3),*(i for tri in self.tri for i in tri))
        bounds=aabb(self.v);d['m_SubMeshes']=[dict(firstByte=0,indexCount=len(self.tri)*3,topology=0,baseVertex=0,firstVertex=0,vertexCount=count,localAABB=bounds)]
        d['m_LocalAABB']=bounds;d['m_StreamData']=dict(offset=0,size=0,path='');d['m_IsReadable']=True
        d['m_BakedConvexCollisionMesh']=b'';d['m_BakedTriangleCollisionMesh']=b''
        # Recompute conservative bone bounds; no stale compressed geometry.
        for b in range(len(d.get('m_BonesAABB',[]))):d['m_BonesAABB'][b]={'m_Min':v3(*np.min(self.v,axis=0)),'m_Max':v3(*np.max(self.v,axis=0))}
        return d
def character(n):
    m=Model();m.softbox((0,1.50,0),(.43,.52,.25),1,1,'shirt');m.softbox((0,1.03,0),(.38,.23,.25),17,2)
    for side,upper,lower,foot,ua,la,hand in [(-1,3,4,7,9,10,11),(1,2,5,6,14,15,16)]:
        x=side*.222
        m.limb((x,.99,0),(x,.64,0),.18,.20,upper,2)
        m.limb((x,.60,0),(x,.17,0),.125,.13,lower,0 if n in (0,1) else 2)
        m.softbox((x,.13,.10),(.18,.13,.30),foot,3)
        m.limb((side*.38,1.94,0),(side*.78,1.94,0),.18,.18,ua,0 if n==0 else 1)
        m.limb((side*.78,1.94,0),(side*1.04,1.94,0),.13,.14,ua,0 if n in (0,1) else 1)
        m.limb((side*1.04,1.94,0),(side*1.45,1.94,0),.125,.13,la,0 if n in (0,1) else 1)
        m.softbox((side*1.51,1.94,0),(.14,.12,.13),hand,0)
        m.ellipsoid((side*1.51,1.85,.10),(.09,.09,.07),hand,0,segments=12,rings=8)
    m.ellipsoid((0,2.08,0),(.18,.22,.18),12,0)
    m.ellipsoid((0,2.55,0),(.50,.51,.44),12,0,'face',segments=32,rings=20)
    for x in (-.49,.49):m.ellipsoid((x,2.53,0),(.07,.11,.07),12,0,segments=12,rings=8)
    hair_start=len(m.v)
    if n==0:
        for x in (-.17,.17):m.ellipsoid((x,2.78,-.015),(.22,.14,.32),12,4)
    elif n==1:
        for x,y,z in [(-.22,2.79,0),(0,2.86,0),(.22,2.79,0),(-.13,2.83,.19),(.13,2.83,.19),(-.13,2.83,-.19),(.13,2.83,-.19)]:m.ellipsoid((x,y,z),(.14,.12,.14),12,4,segments=12,rings=8)
    elif n==3:
        m.ellipsoid((0,2.48,-.29),(.38,.43,.17),12,4)
        m.ellipsoid((0,2.74,-.08),(.37,.20,.30),12,4)
        for x in (-.29,.29):m.ellipsoid((x,2.44,-.14),(.12,.44,.18),12,4)
    elif n==4:
        m.ellipsoid((0,2.76,-.04),(.35,.18,.30),12,4);m.ellipsoid((0,2.74,-.32),(.17,.17,.16),12,4)
    elif n==5:
        for x in (-.28,.28):m.ellipsoid((x,2.69,-.04),(.10,.16,.26),12,4)
    else:m.ellipsoid((-.05 if n==6 else 0,2.79,-.035),(.36,.18 if n==6 else .10,.29),12,4)
    for k in range(hair_start,len(m.v)):
        v=np.array(m.v[k]);m.v[k]=(np.array([0,2.55,0])+(v-[0,2.48,0])*1.34).tolist()
    return m
MODELS=[character(i) for i in range(7)]

def render_model(model,atlas,size=600):
    # Orthographic front preview of the authored mesh, lighting and UVs.
    v=np.array(model.v);n=np.array(model.n);uv=np.array(model.uv);tri=np.array(model.tri)
    im=np.zeros((size,size,3),np.uint8);im[:]=[228,235,237];depth=np.full((size,size),-1e9)
    scale=size/3.7;xy=np.stack([size/2-v[:,0]*scale,size*.91-v[:,1]*scale],axis=1);tex=np.array(atlas)
    for ids in tri:
        p=xy[ids];u=p[1]-p[0];w=p[2]-p[0];area=u[0]*w[1]-u[1]*w[0]
        if abs(area)<1e-5:continue
        x0=max(0,int(p[:,0].min()));x1=min(size-1,int(p[:,0].max())+1);y0=max(0,int(p[:,1].min()));y1=min(size-1,int(p[:,1].max())+1)
        if x0>x1 or y0>y1:continue
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1];a=((p[1,0]-xx)*(p[2,1]-yy)-(p[1,1]-yy)*(p[2,0]-xx))/area;b=((p[2,0]-xx)*(p[0,1]-yy)-(p[2,1]-yy)*(p[0,0]-xx))/area;c=1-a-b
        z=a*v[ids[0],2]+b*v[ids[1],2]+c*v[ids[2],2];ok=(a>=0)&(b>=0)&(c>=0)&(z>depth[y0:y1+1,x0:x1+1])
        u=a*uv[ids[0],0]+b*uv[ids[1],0]+c*uv[ids[2],0];w=a*uv[ids[0],1]+b*uv[ids[1],1]+c*uv[ids[2],1]
        norm=a[...,None]*n[ids[0]]+b[...,None]*n[ids[1]]+c[...,None]*n[ids[2]];light=np.clip(.65+.35*(norm@np.array([-.3,.5,.8])),.3,1)
        col=tex[np.clip(((1-w)*1023).astype(int),0,1023),np.clip((u*1023).astype(int),0,1023)]*light[...,None]
        im[y0:y1+1,x0:x1+1][ok]=col[ok].astype(np.uint8);depth[y0:y1+1,x0:x1+1][ok]=z[ok]
    return Image.fromarray(im)
for i,m in enumerate(MODELS):
    render_model(m,ATLASES[i]).save(A/f'bot-{i+1:02d}-modelo.png')
    (A/f'bot-{i+1:02d}-geometry.json').write_text(json.dumps({'vertices':m.v,'normals':m.n,'uv':m.uv,'bones':m.b,'triangles':m.tri}))
gallery=Image.new('RGB',(1800,1200),'#e4ebed')
for i,m in enumerate(MODELS):
    tile=render_model(m,ATLASES[i],450);d=ImageDraw.Draw(tile);d.text((225,424),f'BOT {i+1}',font=font(22,True),fill='#263340',anchor='mm');gallery.paste(tile,((i%4)*450,(i//4)*550))
gallery.save(A/'bots-visuais.png')
players=Image.new('RGB',(2048,512))
for i in range(4):players.paste(face(i,True),(i*512,0))
players.save(A/'players-emojis.png')

def ptr(i,f=0):return dict(m_FileID=f,m_PathID=i)
def clone(file,source,data):
    o=copy.copy(source);o.assets_file=file;o.path_id=max(file.objects)+1;o.data=source.get_raw_data();file.objects[o.path_id]=o;o.save_typetree(data);return o.path_id
def texture(file,id,im):t=file.objects[id].read();t.set_image(im,mipmap_count=1);t.save()
def plain_material(file,id,tex):
    d=file.objects[id].read_typetree();p=d['m_SavedProperties'];d['m_ShaderKeywords']='';p['m_TexEnvs']=[('_MainTex',{'m_Texture':ptr(tex),'m_Scale':{'x':1.,'y':1.},'m_Offset':{'x':0.,'y':0.}})]
    p['m_Colors']=[('_Color',dict(r=1.,g=1.,b=1.,a=1.)),('_EmissionColor',dict(r=0.,g=0.,b=0.,a=1.))];p['m_Floats']=[(k,.15 if k=='_Glossiness' else v) for k,v in p['m_Floats']];file.objects[id].save_typetree(d)

def build_assets():
    E=UnityPy.load(str(R/'working/VolleyballFever_Data'));files={o.assets_file.name:o.assets_file for o in E.objects}
    for name in ['resources.assets','sharedassets0.assets']:
        f=UnityPy.load(str(BASE/name)).file;f.parent=E;files[name]=f
    f=files['sharedassets0.assets'];template=f.objects[133].read_typetree()
    meshes=[clone(f,f.objects[133],m.serialize(template,f'Cloudcourt_Bot_{i+1}')) for i,m in enumerate(MODELS)]
    # All legacy variants map deterministically to seven complete appearances.
    material_bots={};family={'Runner':0,'Footballer':1,'Nerd':2,'Hippie':3,'Grandma':4,'Grandpa':5,'Biker':6,'Tourist':0,'Clown':1,'Emo':3,'Mountie':5,'ShopKeeper':6,'Racer':1,'Prisoner':2,'Luchador':6,'Cheerleader':4}
    for o in list(f.objects.values()):
        if o.type.name!='Material':continue
        d=o.read_typetree();name=d['m_Name']
        if not name.startswith('SimpleCitizens_'):continue
        bot=family[name.split('_')[1]];material_bots[o.path_id]=bot
        tex=next(v['m_Texture']['m_PathID'] for k,v in d['m_SavedProperties']['m_TexEnvs'] if k=='_MainTex')
        texture(f,tex,ATLASES[bot]);plain_material(f,o.path_id,tex)
    replaced=0
    for o in list(f.objects.values()):
        if o.type.name!='SkinnedMeshRenderer':continue
        d=o.read_typetree();mesh=d['m_Mesh']['m_PathID']
        if d['m_Mesh']['m_FileID']!=0:continue
        if mesh==133:
            mat=d['m_Materials'][0]['m_PathID'];bot=material_bots.get(mat,0);d['m_Mesh']=ptr(meshes[bot]);d['m_AABB']=aabb(MODELS[bot].v);d['m_UpdateWhenOffscreen']=True;replaced+=1
        elif 134<=mesh<=147:d['m_Enabled']=False
        else:continue
        o.save_typetree(d)
    for name in ['sharedassets0.assets']: (OUT/name).write_bytes(files[name].save())
    # Player atlas and round head / jacket use the existing shared material.
    f=files['resources.assets'];atlas4=Image.new('RGB',(4096,1024))
    for i,t in enumerate(PLAYERS):atlas4.paste(t,(i*1024,0))
    td=f.objects[42].read_typetree();td['m_Name']='Cloudcourt_Player_EmojiAtlas';texid=clone(f,f.objects[42],td);texture(f,texid,atlas4);plain_material(f,4,texid)
    for meshid,center,rad,mapping in [(67,(0,0,0),(.355,.355,.355),'face'),(68,(0,0,0),(.44,.50,.28),'shirt')]:
        m=Model();m.ellipsoid(center,rad,0,1,mapping,segments=32,rings=20)
        # Four horizontal cells; native per-player material offset selects one.
        m.uv=[(u/4,v) for u,v in m.uv];f.objects[meshid].save_typetree(m.serialize(f.objects[meshid].read_typetree(),'Cloudcourt_Player_'+mapping,False))
    # Bind both visible player surfaces explicitly (the stock head used an external material).
    for o in list(f.objects.values()):
        if o.type.name!='GameObject':continue
        gd=o.read_typetree();components=[f.objects[c['component']['m_PathID']] for c in gd['m_Component']]
        if any(c.type.name=='MeshFilter' and c.read_typetree()['m_Mesh']==ptr(k) for c in components for k in (67,68)):
            for c in components:
                if c.type.name=='MeshRenderer':
                    rd=c.read_typetree();rd['m_Materials']=[ptr(4)];c.save_typetree(rd)
    # Hide the stock decorative hair attached above the player head.
    gd=f.objects[ f.objects[751].read_typetree()['m_GameObject']['m_PathID'] ].read_typetree();gd['m_IsActive']=False
    f.objects[f.objects[751].read_typetree()['m_GameObject']['m_PathID']].save_typetree(gd)
    # Original navy / cream net design, with staggered diamond weave.
    net=Image.new('RGBA',(256,256),(0,0,0,0));d=ImageDraw.Draw(net)
    for k in range(-256,512,64):d.line((k,0,k+256,256),fill='#1d3846',width=5);d.line((k,0,k-256,256),fill='#1d3846',width=5)
    net.save(A/'rede-malha.png');texture(f,51,net)
    tape=Image.new('RGB',(1024,512),'#edddbb');d=ImageDraw.Draw(tape)
    for x in range(-60,1100,96):d.polygon([(x,0),(x+38,0),(x+86,512),(x+48,512)],fill='#177f8a')
    for y in (110,365):d.rounded_rectangle((320,y-38,704,y+38),18,fill='#193e51');d.text((512,y),'CLOUDCOURT',font=font(48,True),fill='#f4e5bf',anchor='mm')
    tape.save(A/'rede-fita.png');texture(f,52,tape)
    (OUT/'resources.assets').write_bytes(f.save())
    report={'bot_renderers_replaced':replaced,'bot_mesh_ids':meshes,'player_atlas_texture':texid,'models':[{'vertices':len(m.v),'triangles':len(m.tri)} for m in MODELS]}
    (OUT/'characters.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':build_assets()
