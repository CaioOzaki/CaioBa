"""Offline rasterization of actual serialized v26 ball geometry/UV/texture."""
exec(open(__file__.replace('preview_art_v26.py','test_art_v26.py')).read().split('for n,o in f.items():')[0])
from PIL import ImageDraw,ImageFont
h=MeshHandler(f['resources.assets'].objects[62].read());h.process()
verts=np.array(h.m_Vertices);verts/=np.linalg.norm(verts,axis=1).max();uv=np.array(h.m_UV0);tris=np.array([t for part in h.get_triangles() for t in part]);tex=np.array(f['resources.assets'].objects[40].read().image.convert('RGB'))
def sphere(offset,angle,pitch,size=400):
 ca,sa=np.cos(angle),np.sin(angle);cp,sp=np.cos(pitch),np.sin(pitch)
 rot=np.array([[ca,0,sa],[0,1,0],[-sa,0,ca]])@np.array([[1,0,0],[0,cp,-sp],[0,sp,cp]])
 v=verts@rot.T;xy=v[:,:2]*(size*.44)+size/2;xy[:,1]=size-xy[:,1]
 rgb=np.full((size,size,3),[235,240,244],dtype=np.uint8);dep=np.full((size,size),-np.inf)
 for tri in tris:
  q=xy[tri];a,b,c=q;lo=np.maximum(np.floor(q.min(0)).astype(int),0);hi=np.minimum(np.ceil(q.max(0)).astype(int)+1,size)
  if (hi<=lo).any():continue
  yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];xx=xx+.5;yy=yy+.5
  den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-10:continue
  w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w2=1-w0-w1
  z=w0*v[tri[0],2]+w1*v[tri[1],2]+w2*v[tri[2],2];view=dep[lo[1]:hi[1],lo[0]:hi[0]];mask=(w0>=0)&(w1>=0)&(w2>=0)&(z>view)
  if not mask.any():continue
  u=w0*uv[tri[0],0]+w1*uv[tri[1],0]+w2*uv[tri[2],0]+offset;vv=w0*uv[tri[0],1]+w1*uv[tri[1],1]+w2*uv[tri[2],1]
  tx=np.clip((u*2047).astype(int),0,2047);ty=np.clip(((1-vv)*1023).astype(int),0,1023)
  light=np.clip(.68+.32*z,.32,1);color=(tex[ty,tx]*light[...,None]).astype(np.uint8);rgb[lo[1]:hi[1],lo[0]:hi[0]][mask]=color[mask];view[mask]=z[mask]
 return Image.fromarray(rgb)
out=Image.new('RGB',(1200,960),'#ebf0f4');dr=ImageDraw.Draw(out)
for row,(off,title) in enumerate([(0,'INDOOR / YELLOW + BLUE / CloudCourt'),(.5,'BEACH / WHITE + YELLOW + BLUE / CloudCourt')]):
 y=45+row*445;dr.text((25,y-32),title,font=ImageFont.truetype(FONT,24),fill='#102b53')
 for j,(a,p) in enumerate([(0,0),(.4,.45),(2.4,-.3)]):out.paste(sphere(off,a,p),(400*j,y))
dr.text((25,940),'Actual serialized mesh + UV + texture readback. Offline preview; runtime material offset selects venue.',font=ImageFont.truetype(FONT,16),fill='#102b53')
out.save(A/'actual-ball-mesh-preview.png')
# Actual flag mesh has portrait UV0 mapped 1:1; read texture from serialized asset.
flag=f['level3'].objects[report['flags']['texture']].read().image.convert('RGB')
flag.thumbnail((300,900));canvas=Image.new('RGB',(1100,960),'#e5ebef');canvas.paste(flag,(45,20));draw=ImageDraw.Draw(canvas)
draw.text((390,90),'INDOOR / 10 VERTICAL FLAGS',font=ImageFont.truetype(FONT,27),fill='#102b53')
for k,line in enumerate(['Actual portrait texture readback','Own rising-ball emblem','Outlined vertical CLOUDCOURT','Gold border and court details','Two-sided geometry, one opaque draw','Bays at Z -14, -6, 2, 10, 14 m','Wall X +11.2 and -11.2 m','Y 5.15 to 7.65 m','No scripts, physics or colliders added']):draw.text((390,160+65*k),line,font=ImageFont.truetype(FONT,22),fill='#102b53')
canvas.save(A/'actual-arena-flag-preview.png');print(A)

