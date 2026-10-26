"""Offline triangle previews decoded from the actual serialized v22 assets.
Uses actual vertex buffers, transforms, materials and texture UVs. This is an
orthographic software preview, not a Unity/headset lighting or shadow capture.
"""
from pathlib import Path
import sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np,UnityPy
from PIL import Image,ImageDraw,ImageFont
from build_environment_v22 import named,ptr,scoreboard_bounds
from build_scene_v20 import _vertices,_world,_apply
from fix_gloves_v16 import hierarchy
from UnityPy.helpers.MeshHelper import MeshHandler
OUT=R/'visuals-v22-environment'
F={n:UnityPy.load(str(OUT/n)).file for n in ['resources.assets','level1','level3','sharedassets1.assets','sharedassets3.assets']}

def faces(mesh,colors,matrix=None,texture=None):
    h=MeshHandler(mesh.read());h.process();v=np.asarray(h.m_Vertices)
    if matrix is not None:v=_apply(matrix,v)
    d=mesh.read_typetree();ix=np.frombuffer(bytes(d['m_IndexBuffer']),dtype='<u2');out=[]
    uv=np.asarray(h.m_UV0) if h.m_UV0 else None
    for k,s in enumerate(d['m_SubMeshes']):
        tri=ix[s['firstByte']//2:s['firstByte']//2+s['indexCount']].reshape(-1,3)
        for ids in tri:
            points=v[ids];c=np.asarray(colors[min(k,len(colors)-1)])
            if texture is not None and uv is not None:
                u=uv[ids].mean(0);c=np.asarray(texture.getpixel((min(texture.width-1,int((u[0]%1)*texture.width)),min(texture.height-1,int((1-u[1]%1)*texture.height)))))[:3]
            n=np.cross(points[1]-points[0],points[2]-points[0]);length=np.linalg.norm(n)
            if length<1e-9:continue
            shade=.76+.24*abs(float(np.dot(n/length,np.array([.3,.85,.43]))));out.append((points,tuple(np.clip(c*shade,0,255).astype(int))))
    return out

def render(fs,eye,target,size=(1500,950),title='',subtitle=''):
    forward=np.asarray(target)-eye;forward=forward/np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward)
    allv=np.concatenate([p for p,c in fs]);xy=np.c_[allv@right,allv@up];lo=xy.min(0);hi=xy.max(0);scale=min((size[0]-140)/(hi[0]-lo[0]),(size[1]-240)/(hi[1]-lo[1]));center=(lo+hi)/2
    def project(p):return (np.c_[p@right,p@up]-center)*[scale,-scale]+[size[0]/2,(size[1]+85)/2]
    rgb=np.empty((size[1],size[0],3),dtype=np.uint8);rgb[:]=[196,229,237];depth=np.full((size[1],size[0]),np.inf)
    for p,c in fs:
        q=project(p);z=p@forward
        x0=max(0,int(np.floor(q[:,0].min())));x1=min(size[0]-1,int(np.ceil(q[:,0].max())))
        y0=max(110,int(np.floor(q[:,1].min())));y1=min(size[1]-47,int(np.ceil(q[:,1].max())))
        if x0>x1 or y0>y1:continue
        a,b,cc=q;den=(b[1]-cc[1])*(a[0]-cc[0])+(cc[0]-b[0])*(a[1]-cc[1])
        if abs(den)<1e-9:continue
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1];xx=xx+.5;yy=yy+.5
        w0=((b[1]-cc[1])*(xx-cc[0])+(cc[0]-b[0])*(yy-cc[1]))/den
        w1=((cc[1]-a[1])*(xx-cc[0])+(a[0]-cc[0])*(yy-cc[1]))/den;w2=1-w0-w1
        zz=w0*z[0]+w1*z[1]+w2*z[2];view=depth[y0:y1+1,x0:x1+1]
        mask=(w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6)&(zz<view)
        view[mask]=zz[mask];rgb[y0:y1+1,x0:x1+1][mask]=c
    im=Image.fromarray(rgb);d=ImageDraw.Draw(im)
    d.rectangle((0,0,size[0],110),fill='#f3f4f0');d.text((36,20),title,font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',29),fill='#172b46');d.text((36,64),subtitle,font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22),fill='#172b46')
    d.rectangle((0,size[1]-46,size[0],size[1]),fill='#f3f4f0');d.text((30,size[1]-34),'Actual asset geometry/material preview. Offline camera; Unity lighting and VR appearance require playtest.',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17),fill='#172b46')
    return im,project,scale

def skyline():
    s=F['sharedassets1.assets'];scene=F['level1'];pal=s.objects[69].read().image.convert('RGB');atlas=s.objects[16].read().image.convert('RGB')
    fs=faces(named(s,'Mesh','Cloudcourt Orla Skyline'),[(255,255,255)],texture=pal)
    fs+=faces(named(s,'Mesh','Cloudcourt Dry Sand Runoff'),[(239,207,146)])
    gs,ts,ps=hierarchy(scene)
    for path,t in ps.items():
        if '/Cloudcourt Fan Palm ' in path:fs+=faces(s.objects[29],[(255,255,255)],_world(ts,t),atlas)
    im,_,_=render(fs,np.array([50,26,75]),np.array([-35,12,0]),title='ORLA / ENLARGED CITY SKYLINE',subtitle='Actual 17-building mesh: 1,572 triangles, one opaque skyline draw. Static palm geometry preserved.')
    im.save(OUT/'orla-actual-mesh-preview.png')

def posts():
    f=F['resources.assets'];gs,ts,ps=hierarchy(f);fs=[]
    for p,t in ps.items():
        if '/NetPole/' not in p:continue
        go=gs[ts[t]['m_GameObject']['m_PathID']]
        mf=next((f.objects[c['component']['m_PathID']] for c in go['m_Component'] if f.objects[c['component']['m_PathID']].type.name=='MeshFilter'),None)
        mr=next((f.objects[c['component']['m_PathID']] for c in go['m_Component'] if f.objects[c['component']['m_PathID']].type.name=='MeshRenderer'),None)
        if not mf or not mr:continue
        colors=[]
        for ref in mr.read_typetree()['m_Materials']:
            col=dict(f.objects[ref['m_PathID']].read_typetree()['m_SavedProperties']['m_Colors'])['_Color'];colors.append([col[k]*255 for k in 'rgb'])
        fs+=faces(f.objects[mf.read_typetree()['m_Mesh']['m_PathID']],colors,_world(ts,t))
    im,_,_=render(fs,np.array([9,3,6]),np.array([5.1,1,0]),size=(850,1000),title='NET POST / METAL + PADDING',subtitle='Silver metal; dark gray unbranded padding.')
    im.save(OUT/'post-actual-mesh-preview.png')

def board():
    f=F['level3'];m=named(f,'Mesh','Cloudcourt Scoreboard Rectangle Backings');fs=faces(m,[(6,7,8),(255,255,255)])
    # Only near-end board, drawn directly from serialized triangles.
    fs=[(p,c) for p,c in fs if p[:,2].mean()>0]
    im,project,scale=render(fs,np.array([0,6.8,10]),np.array([0,6.8,17.7]),size=(1200,1000),title='INDOOR / FITTED WHITE SCOREBOARD',subtitle='3.259 x 2.593 m backing; black 4 cm border. Live text hierarchy unchanged.')
    d=ImageDraw.Draw(im)
    for text,px,y in [('CLOUDCOURT VR',28,71),('99 : 99',76,-6.1),('0 - 0',40,-73.8)]:
        pos=project(np.array([[0,6.8+y*.013,17.64]]))[0];font=ImageFont.truetype(str(R/'assets/cloudcourt-v16/CloudcourtBubble.ttf'),round(px*.013*scale))
        d.text(tuple(pos),text,font=font,fill='#75cfff' if px==76 else '#293c57',anchor='mm',stroke_width=max(1,round(2.5*.013*scale)),stroke_fill='black')
    im.save(OUT/'board-actual-mesh-preview.png')
if __name__=='__main__':skyline();posts();board();print(str(OUT))
