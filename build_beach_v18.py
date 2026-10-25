"""Original low-poly palm and new sculpted sand; edit the current map in place.
Preserves serialized schemas, shaders, court and collider components.
"""
from pathlib import Path
import sys,math,json,struct,copy
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import numpy as np,UnityPy
from PIL import Image,ImageDraw
from fix_gloves_v16 import _model_class
A=R/'assets/beach-v18';A.mkdir(exist_ok=True);W=R/'working/VolleyballFever_Data'
def vec(p):return dict(zip('xyz',map(float,p)))
def rotation(q):
 x,y,z,w=[q[k] for k in 'xyzw'];return np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])
def quaternion(m):
 # Robust conversion using the dominant diagonal (including 180-degree parents).
 vals=[1+np.trace(m),1+m[0,0]-m[1,1]-m[2,2],1-m[0,0]+m[1,1]-m[2,2],1-m[0,0]-m[1,1]+m[2,2]];i=int(np.argmax(vals));s=math.sqrt(max(vals[i],0))*2
 if i==0:q=[(m[2,1]-m[1,2])/s,(m[0,2]-m[2,0])/s,(m[1,0]-m[0,1])/s,s/4]
 elif i==1:q=[s/4,(m[0,1]+m[1,0])/s,(m[0,2]+m[2,0])/s,(m[2,1]-m[1,2])/s]
 elif i==2:q=[(m[0,1]+m[1,0])/s,s/4,(m[1,2]+m[2,1])/s,(m[0,2]-m[2,0])/s]
 else:q=[(m[0,2]+m[2,0])/s,(m[1,2]+m[2,1])/s,s/4,(m[1,0]-m[0,1])/s]
 return dict(zip('xyzw',q))
def palm():
 m=_model_class()()
 def vertex(p,uv):m.v.append(list(p));m.n.append([0,1,0]);m.uv.append(uv);m.b.append(0);return len(m.v)-1
 def triangle(a,b,c):m.tri.append((a,b,c))
 # Curved, tapered trunk: eight sides and eight height sections.
 for j in range(9):
  t=j/8;c=np.array([.7*t*t,5.4*t,.15*math.sin(t*math.pi)]);rad=.31-.15*t
  for i in range(9):
   ang=2*math.pi*i/8;vertex(c+[rad*math.cos(ang),0,rad*math.sin(ang)],(.02+.44*i/8,.02+.96*t))
 for j in range(8):
  for i in range(8):
   a=j*9+i;b=a+9;triangle(a,b,a+1);triangle(a+1,b,b+1)
 # Broad solid faceted fronds, no transparent cards or animated shader.
 for k in range(9):
  angle=2*math.pi*k/9;direction=np.array([math.cos(angle),0,math.sin(angle)]);side=np.array([-math.sin(angle),0,math.cos(angle)]);start=len(m.v)
  for j in range(6):
   t=j/5;center=np.array([.7,5.4,0])+direction*(3.1*t);center[1]+=.75*math.sin(math.pi*t)-1.25*t*t;width=.43*math.sin(math.pi*t)+.025
   for a in (-1,0,1):vertex(center+side*width*a+[0,.1*(1-abs(a))*math.sin(math.pi*t),0],(.52+.46*t,.12+.72*(a+1)/2))
  for j in range(5):
   for i in range(2):
    a=start+j*3+i;b=a+3;triangle(a,a+1,b);triangle(a+1,b+1,b);triangle(b,a+1,a);triangle(b,b+1,a+1)
 # Simple small coconuts, 3 octahedra.
 for p in [[.55,5.18,.22],[.89,5.14,.12],[.62,5.18,-.23]]:
  start=len(m.v)
  for d in [[.16,0,0],[-.16,0,0],[0,.19,0],[0,-.19,0],[0,0,.16],[0,0,-.16]]:vertex(np.array(p)+d,(.25,.48))
  for a,b,c in [(2,0,4),(2,4,1),(2,1,5),(2,5,0),(3,4,0),(3,1,4),(3,5,1),(3,0,5)]:triangle(start+a,start+b,start+c)
 # Bake averaged normals. Duplicate backs of leaves still receive an upward normal.
 normals=np.zeros((len(m.v),3));v=np.asarray(m.v)
 for a,b,c in m.tri:
  n=np.cross(v[b]-v[a],v[c]-v[a]);normals[[a,b,c]]+=n
 lengths=np.linalg.norm(normals,axis=1);normals[lengths<1e-6]=[0,1,0];lengths=np.linalg.norm(normals,axis=1)
 m.n=(normals/lengths[:,None]).tolist();return m
def textures(f):
 n=512;y,x=np.mgrid[:n,:n]/n
 ripple=np.sin(2*np.pi*(y*9+.22*np.sin(2*np.pi*x*2)))
 grain=np.random.default_rng(18).normal(0,1,(n,n));shade=ripple*3+grain*.85+2*np.sin(2*np.pi*x)
 rgb=np.clip(np.array([239,207,146])+shade[:,:,None],0,255).astype('uint8');sand=Image.fromarray(rgb)
 normal=np.zeros((n,n,4),dtype='uint8');normal[:]=[128,128,255,128];normal[:,:,1]=np.clip(128+np.cos(2*np.pi*y*9)*9,0,255).astype('uint8')
 atlas=Image.new('RGB',(512,512),'#74b958');d=ImageDraw.Draw(atlas);d.rectangle((0,0,255,511),fill='#b77a42')
 for j in range(0,512,42):d.polygon([(0,j),(255,j+14),(255,j+20),(0,j+6)],fill='#81572f');d.line((0,j+24,255,j+37),fill='#d59d59',width=4)
 for j in range(12,512,24):d.line((265,j,500,j-10),fill='#539d4d',width=3)
 d.line((378,0,378,511),fill='#bdd66c',width=6)
 for i,im,name in [(26,sand,'sand'),(21,Image.fromarray(normal),'sand-normal'),(16,atlas,'palm-atlas')]:
  im.save(A/(name+'.png'));t=f.objects[i].read();t.set_image(im,mipmap_count=10,target_format=4);t.m_Name='Cloudcourt '+name;t.save()
def main():
 f=UnityPy.load(str(W/'sharedassets1.assets')).file;original={i:o.get_raw_data() for i,o in f.objects.items() if o.type.name=='Shader'}
 m=palm();template=f.objects[29].read_typetree();base=UnityPy.load(str(R/'versions/cloudcourt-v17-antes-v18/sharedassets1.assets')).file;oldtri=len(base.objects[29].read_typetree()['m_IndexBuffer'])//6
 f.objects[29].save_typetree(m.serialize(template,'Cloudcourt curved fan palm',False));textures(f)
 terrain=f.objects[67].read_typetree();h=terrain['m_Heightmap'];N=h['m_Resolution'];origin=np.array([-33.539940834,-3.668615818,-85.263917923])
 x=origin[0]+np.arange(N)*h['m_Scale']['x'];z=origin[2]+np.arange(N)*h['m_Scale']['z'];X,Z=np.meshgrid(x,z)
 # New crescent cove and low sweeping dunes, completely flat play/runoff area.
 shore=23+4*np.cos(Z*.055)+7*np.exp(-((Z-48)/15)**2)
 H=np.clip((shore-X)*.11,-2.8,.2)
 H+=3.4*np.exp(-((X+23)/9)**2-((Z-25)/20)**2)+2.5*np.exp(-((X+25)/9)**2-((Z+34)/15)**2)
 H+=1.5*np.exp(-((X-16)/12)**2-((Z-47)/15)**2)
 blend=np.clip(np.maximum(np.abs(X)-12,np.abs(Z)-18)/10,0,1);H*=blend*blend*(3-2*blend)
 values=np.rint(np.clip((H-origin[1])/h['m_Scale']['y'],0,1)*32766).astype(np.int16);h['m_Heights']=values.ravel().tolist();norm=values.astype(float)/32766
 bounds=[];errors=[];patches=(N-1)//16
 while patches:
  span=(N-1)//patches
  for j in range(patches):
   for i in range(patches):
    p=norm[j*span:(j+1)*span+1,i*span:(i+1)*span+1];bounds.extend([float(p.min()),float(p.max())])
    if span==16:errors.append(0.);continue
    step=span//16;coarse=p[::step,::step];q=np.arange(span+1)/step;lo=np.minimum(q.astype(int),15);t=q-lo
    interp=(1-t[:,None])*((1-t[None,:])*coarse[lo[:,None],lo[None,:]]+t[None,:]*coarse[lo[:,None],lo[None,:]+1])+t[:,None]*((1-t[None,:])*coarse[lo[:,None]+1,lo[None,:]]+t[None,:]*coarse[lo[:,None]+1,lo[None,:]+1])
    errors.append(float(np.abs(p-interp).max()))
  patches//=2
 assert len(errors)==len(h['m_PrecomputedError']);h['m_PrecomputedError']=errors;h['m_MinMaxPatchHeights']=bounds;terrain['m_Name']='Cloudcourt / Sunbeam Cove';f.objects[67].save_typetree(terrain)
 for i in [65,66]:
  d=f.objects[i].read_typetree();d['m_TileSize']={'x':5.,'y':5.};d['m_NormalScale']=.25;f.objects[i].save_typetree(d)
 for i,b in original.items():assert f.objects[i].get_raw_data()==b
 (W/'sharedassets1.assets').write_bytes(f.save())
 placements=[(-20,-26),(-26,-29),(-22,-37),(-23,26),(-18,34),(-27,38),(18,40),(24,44),(28,48),(18,-39),(25,-45),(28,-48),(-25,5),(-23,14),(-20,-10),(-27,-17),(-28,23)]
 def ground(px,pz):return origin[1]+norm[int(np.clip(round((pz-origin[2])/h['m_Scale']['z']),0,N-1)),int(np.clip(round((px-origin[0])/h['m_Scale']['x']),0,N-1))]*h['m_Scale']['y']
 records=[]
 for name in ['level1','level2']:
  sf=UnityPy.load(str(W/name)).file;ts={i:o.read_typetree() for i,o in sf.objects.items() if o.type.name=='Transform'}
  def world(i):
   if not i:return np.eye(4)
   t=ts[i];a=np.eye(4);a[:3,:3]=rotation(t['m_LocalRotation'])@np.diag([t['m_LocalScale'][k] for k in 'xyz']);a[:3,3]=[t['m_LocalPosition'][k] for k in 'xyz'];return world(t['m_Father']['m_PathID'])@a
  palms=[o for o in sf.objects.values() if o.type.name=='GameObject' and (o.read().m_Name.startswith('Palmtree') or o.read().m_Name.startswith('Cloudcourt Fan Palm'))]
  colliders={i:o.get_raw_data() for i,o in sf.objects.items() if 'Collider' in o.type.name}
  for k,o in enumerate(palms):
   d=o.read_typetree();tid=d['m_Component'][0]['component']['m_PathID'];t=ts[tid];px,pz=placements[k%len(placements)];a=np.eye(4);angle=k*2.39996;scale=.82+.08*(k%4)
   a[:3,:3]=rotation(dict(x=0,y=math.sin(angle/2),z=0,w=math.cos(angle/2)))*scale;a[:3,3]=[px,ground(px,pz)-.04,pz]
   local=np.linalg.inv(world(t['m_Father']['m_PathID']))@a;scales=np.linalg.norm(local[:3,:3],axis=0);rot=local[:3,:3]/scales
   assert np.max(np.abs(rot.T@rot-np.eye(3)))<1e-4
   t.update(m_LocalPosition=vec(local[:3,3]),m_LocalScale=vec(scales),m_LocalRotation=quaternion(rot));sf.objects[tid].save_typetree(t)
   d['m_Name']=f'Cloudcourt Fan Palm {k+1:02}';d['m_IsActive']=True;o.save_typetree(d)
   for c in d['m_Component']:
    ob=sf.objects[c['component']['m_PathID']]
    if ob.type.name=='Animator':ad=ob.read_typetree();ad['m_Enabled']=False;ob.save_typetree(ad)
  for ob in sf.objects.values():
   if ob.type.name=='Terrain':
    d=ob.read_typetree();d['m_LightmapIndex']=65535;d['m_HeightmapPixelError']=4.;ob.save_typetree(d)
  for i,b in colliders.items():assert sf.objects[i].get_raw_data()==b
  (W/name).write_bytes(sf.save());records.append({'scene':name,'palms':len(palms),'colliders_unchanged':True})
 for px,pz in [(0,0),(-5,-10),(5,10),(-11,17),(11,-17)]:assert abs(ground(px,pz))<.002
 # Preview the actual authored palm geometry, plus sand and atlas samples.
 im=Image.new('RGB',(1200,800),'#b9e9ef');draw=ImageDraw.Draw(im);draw.rectangle((0,590,1200,800),fill='#efcf92')
 verts=np.asarray(m.v);proj=np.array([[.86,0,-.5],[.14,-1,.24]]);points=verts@proj.T*91+np.array([570,650]);depth=verts@np.array([.5,.3,.86]);faces=sorted(m.tri,key=lambda t:float(depth[list(t)].mean()))
 atlas=Image.open(A/'palm-atlas.png')
 for tri in faces:
  uv=np.asarray([m.uv[i] for i in tri]).mean(0);color=atlas.getpixel((min(511,int(uv[0]*512)),min(511,int((1-uv[1])*512))));draw.polygon([tuple(points[i]) for i in tri],fill=color)
 im.paste(Image.open(A/'sand.png').resize((240,240)),(30,30));draw.text((30,280),'CLOUDCOURT - SUNBEAM COVE\nOriginal low-poly geometry / sand',fill='#172b46');im.save(A/'preview-palm.png')
 report={'passed':True,'palm_vertices':len(m.v),'palm_triangles':len(m.tri),'previous_triangles':oldtri,'shared_mesh_and_material':True,'texture_size':512,'no_transparency':True,'terrain_resolution_preserved':N,'scenes':records,'preview':'assets/beach-v18/preview-palm.png'}
 (R/'analysis/v18-beach-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
