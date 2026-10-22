"""Local rasterization of the real mesh and newly authored UV atlas."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
vertices=[];uv=[];triangles=[]
for line in (R/'analysis/Volleyball.obj').read_text().splitlines():
    p=line.split()
    if not p:continue
    if p[0]=='v':vertices.append(list(map(float,p[1:4])))
    elif p[0]=='vt':uv.append(list(map(float,p[1:3])))
    elif p[0]=='f':triangles.append([(int(x.split('/')[0])-1,int(x.split('/')[1])-1) for x in p[1:]])
verts=np.array(vertices);verts-=verts.mean(axis=0);verts/=np.linalg.norm(verts,axis=1).max();uv=np.array(uv)
tex=np.asarray(Image.open(R/'analysis/Mikasa-texture-readback.png').convert('RGB'))
size=480;canvas=Image.new('RGB',(size*3,560),'#eceff2')
for view,(angle,pitch) in enumerate([(0,1.57),(.65,.55),(2.1,-.35)]):
    ca,sa=np.cos(angle),np.sin(angle)
    cp,sp=np.cos(pitch),np.sin(pitch)
    rot=np.array([[ca,0,sa],[0,1,0],[-sa,0,ca]])@np.array([[1,0,0],[0,cp,-sp],[0,sp,cp]])
    v=verts@rot.T;xy=v[:,:2]*200+240;xy[:,1]=480-xy[:,1]
    pixels=np.full((size,size,3),[236,239,242],dtype=np.uint8);zbuf=np.full((size,size),-np.inf)
    for face in triangles:
        vi=[x[0] for x in face];ti=[x[1] for x in face]
        a,b,c=xy[vi];lo=np.maximum(np.floor(np.min([a,b,c],axis=0)).astype(int),0);hi=np.minimum(np.ceil(np.max([a,b,c],axis=0)).astype(int)+1,size)
        if np.any(hi<=lo):continue
        xx,yy=np.meshgrid(np.arange(lo[0],hi[0])+.5,np.arange(lo[1],hi[1])+.5)
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-9:continue
        w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w2=1-w0-w1
        zz=w0*v[vi[0],2]+w1*v[vi[1],2]+w2*v[vi[2],2]
        dest=zbuf[lo[1]:hi[1],lo[0]:hi[0]];mask=(w0>=0)&(w1>=0)&(w2>=0)&(zz>dest)
        if not mask.any():continue
        u=w0*uv[ti[0],0]+w1*uv[ti[1],0]+w2*uv[ti[2],0]
        vv=w0*uv[ti[0],1]+w1*uv[ti[1],1]+w2*uv[ti[2],1]
        tx=np.clip((u*1023).astype(int),0,1023);ty=np.clip(((1-vv)*1023).astype(int),0,1023)
        nx=(xx-240)/200;ny=(240-yy)/200;nz=np.sqrt(np.maximum(0,1-nx*nx-ny*ny))
        light=np.clip(.65+.35*(-.3*nx+.4*ny+.85*nz),.3,1)
        rgb=np.clip(tex[ty,tx]*light[...,None],0,255).astype(np.uint8)
        dest[mask]=zz[mask];pixels[lo[1]:hi[1],lo[0]:hi[0]][mask]=rgb[mask]
    rendered=Image.fromarray(pixels)
    if view==0:rendered=rendered.rotate(90)
    canvas.paste(rendered,(view*size,0))
d=ImageDraw.Draw(canvas);d.text((24,494),'MIKASA BEACH PRO BV550C - adapted to original game mesh',fill='#27364b');d.text((24,518),'Local mesh preview. Not a screenshot of the game. Original 18-panel geometry preserved.',fill='#536477')
canvas.save(R/'assets/Mikasa-mesh-preview.png')
print(R/'assets/Mikasa-mesh-preview.png')
