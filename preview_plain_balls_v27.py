from pathlib import Path
import sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np, UnityPy
from PIL import Image,ImageDraw,ImageFont
from UnityPy.helpers.MeshHelper import MeshHandler
A=R/'assets/cloudcourt-v27'; FONT='C:/Windows/Fonts/arialbd.ttf'
f=UnityPy.load(str(R/'visuals-v27-balls/resources.assets')).file
h=MeshHandler(f.objects[62].read());h.process()
verts=np.array(h.m_Vertices);verts/=np.linalg.norm(verts,axis=1).max()
uv=np.array(h.m_UV0);tris=np.array([t for part in h.get_triangles() for t in part]);tex=np.array(f.objects[40].read().image.convert('RGB'))
# Reuse only the triangle rasterizer; no legacy authoring/build execution.
text=(R/'preview_art_v26.py').read_text()
exec(text[text.index('def sphere('):text.index("out=Image.new")])
views=[(0,0),(.65,.45),(1.6,-.25),(2.6,.35)]
out=Image.new('RGB',(1280,760),'#ebf0f4');dr=ImageDraw.Draw(out)
for row,(off,title) in enumerate([(0,'INDOOR - continuous original yellow/blue panels, no printing'),(.5,'BEACH - broad curved panel groups, no printing')]):
 y=36+row*355;dr.text((20,y-28),title,font=ImageFont.truetype(FONT,22),fill='#102b53')
 for j,(a,p) in enumerate(views):out.paste(sphere(off,a,p,320),(320*j,y))
dr.text((20,735),'Actual serialized mesh 62 / material 3 / texture 40 / UV atlas with venue offsets 0 and 0.5.',font=ImageFont.truetype(FONT,16),fill='#102b53')
out.save(A/'actual-ball-mesh-preview.png')
print(A/'actual-ball-mesh-preview.png')

