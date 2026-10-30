"""Original procedural achievement cosmetics; no original game image samples.

apply_rewards_art_v29(resources, level0) adds 3x3 atlases + disabled material
carrier children only. Existing avatar geometry/UVs and visible materials stay
unchanged. Reward choices1..3 use atlas cells0..2 (top row, left to right).
"""
from pathlib import Path
import argparse,copy,hashlib,json,math,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from PIL import Image,ImageDraw,ImageFont
from fix_gloves_v16 import hierarchy
from build_landing_v20 import clone,save,ptr,raw
from build_customization_art_v19 import outfit_tile,atlas,CELL

A=R/'assets/rewards-v29'
NAMES=['Sunset','Skyline','Emerald']
FACES=['Wink','Focus','Starry Joy']
ACCENTS=['#ffcf58','#63d7f4','#a4f0cf']
SHIRT_COLORS=['#d76b45','#227fa8','#277c62']

def reward_face(index):
    im=Image.new('RGB',(1024,1024),'#ffca46');d=ImageDraw.Draw(im)
    ink='#252d39';white='#fff6e7';accent=ACCENTS[index]
    def star(cx,cy,r):
        points=[]
        for i in range(10):
            a=-math.pi/2+i*math.pi/5;s=r if i%2==0 else r*.46
            points.append((cx+s*math.cos(a),cy+s*math.sin(a)))
        d.polygon(points,fill=ink)
    if index==0:
        d.arc((246,330,438,475),185,355,fill=ink,width=27)
        d.ellipse((639,347,707,459),fill=ink);d.ellipse((649,356,670,386),fill=white)
        d.arc((288,475,750,824),0,180,fill=ink,width=28)
        d.arc((323,490,715,796),0,180,fill=white,width=28)
        for x in (204,746):d.ellipse((x,576,x+76,620),fill=accent)
    elif index==1:
        # Sport visor shape as an expression mark; no eyewear mesh needed.
        for x in (342,684):
            d.arc((x-99,305,x+99,481),0,180,fill=ink,width=28)
            d.line((x-89,330,x+77,308),fill=ink,width=20)
        d.arc((371,568,655,735),8,173,fill=ink,width=25)
        d.ellipse((719,500,753,535),fill=white)
        d.polygon([(776,452),(792,489),(830,505),(792,522),(776,559),(759,522),(722,505),(759,489)],fill=accent)
    else:
        star(344,405,79);star(680,405,79)
        d.arc((288,475,750,824),0,180,fill=ink,width=28)
        d.arc((323,490,715,796),0,180,fill=white,width=28)
        for x in (204,746):d.ellipse((x,576,x+76,620),fill=accent)
        d.polygon([(790,250),(806,284),(841,300),(806,316),(790,351),(773,316),(739,300),(773,284)],fill=white)
    return im.resize((CELL,CELL),Image.Resampling.LANCZOS)

def reward_outfit(index):
    # Reuse our own whole legacy UV tile layout, including its palette swatches.
    # Repaint all clothing pixels procedurally; no base-game art is sampled.
    im=outfit_tile(6).resize((1024,1024),Image.Resampling.LANCZOS)
    d=ImageDraw.Draw(im);accent=ACCENTS[index]
    base=SHIRT_COLORS[index]
    d.rectangle((0,0,1023,1023),fill=base)
    palette=['#ffca46',base,'#222b3b','#161d29','#332b25','#e9e8df','#263340','#ca9e60']
    for i,color in enumerate(palette):
        x=512+(i%4)*128;y=(i//4)*128;d.rectangle((x,y,x+127,y+127),fill=color)
    if index==0:
        # Layered dusk bands and a small sun, confined to the shirt-front UV.
        for y,color in [(650,'#a34740'),(730,'#c35e47'),(810,'#ed925f'),(890,'#ffb266')]:d.rectangle((0,y,511,y+79),fill=color)
        d.ellipse((154,698,358,902),fill='#ffd183');d.rectangle((0,832,511,1023),fill=base)
        for y in (854,880,906):d.line((128,y,384,y),fill='#ffb266',width=10)
    elif index==1:
        d.polygon([(0,810),(512,676),(512,742),(0,876)],fill='#267ab1')
        d.polygon([(0,894),(512,760),(512,785),(0,919)],fill=accent)
        for x,height in [(130,49),(178,77),(229,112),(281,64),(331,95)]:
            d.rectangle((x,870-height,x+32,870),fill='#d4eeff')
    else:
        d.polygon([(0,665),(256,788),(512,665),(512,722),(256,850),(0,722)],fill='#2c9a7c')
        d.polygon([(0,752),(256,877),(512,752),(512,775),(256,902),(0,775)],fill=accent)
        d.polygon([(256,625),(295,679),(256,733),(217,679)],fill='#e4f5c4')
    # Neckline and seam coordinates match the inherited whole-tile mapping.
    d.rectangle((181,512,331,545),fill='#ffca46');d.pieslice((180,464,332,625),0,180,fill='#ffca46')
    d.arc((172,457,340,635),0,180,fill=accent,width=12)
    d.line((27,512,78,694),fill=accent,width=8);d.line((485,512,434,694),fill=accent,width=8)
    d.line((43,799,43,978),fill=accent,width=5);d.line((469,799,469,978),fill=accent,width=5)
    d.line((50,999,460,999),fill=accent,width=7)
    return im.resize((CELL,CELL),Image.Resampling.LANCZOS)

def create_rewards_art_v29(out=A):
    out.mkdir(parents=True,exist_ok=True)
    faces=[reward_face(i) for i in range(3)];outfits=[reward_outfit(i) for i in range(3)]
    fa=atlas(faces*3);oa=atlas(outfits*3)
    fa.save(out/'reward-faces-atlas.png');oa.save(out/'reward-outfits-atlas.png')
    preview=Image.new('RGB',(1140,850),'#edf1f0');d=ImageDraw.Draw(preview)
    fontpath=R/'assets/shared/fonts/CloudcourtBubble.ttf';font=ImageFont.truetype(str(fontpath),24)
    for i in range(3):
        x=i*380
        preview.paste(faces[i].resize((312,312)),(x+34,25))
        preview.paste(outfits[i].crop((0,256,256,512)).resize((312,312)),(x+34,366))
        d.rounded_rectangle((x+34,704,x+346,742),radius=15,fill=ACCENTS[i])
        d.text((x+190,774),f'{NAMES[i]} / {FACES[i]}',font=font,fill='#172b46',anchor='mm')
    preview.save(out/'preview-rewards-v29.png')
    catalog=dict(version=29,reward_choices={'0':'Base','1':'Sunset','2':'Skyline','3':'Emerald'},cells={'1':0,'2':1,'3':2},faces=FACES,shirt_hex=SHIRT_COLORS,accent_hex=ACCENTS,atlas_pixels=[1536,1536],cell_pixels=512,offset_formula='(cell%3/3, (2-cell//3)/3)',layout='Same complete legacy tile as customization-v19: face full cell; outfit visible shirt is lower-left quadrant. Existing base mesh UV/tiling is retained.',head_tiling=[1,1],body_tiling=[1,1],atlas_division="Baked into existing native mesh UVs; material tiling must remain unit scale",unused_cells='Repeat reward row to avoid uninitialized artwork',copyright='Original procedural Cloudcourt art. No game images, photo textures, external image samples, or base-game meshes are delivered here.')
    (out/'catalog.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
    (out/'LICENSE.txt').write_text('Cloudcourt v29 achievement art\n\nThe PNG artwork and color designs in this folder were authored procedurally for Cloudcourt. They contain no sampled original-game images, third-party artwork, or original-game geometry. Artwork may be used, modified, and redistributed with the Cloudcourt mod under CC0-1.0.\n\nThe preview lettering uses the existing CloudcourtBubble font; keep that font\'s existing license notice if distributing the font itself. No font binary is copied into this folder.\n',encoding='utf-8')
    return fa,oa,catalog

def apply_rewards_art_v29(resources,level0):
    before_r={i:o.get_raw_data() for i,o in resources.objects.items()};before_l={i:o.get_raw_data() for i,o in level0.objects.items()}
    gs,ts,paths=hierarchy(resources)
    bodyid=paths['NetworkPlayer/PhysicalBody']
    headid=paths['NetworkPlayer/PhysicalBody/Physical Head/Visual Head Root/Head']
    shirtid=paths['NetworkPlayer/PhysicalBody/Physical Torso/Scaler (1)/Body']
    menuparent=hierarchy(level0)[2]['Menu/CC_Customization']
    fa,oa,catalog=create_rewards_art_v29()
    def named(file,kind,name):return next((o for o in file.objects.values() if o.type.name==kind and o.read_typetree().get('m_Name')==name),None)
    def component(file,tid,kind):
        go=file.objects[file.objects[tid].read_typetree()['m_GameObject']['m_PathID']]
        return next(file.objects[x['component']['m_PathID']] for x in go.read_typetree()['m_Component'] if file.objects[x['component']['m_PathID']].type.name==kind)
    textures={};materials={}
    for name,im,tid in [('Face',fa,headid),('Outfit',oa,shirtid)]:
        tex=named(resources,'Texture2D','Cloudcourt v29 Reward '+name) or clone(resources,resources.objects[1301])
        texture=tex.read();texture.set_image(im.convert('RGBA'),target_format=12,mipmap_count=9);texture.save();raw(tex,tex.data)
        td=tex.read_typetree();td['m_Name']='Cloudcourt v29 Reward '+name;td['m_TextureSettings'].update(m_WrapU=1,m_WrapV=1,m_FilterMode=2);save(tex,td);textures[name]=tex.path_id
        originalmat=resources.objects[component(resources,tid,'MeshRenderer').read_typetree()['m_Materials'][0]['m_PathID']]
        mat=named(resources,'Material','Cloudcourt v29 Reward '+name) or clone(resources,originalmat)
        md=copy.deepcopy(originalmat.read_typetree());md['m_Name']='Cloudcourt v29 Reward '+name
        for key,value in md['m_SavedProperties']['m_TexEnvs']:
            if key=='_MainTex':value['m_Texture']=ptr(tex.path_id)
        save(mat,md);materials[name]=mat.path_id
    def remap(file,tree):
        if file is resources:return
        dependency=next(i+1 for i,e in enumerate(file.externals) if e.path.replace('\\','/').rsplit('/',1)[-1].lower()=='resources.assets')
        def walk(v):
            if isinstance(v,dict):
                if set(v)=={'m_FileID','m_PathID'} and v['m_PathID']:
                    if not v['m_FileID']:v['m_FileID']=dependency
                    else:
                        src=resources.externals[v['m_FileID']-1]
                        match=next((i+1 for i,e in enumerate(file.externals) if e.path==src.path),None)
                        if match is None:file.externals.append(copy.deepcopy(src));match=len(file.externals)
                        v['m_FileID']=match
                else:
                    for vv in v.values():walk(vv)
            elif isinstance(v,list):
                for vv in v:walk(vv)
        walk(tree)
    def source_nodes(file,parent):
        pg,pt,pp=hierarchy(file);rootpath=next(p for p,t in pp.items() if t==parent)+'/CC_RewardSources'
        if rootpath in pp:return {'root':pp[rootpath],'idempotent':True}
        sourcego=resources.objects[ts[headid]['m_GameObject']['m_PathID']]
        rootgo=clone(file,sourcego);root=clone(file,resources.objects[headid])
        gd=rootgo.read_typetree();gd.update(m_Name='CC_RewardSources',m_IsActive=False,m_Component=[{'component':ptr(root.path_id)}],m_Layer=5 if file is level0 else 0,m_TagString='Untagged',m_StaticEditorFlags=0);save(rootgo,gd)
        td=root.read_typetree();td.update(m_GameObject=ptr(rootgo.path_id),m_Father=ptr(parent),m_Children=[],m_LocalPosition=dict(x=0.,y=0.,z=0.),m_LocalRotation=dict(x=0.,y=0.,z=0.,w=1.),m_LocalScale=dict(x=1.,y=1.,z=1.));save(root,td)
        par=file.objects[parent];pd=par.read_typetree();pd['m_Children'].append(ptr(root.path_id));save(par,pd)
        children={}
        for name,tid in [('Face',headid),('Outfit',shirtid)]:
            go=clone(file,resources.objects[ts[tid]['m_GameObject']['m_PathID']]);tr=clone(file,resources.objects[tid]);mr=clone(file,component(resources,tid,'MeshRenderer'));mf=clone(file,component(resources,tid,'MeshFilter'))
            gd=go.read_typetree();gd.update(m_Name=name,m_IsActive=False,m_Component=[{'component':ptr(o.path_id)} for o in (tr,mr,mf)],m_Layer=5 if file is level0 else 0,m_TagString='Untagged',m_StaticEditorFlags=0);save(go,gd)
            d=tr.read_typetree();d.update(m_GameObject=ptr(go.path_id),m_Father=ptr(root.path_id),m_Children=[],m_LocalPosition=dict(x=0.,y=0.,z=0.),m_LocalRotation=dict(x=0.,y=0.,z=0.,w=1.),m_LocalScale=dict(x=1.,y=1.,z=1.));save(tr,d)
            rd=mr.read_typetree();fd=mf.read_typetree();rd['m_Materials']=[ptr(materials[name])];remap(file,rd);remap(file,fd)
            rd.update(m_GameObject=ptr(go.path_id),m_Enabled=False,m_CastShadows=0,m_ReceiveShadows=False,m_StaticBatchInfo=dict(firstSubMesh=0,subMeshCount=0),m_StaticBatchRoot=ptr(0),m_ProbeAnchor=ptr(0),m_LightProbeVolumeOverride=ptr(0));fd['m_GameObject']=ptr(go.path_id);save(mr,rd);save(mf,fd)
            td['m_Children'].append(ptr(tr.path_id));children[name]=dict(transform=tr.path_id,renderer=mr.path_id,material=rd['m_Materials'][0])
        save(root,td);return dict(root=root.path_id,children=children)
    nodes={'avatar':source_nodes(resources,bodyid),'menu':source_nodes(level0,menuparent)}
    changed_r=[i for i,b in before_r.items() if resources.objects[i].get_raw_data()!=b];changed_l=[i for i,b in before_l.items() if level0.objects[i].get_raw_data()!=b]
    assert set(changed_r)<=set([bodyid]),changed_r
    assert set(changed_l)<=set([menuparent]),changed_l
    return dict(textures=textures,materials=materials,nodes=nodes,rewards=catalog,changed_existing_resources=changed_r,changed_existing_menu=changed_l,new_resource_objects=len(resources.objects)-len(before_r),new_menu_objects=len(level0.objects)-len(before_l),base_geometry_changed=False,base_materials_changed=False,source_renderers_enabled=False,colliders_added=0,scripts_added=0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=R/'versions/cloudcourt-v28-antes-v29');p.add_argument('--output',type=Path,default=R/'visuals-v29-rewards');a=p.parse_args()
    assert a.output.resolve()!=a.input.resolve() and 'working' not in a.output.resolve().parts
    resources=UnityPy.load(str(a.input/'resources.assets')).file;level0=UnityPy.load(str(a.input/'level0')).file
    report=apply_rewards_art_v29(resources,level0);a.output.mkdir(exist_ok=True)
    for name,file in [('resources.assets',resources),('level0',level0)]:
        data=file.save();(a.output/name).write_bytes(data);report[name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    (R/'analysis/v29-rewards-art.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
