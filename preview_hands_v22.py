"""Render actual serialized v22 triangles; bot skeleton pose comes from native fixture."""
from pathlib import Path
import json,sys,ctypes,math
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np,UnityPy
from PIL import Image,ImageDraw,ImageFont
from fix_gloves_v16 import hierarchy
from build_hands_v22 import build_resources_v22
OUT=R/'analysis/v22-hands-preview.png'
def matrix(t):
 x,y,z,w=[t['m_LocalRotation'][k] for k in 'xyzw'];m=np.eye(4);m[:3,:3]=quatmat((x,y,z,w))@np.diag([t['m_LocalScale'][k] for k in 'xyz']);m[:3,3]=[t['m_LocalPosition'][k] for k in 'xyz'];return m
def quatmat(q):
 x,y,z,w=q;return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def mesh(d):
 vd=d['m_VertexData'];ch=vd['m_Channels'];stride=max(c['offset']+c['dimension']*(4 if c['format'] in (0,10) else 1) for c in ch if c['dimension']);raw=bytes(vd['m_DataSize']);n=vd['m_VertexCount']
 def channel(i,dtype,dim):return np.ndarray((n,dim),dtype,raw,offset=ch[i]['offset'],strides=(stride,np.dtype(dtype).itemsize)).copy()
 return channel(0,'<f4',3),channel(4,'<f4',2),np.frombuffer(bytes(d['m_IndexBuffer']),dtype='<u2').reshape(-1,3),channel(12,'<f4',4) if ch[12]['dimension'] else None,channel(13,'<u4',4) if ch[13]['dimension'] else None

def render(items,size,eye,target):
 W,H=size;image=Image.new('RGB',size,'#f5f6f8');draw=ImageDraw.Draw(image)
 eye=np.array(eye);target=np.array(target);f=target-eye;f=f/np.linalg.norm(f);r=np.cross(f,[0,1,0]);r=r/np.linalg.norm(r);u=np.cross(r,f);basis=np.array([r,u,f])
 triangles=[]
 for v,uv,tri,texture,color in items:
  cam=(v-eye)@basis.T;screen=cam[:,:2]/cam[:,2:3]*min(W,H)*1.4;screen[:,1]*=-1;screen+=[W/2,H*.56]
  for t in tri:
   if (cam[t,2]<=.001).any():continue
   p=v[t];normal=np.cross(p[1]-p[0],p[2]-p[0]);n=np.linalg.norm(normal)
   if n<1e-12:continue
   normal/=n;light=abs(normal@np.array([-.3,.7,.65]));light=.53+.47*light
   if texture is not None:
    a=uv[t].mean(0);col=np.array(texture.getpixel((int(a[0]*texture.width)%texture.width,int((1-a[1])*texture.height)%texture.height))[:3])
   else:col=np.array(color)
   triangles.append((cam[t,2].mean(),screen[t],tuple(int(x) for x in np.clip(col*light,0,255))))
 triangles.sort(reverse=True,key=lambda x:x[0])
 for depth,points,col in triangles:draw.polygon([tuple(x) for x in points],fill=col)
 return image

def main():
 f=UnityPy.load(str(R/'visuals-v22-hands/resources.assets')).file;report=json.loads((R/'visuals-v22-hands/hands-v22-report.json').read_text());g,t,p=hierarchy(f)
 hands={}
 for rec in report['hands']:
  v,uv,tr,_,_=mesh(f.objects[rec['mesh']].read_typetree());hands[rec['side'],rec['pose']]=(v,uv,tr)
 # Native fixture invokes the production post-IK cosmetic override.
 dll=ctypes.CDLL(str(R/'tools/h22.dll'));dll.preview_bot();dll.fixture.argtypes=[ctypes.c_int,ctypes.c_int];dll.fixture.restype=ctypes.c_float
 native={i:dict(position=[dll.fixture(i,k) for k in range(7,10)],rotation=[dll.fixture(i,k) for k in range(10,14)]) for i in (8,10,11,12)}
 sf=UnityPy.load(str(R/'working/VolleyballFever_Data/sharedassets0.assets')).file;sg,st,sp=hierarchy(sf)
 root='SimpleCitizens_Hippie_White';ri=sp[root];base=sp[root+'/Base_mesh'];go=sg[st[base]['m_GameObject']['m_PathID']]
 skin=next(sf.objects[x['component']['m_PathID']].read_typetree() for x in go['m_Component'] if sf.objects[x['component']['m_PathID']].type.name=='SkinnedMeshRenderer')
 md=sf.objects[skin['m_Mesh']['m_PathID']].read_typetree();verts,uv,tr,weights,indices=mesh(md)
 mat=sf.objects[skin['m_Materials'][0]['m_PathID']].read_typetree();texid=next(d['m_Texture']['m_PathID'] for name,d in mat['m_SavedProperties']['m_TexEnvs'] if name=='_MainTex');texture=sf.objects[texid].read().image.convert('RGB')
 # Use all real serialized joint matrices, remove asset-library placement only,
 # and apply the bot's exact game Scaler .5575737357.
 def world(i):
  if i==ri:return np.diag([.5575737357]*3+[1])
  return world(st[i]['m_Father']['m_PathID'])@matrix(st[i])
 bones=[x['m_PathID'] for x in skin['m_Bones']];bind=[]
 for b in md['m_BindPose']:bind.append(np.array([[b[f'e{row}{col}'] for col in range(4)] for row in range(4)]))
 original={i:world(i) for i in bones};changed={}
 for name,j in [('UpperArm_Right_jnt',10),('LowerArm_Right_jnt',11),('Hand_Right_jnt',12)]:
  i=next(i for q,i in sp.items() if q.startswith(root+'/') and q.endswith('/'+name));parent=st[i]['m_Father']['m_PathID'];pw=changed.get(parent,world(parent));wm=pw@matrix(st[i]);scale=np.linalg.norm(wm[:3,:3],axis=0)
  if j in (10,11):wm[:3,:3]=quatmat(native[j]['rotation'])@np.diag(scale)
  else:wm[:3,:3]*=.001
  changed[i]=wm
 def skinned(pose):
  out=np.zeros_like(verts,dtype=float);v=np.c_[verts,np.ones(len(verts))]
  for k,ident in enumerate(bones):
   inds=np.nonzero((indices==k)&(weights>0))[0]
   if not len(inds):continue
   wm=pose.get(ident,original[ident])@bind[k];out[inds]=(v[inds]@wm.T)[:,:3]
  return out
 v=skinned(changed);handid=next(i for q,i in sp.items() if q.startswith(root+'/') and q.endswith('/Hand_Right_jnt'));wrist=changed[handid][:3,3]
 hv,hu,ht=hands['R','Thumb'];hm=np.eye(4);hm[:3,:3]=quatmat(native[8]['rotation'])*1.3;hm[:3,3]=wrist;hv=(np.c_[hv,np.ones(len(hv))]@hm.T)[:,:3]
 botitems=[(v,uv,tr,texture,None),(hv,hu,ht,texture,None)]
 canvas=Image.new('RGB',(1500,1060),'white');d=ImageDraw.Draw(canvas)
 try:font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
 except:font=small=None
 panels=[]
 for pose,col in [('Thumb',0),('Set',1)]:
  for view,row in [('Palm',0),('Side',1)]:
   vv,uu,tt=hands['L',pose];eye=(.40,.12,.16) if view=='Palm' else (.26,.24,.25)
   im=render([(vv,uu,tt,None,(222,165,119))],(460,440),eye,(0,.023,.057));canvas.paste(im,(col*470,row*490+40))
   d.text((col*470+14,row*490+14),f'{pose} | {view}',fill='#19283c',font=font)
 for row,eye in [(0,(2.3,1.7,3.5)),(1,(-2.1,1.7,3.2))]:
  im=render(botitems,(550,440),eye,(0,.85,0));canvas.paste(im,(950,row*490+40));d.text((964,row*490+14),'Actual bot mesh + native post-IK arm',fill='#19283c',font=small)
 d.text((16,1020),'Serialized game meshes; hand frame +Y thumb / +Z fingers. Native pose applied to original bot skeleton. VR view still needs headset validation.',fill='#34465e',font=small)
 canvas.save(OUT)
 data=dict(native_pose=native,actual_bot_rig=dict(root=root,scale=.5575737357,bones=len(bones),right_arm_path='Root_jnt/Hips_jnt/Body_jnt/Spine_jnt/UpperArm_Right_jnt/LowerArm_Right_jnt/Hand_Right_jnt'),actual_hand_meshes=report['hands'],wrist=wrist.tolist(),preview=str(OUT),scope='Actual serialized triangles and bind matrices, actual native production pose quaternions; offline preview, not headset capture')
 (R/'analysis/v22-hands-preview.json').write_text(json.dumps(data,indent=2));print(OUT)
if __name__=='__main__':main()
