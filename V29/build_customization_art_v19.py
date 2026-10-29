"""Original Cloudcourt face/outfit atlas authoring and narrow Unity v19 upgrade.

Only the avatar material bindings and mesh UVs change. Existing avatar shape,
tracking, collider and gameplay objects remain intact. No stock game artwork is
used. The first four faces are the existing original Cloudcourt emoji drawings.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import math
import struct
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import numpy as np
import UnityPy
from UnityPy.streams import EndianBinaryReader
from PIL import Image, ImageDraw, ImageFont
from fix_gloves_v16 import hierarchy

A = R / 'assets/customization-v19'
FACE_NAMES = ['Cool', 'Nerd', 'Smirk', 'Goofy', 'Crying', 'Surprised', 'Gigachad', 'Glam', 'Pleading']
OUTFIT_NAMES = ['Black Tank', 'White Tank', 'Black Suit', 'White Suit', 'White Tee',
                'Black Tee', 'Blue Tee', 'Forest Tee', 'Wine Tee']
COLORS = ['#171d29', '#f1f1ea', '#171d2b', '#eeeae0', '#f1f1ea',
          '#171d29', '#2585ce', '#1c5145', '#762f49']
SIZE = 1536
CELL = 512


def font(size):
    return ImageFont.truetype(str(R / 'assets/shared/fonts/CloudcourtBubble.ttf'), size)


def new_face(index):
    """Draw the five new expressions from geometric marks, with no source image."""
    assert 4 <= index <= 8
    im = Image.new('RGB', (1024, 1024), '#ffca46')
    d = ImageDraw.Draw(im)
    ink, white = '#252d39', '#fff8ed'
    # All drawing coordinates use a 512-unit design grid at 2x resolution.
    def ellipse(box, **kw):d.ellipse(tuple(int(x*2) for x in box), **kw)
    def line(points, **kw):
        if 'width' in kw:kw['width'] *= 2
        d.line(tuple(int(x*2) for x in points), **kw)
    def arc(box, start, end, **kw):
        if 'width' in kw:kw['width'] *= 2
        d.arc(tuple(int(x*2) for x in box), start, end, **kw)
    def polygon(points, **kw):d.polygon([(int(x*2),int(y*2)) for x,y in points], **kw)
    if index == 4:
        for x in (172, 340):
            arc((x-43, 167, x+43, 240), 185, 352, fill=ink, width=11)
            line((x-38, 160, x+29, 147), fill=ink, width=10)
            d.rounded_rectangle(tuple(int(v*2) for v in (x-25, 224, x+25, 355)),
                                radius=28, fill='#43b8e8')
            line((x-11, 241, x-11, 324), fill='#b8eeff', width=9)
        arc((193, 330, 320, 414), 187, 352, fill=ink, width=13)
        ellipse((92, 294, 137, 316), fill='#f0a757')
        ellipse((375, 294, 420, 316), fill='#f0a757')
    elif index == 5:
        for x in (174, 338):
            ellipse((x-48, 165, x+48, 277), fill=white)
            ellipse((x-22, 194, x+22, 258), fill=ink)
            ellipse((x-10, 201, x+2, 217), fill='white')
            arc((x-49, 121, x+49, 179), 190, 349, fill=ink, width=10)
        ellipse((215, 303, 298, 414), fill=ink)
        ellipse((238, 369, 284, 401), fill='#e88991')
    elif index == 6:
        # An original strong-jaw cartoon, rather than a photo or meme trace.
        polygon([(83, 289), (131, 387), (215, 439), (298, 439), (382, 387),
                 (430, 289), (391, 359), (314, 405), (199, 405), (120, 359)], fill='#e6a438')
        polygon([(93, 166), (149, 130), (238, 154), (231, 175), (150, 157)], fill=ink)
        polygon([(419, 166), (363, 130), (274, 154), (281, 175), (362, 157)], fill=ink)
        for x in (174, 338):
            arc((x-42, 182, x+42, 235), 10, 168, fill=ink, width=12)
        line((258, 210, 237, 286, 269, 292), fill='#b77c2c', width=10)
        arc((173, 287, 351, 378), 7, 162, fill=ink, width=12)
        line((216, 363, 296, 363), fill='#b77c2c', width=7)
        polygon([(93, 92), (139, 35), (271, 45), (399, 61), (422, 113),
                 (350, 91), (267, 104), (183, 84)], fill='#292c34')
        line((143, 72, 239, 71, 353, 85), fill='#55525a', width=9)
    elif index == 7:
        for x in (175, 338):
            arc((x-47, 174, x+47, 264), 0, 180, fill=ink, width=13)
            for start,end in [((x-35,222),(x-54,206)), ((x-11,247),(x-18,275)),
                              ((x+16,245),(x+25,274)), ((x+37,224),(x+56,208))]:
                line((*start,*end), fill=ink, width=9)
            arc((x-39, 135, x+39, 185), 195, 346, fill='#7c4f32', width=8)
        ellipse((99, 282, 161, 319), fill='#ed8c87')
        ellipse((351, 282, 413, 319), fill='#ed8c87')
        polygon([(194, 353),(225, 330),(255, 344),(284,330),(317,353),
                 (288,384),(256,394),(226,384)], fill='#ba284c')
        arc((208, 336, 304, 382), 8, 172, fill='#e66381', width=10)
        line((220, 355, 291, 355), fill='#84213b', width=5)
    else:
        for x in (176, 337):
            ellipse((x-58, 162, x+58, 292), fill=white)
            ellipse((x-41, 179, x+41, 280), fill='#65432c')
            ellipse((x-29, 190, x+29, 274), fill=ink)
            ellipse((x-24, 186, x+6, 222), fill='white')
            ellipse((x+9, 239, x+23, 254), fill='white')
            arc((x-48, 117, x+48, 176), 8, 173, fill=ink, width=10)
        arc((222, 321, 293, 378), 186, 354, fill=ink, width=11)
        ellipse((111, 297, 163, 326), fill='#f4a066')
        ellipse((350, 297, 402, 326), fill='#f4a066')
    return im.resize((CELL, CELL), Image.Resampling.LANCZOS)


def outfit_tile(index):
    """Whole legacy UV tile: clothing front below-left and solid palette above-right."""
    color = COLORS[index]
    im = Image.new('RGB', (1024, 1024), color)
    d = ImageDraw.Draw(im)
    palette = ['#ffca46', color, '#222b3b', '#161d29', '#332b25', '#e9e8df', '#263340', '#ca9e60']
    for i,c in enumerate(palette):
        x=512+(i%4)*128;y=(i//4)*128;d.rectangle((x,y,x+127,y+127),fill=c)
    # The inherited ellipsoid's front uses the 512x512 lower-left quadrant.
    d.rectangle((0,512,511,1023), fill=color)
    if index in (2,3):
        lapel = '#3c4d63' if index == 2 else '#ccc8bf'
        shirt = '#f8f3e9' if index == 2 else '#242e3f'
        tie = '#3f8db4' if index == 2 else '#b74b64'
        d.polygon([(181,512),(331,512),(256,839)], fill=shirt)
        d.polygon([(160,512),(224,604),(187,667),(256,845),(117,632)], fill=lapel)
        d.polygon([(352,512),(288,604),(325,667),(256,845),(395,632)], fill=lapel)
        d.polygon([(242,555),(269,555),(280,704),(256,744),(232,704)], fill=tie)
        d.line((256,847,256,1023), fill='#0b121d' if index==2 else '#b4b0a8', width=5)
        for y in (877,957):d.ellipse((270,y,281,y+11), fill='#c8af77')
        d.line((46,800,104,808), fill=lapel, width=5)
        d.line((408,808,466,800), fill=lapel, width=5)
    else:
        light = '#91add0' if index in (0,5,6,7,8) else '#9b9c9c'
        if index in (0,1):
            # Broad neckline and shoulder cut-outs communicate the tank silhouette.
            d.rectangle((143,512,369,568),fill='#ffca46')
            d.pieslice((142,425,370,710),0,180,fill='#ffca46')
            d.arc((133,432,379,719),0,180,fill=light,width=12)
            d.pieslice((-100,478,147,825),270,90,fill='#ffca46')
            d.pieslice((365,478,612,825),90,270,fill='#ffca46')
            d.arc((-100,478,147,825),270,90,fill=light,width=9)
            d.arc((365,478,612,825),90,270,fill=light,width=9)
        else:
            d.rectangle((181,512,331,545),fill='#ffca46')
            d.pieslice((180,464,332,625),0,180,fill='#ffca46')
            d.arc((172,457,340,635),0,180,fill=light,width=12)
            d.line((27,512,78,694), fill=light,width=7)
            d.line((485,512,434,694),fill=light,width=7)
        d.line((50,999,460,999),fill=light,width=5)
        d.line((43,799,43,978),fill=light,width=4)
        d.line((469,799,469,978),fill=light,width=4)
        # Small own identity badge, legible at normal avatar scale.
        d.rounded_rectangle((313,713,404,773),radius=15,fill='#172b46')
        d.arc((333,723,384,759),38,317,fill='#ffcf58',width=6)
    return im.resize((CELL,CELL), Image.Resampling.LANCZOS)


def atlas(images):
    out=Image.new('RGB',(SIZE,SIZE))
    for i,im in enumerate(images):out.paste(im,((i%3)*CELL,(i//3)*CELL))
    return out


def grid_preview(images,names,path,clothes=False):
    tile=400;h=470
    out=Image.new('RGB',(tile*3,h*3),'#e8eef0');d=ImageDraw.Draw(out)
    for i,(im,name) in enumerate(zip(images,names)):
        x=(i%3)*tile;y=(i//3)*h
        d.rounded_rectangle((x+10,y+10,x+390,y+453),radius=28,fill='#172b46')
        crop=im.crop((0,256,256,512)).resize((340,340),Image.Resampling.LANCZOS) if clothes else im.resize((340,340),Image.Resampling.LANCZOS)
        out.paste(crop,(x+30,y+28))
        d.text((x+200,y+413),name,font=font(27),fill='#fff1dc',anchor='mm')
    out.save(path)


def create_art():
    A.mkdir(parents=True,exist_ok=True)
    faces=[Image.open(R/f'assets/shared/legacy-art/player-{i+1:02d}-rosto.png').convert('RGB') for i in range(4)]
    faces += [new_face(i) for i in range(4,9)]
    clothes=[outfit_tile(i) for i in range(9)]
    for i,im in enumerate(faces):im.save(A/f'face-{i:02d}-{FACE_NAMES[i].lower()}.png')
    for i,im in enumerate(clothes):im.save(A/f'outfit-{i:02d}-{OUTFIT_NAMES[i].lower().replace(" ","-")}.png')
    face_atlas,body_atlas=atlas(faces),atlas(clothes)
    face_atlas.save(A/'faces-atlas.png');body_atlas.save(A/'outfits-atlas.png')
    grid_preview(faces,FACE_NAMES,A/'preview-faces.png')
    grid_preview(clothes,OUTFIT_NAMES,A/'preview-outfits.png',True)
    catalog={'version':19,'grid':[3,3],'cell_pixels':CELL,'atlas_pixels':[SIZE,SIZE],
             'material_scale':[1.,1.], 'offset_formula':'(index % 3 / 3, (2 - index // 3) / 3)',
             'face_ids':dict(enumerate(FACE_NAMES)),'outfit_ids':dict(enumerate(OUTFIT_NAMES)),
             'default_outfit':2,'copyright':'Original procedural Cloudcourt artwork; no base-game image samples.',
             'mip_levels':9,'texture_format':'BC3/DXT5 opaque',
             'legacy_faces_preserved':[0,1,2,3], 'meshes':'Original v18 positions/normals/indices and hitboxes preserved; only avatar UVs are remapped.'}
    (A/'catalog.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
    return face_atlas,body_atlas,catalog


def readable(obj):
    data=getattr(obj,'data',None)
    if data is not None:
        obj.reader=EndianBinaryReader(data,endian=obj.reader.endian)
        obj.byte_start=0;obj.byte_size=len(data)


def put(obj,data):
    obj.save_typetree(data);readable(obj)


def clone(file,source):
    obj=copy.copy(source);obj.path_id=max(file.objects)+1;obj.assets_file=file
    obj.set_raw_data(source.get_raw_data());readable(obj);file.objects[obj.path_id]=obj
    return obj


def named(file,kind,name):
    return next((o for o in file.objects.values() if o.type.name==kind and o.read_typetree().get('m_Name')==name),None)


def set_atlas(file,im,name):
    obj=named(file,'Texture2D',name) or clone(file,file.objects[1301])
    # Explicit BC3 keeps alpha opaque at every mip. The old implicit BC7 path
    # could encode transparent alpha while RGB-only authoring checks still passed.
    texture=obj.read();texture.set_image(im.convert('RGBA'),target_format=12,mipmap_count=9);texture.save();readable(obj)
    data=obj.read_typetree();data['m_Name']=name;data['m_TextureSettings']['m_WrapU']=data['m_TextureSettings']['m_WrapV']=1
    # Bilinear+mipmaps gives readable expressions without shimmering in the Quest.
    data['m_TextureSettings']['m_FilterMode']=2
    put(obj,data)
    return obj.path_id


def set_material(file,name,texture,default_index=0):
    obj=named(file,'Material',name) or clone(file,file.objects[4])
    data=obj.read_typetree();data['m_Name']=name
    data['m_SavedProperties']['m_TexEnvs']=[('_MainTex',{'m_Texture':dict(m_FileID=0,m_PathID=texture),
        'm_Scale':dict(x=1.,y=1.),'m_Offset':dict(x=(default_index%3)/3,y=(2-default_index//3)/3)})]
    data['m_SavedProperties']['m_Colors']=[('_Color',dict(r=1.,g=1.,b=1.,a=1.)),('_EmissionColor',dict(r=0.,g=0.,b=0.,a=1.))]
    put(obj,data)
    return obj.path_id


def remap_uv(file,ident,face):
    obj=file.objects[ident];data=obj.read_typetree()
    if data['m_Name'].endswith('_v19'):return
    assert data['m_Name'] in ('Cloudcourt_Player_face','Cloudcourt_Player_shirt'),data['m_Name']
    count=data['m_VertexData']['m_VertexCount'];raw=bytearray(data['m_VertexData']['m_DataSize'])
    assert len(raw)==count*48
    for i in range(count):
        u,v=struct.unpack_from('<2f',raw,i*48+40)
        if face:
            u,v=(u*8,(v-.5)*2) if u<.13 else (.98,.02)
            u=max(.002,min(.998,u));v=max(.002,min(.998,v))
        else:u*=4
        struct.pack_into('<2f',raw,i*48+40,u/3,v/3)
    data['m_VertexData']['m_DataSize']=bytes(raw);data['m_Name']+='_v19';put(obj,data)


def apply_customization_assets(resources,art=None):
    """Narrow, idempotent in-memory upgrade; root controls the final file write."""
    face_image,body_image,catalog=art or create_art()
    face_tex=set_atlas(resources,face_image,'Cloudcourt v19 Faces 3x3')
    body_tex=set_atlas(resources,body_image,'Cloudcourt v19 Outfits 3x3')
    face_mat=set_material(resources,'Cloudcourt v19 Face',face_tex)
    body_mat=set_material(resources,'Cloudcourt v19 Outfit',body_tex,2)
    remap_uv(resources,67,True);remap_uv(resources,68,False)
    gs,ts,paths=hierarchy(resources);renderers={}
    for suffix,mat in [('Physical Head/Visual Head Root/Head',face_mat),('Physical Torso/Scaler (1)/Body',body_mat)]:
        path=next(p for p in paths if p.endswith(suffix));go=gs[ts[paths[path]]['m_GameObject']['m_PathID']]
        renderer=next(resources.objects[c['component']['m_PathID']] for c in go['m_Component'] if resources.objects[c['component']['m_PathID']].type.name=='MeshRenderer')
        data=renderer.read_typetree();data['m_Materials']=[dict(m_FileID=0,m_PathID=mat)];put(renderer,data);renderers[suffix]=renderer.path_id
    report={**catalog,'texture_ids':{'face':face_tex,'outfit':body_tex},'material_ids':{'face':face_mat,'outfit':body_mat},
            'renderer_ids':renderers,'mesh_ids':{'head':67,'torso':68},
            'existing_modified_object_ids':[67,68,*renderers.values()],
            'new_objects':[face_tex,body_tex,face_mat,body_mat]}
    (A/'unity-bindings.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();art=create_art()
    if args.input:
        assert args.output and args.input.resolve()!=args.output.resolve(),'Specify a separate output file.'
        file=UnityPy.load(str(args.input)).file;report=apply_customization_assets(file,art)
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(file.save())
        print(json.dumps(report,indent=2))
    else:print(json.dumps(art[2],indent=2))
