"""Preview only original v21 art; reference renders, not headset screenshots."""
from pathlib import Path
import copy,sys,math
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build_environment_v21 import skyline_geometry,ball_art
from build_bot_appearance_v21 import appearance_art,PROFILES
from build_bots_v20 import character
from build_beach_v18 import palm
OUT=R/'visuals-v21-environment';OUT.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',28)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)

def gallery():
    scope,atlases=appearance_art();im=Image.new('RGB',(1500,1100),'#e4ebed');d=ImageDraw.Draw(im)
    for k,n in enumerate(PROFILES):
        m,_=character(scope,n);x=(k%3)*500;y=(k//3)*550
        scope['render_model'](m,atlases[n],460).save(OUT/f'bot-{n+1:02}-appearance.png')
        im.paste(Image.open(OUT/f'bot-{n+1:02}-appearance.png'),(x+20,y))
        d.text((x+250,y+490),PROFILES[n],font=font,fill='#172b46',anchor='mm')
    d.text((1250,805),'Original authored textures\n1024px RGB24 / 11 mips\nMeshes and rig preserved\nReference artwork preview',font=small,fill='#172b46',anchor='mm',align='center')
    im.save(OUT/'bots-appearance-preview.png')

def orla():
    g,_=skyline_geometry();im=Image.new('RGB',(1500,900),'#bde5ed');d=ImageDraw.Draw(im)
    d.rectangle((0,480,1500,900),fill='#44b9c9')
    def project(p):x,y,z=p;return (750+z*9,-y*13+x*2+600)
    # Reference ground/court are flat illustration guides; skyline/palms below
    # are rendered from actual original authored vertices and UV palette.
    d.polygon([project(p) for p in [(-33,0,-73),(25,0,-73),(25,0,73),(-33,0,73)]],fill='#eed3a0')
    colors=['#d4c7ab','#e7dfc9','#d5e0e2','#528497']
    faces=[]
    for points,normal,uv in g.parts[0]:faces.append((np.asarray(points),colors[min(3,int(uv[0][0]*4))]))
    m=palm();atlas=Image.open(R/'assets/beach-v18/palm-atlas.png')
    for px,pz in [(-24,-42),(-24,-22),(-24,0),(-24,22),(-24,42)]:
        v=np.asarray(m.v)+[px,0,pz]
        for tri in m.tri:
            uv=np.asarray([m.uv[i] for i in tri]).mean(0);color=atlas.getpixel((min(511,int(uv[0]*512)),min(511,int((1-uv[1])*512))))
            faces.append((v[list(tri)],color))
    for points,color in sorted(faces,key=lambda p:p[0][:,0].mean()):d.polygon([project(p) for p in points],fill=color)
    # Court location guide in exactly the preserved9x18m rectangle.
    d.polygon([project(p) for p in [(-4.5,.03,-9),(4.5,.03,-9),(4.5,.03,9),(-4.5,.03,9)]],fill='#e7bf7c',outline='white')
    d.text((50,50),'CLOUDCOURT / URBAN SEASIDE',font=font,fill='#172b46')
    d.text((50,95),'17 landward buildings + promenade / 1,572 triangles / one opaque draw',font=small,fill='#172b46')
    d.text((50,840),'Authored geometry preview; reference camera and ground. Not an in-game VR capture.',font=small,fill='#172b46')
    im.save(OUT/'orla-geometry-preview.png')

def arena():
    im=Image.new('RGB',(1300,800),'#e8e4d9');d=ImageDraw.Draw(im)
    # Front section drawn in authored units; closed gable matches the roof,
    # and has both face windings in the serialized geometry.
    def p(x,y):return (650+x*45,740-y*37)
    d.polygon([p(-12,14),p(0,16.02),p(12,14)],fill='#c3d1d2')
    d.line([p(-12,14),p(0,16),p(12,14)],fill='#08090b',width=8)
    for x in (-11.76,-9,-6,0,6,9,11.76):d.line([p(x,0),p(x,13.8)],fill='#08090b',width=7)
    d.line([p(-12,13.8),p(12,13.8)],fill='#08090b',width=8)
    x0,y0=p(-4.9,11.7);x1,y1=p(4.9,1.9);d.rectangle((x0,y0,x1,y1),fill='#060708')
    d.rectangle((x0+7,y0+7,x1-7,y1-7),fill='white')
    d.text((650,485),'00 : 00',font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',65),fill='#172b46',anchor='mm')
    d.text((45,35),'CLOUDCOURT / ARENA ROOF + BOARD',font=font,fill='#172b46')
    d.text((45,78),'Closed 14–16m gable / black structural beams / square white backing with black border',font=small,fill='#172b46')
    d.text((45,770),'Section diagram of authored dimensions; not an in-game screenshot. Live score UI remains unchanged.',font=small,fill='#172b46')
    im.save(OUT/'arena-section-preview.png')

if __name__=='__main__':
    gallery();orla();arena();ball_art().save(OUT/'yellow-blue-ball-atlas.png');print(str(OUT))
