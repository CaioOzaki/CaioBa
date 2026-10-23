"""New terrain topology on the original Unity terrain component/asset schema."""
from pathlib import Path
import sys,math,json,hashlib
import numpy as np
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
O=R/'maps-v12';O.mkdir(exist_ok=True)
BASE=R/'versions/v11-praia-estavel'
f=UnityPy.load(str(BASE/'sharedassets1.assets')).file
terrain=f.objects[67].read_typetree();h=terrain['m_Heightmap'];N=h['m_Resolution']
origin=np.array([-33.539940834,-3.668615818,-85.263917923])
x=origin[0]+np.arange(N)*h['m_Scale']['x'];z=origin[2]+np.arange(N)*h['m_Scale']['z'];X,Z=np.meshgrid(x,z)
shore=19+6*np.sin(Z*.042)+12*np.exp(-((Z-44)/14)**2)+9*np.exp(-((Z+43)/13)**2)
H=np.clip((shore-X)*.12,-2.8,.35)
H+=6*np.exp(-((X+22)/9)**2-((Z-8)/25)**2)
H+=3.5*np.exp(-((X+19)/8)**2-((Z+38)/17)**2)
H+=2.3*np.exp(-((X-22)/13)**2-((Z-45)/12)**2)
H+=1.8*np.exp(-((X-22)/12)**2-((Z+43)/11)**2)
blend=np.clip(np.maximum(np.abs(X)-12,np.abs(Z)-18)/9,0,1);blend=blend*blend*(3-2*blend)
H*=blend
values=np.rint(np.clip((H-origin[1])/h['m_Scale']['y'],0,1)*32766).astype(np.int16)
h['m_Heights']=values.ravel().tolist()
# Unity stores a complete 64x64 -> 1x1 min/max and error pyramid. Recompute
# each entry from the new heights so old terrain bounds cannot cull new dunes.
norm=values.astype(float)/32766;bounds=[];errors=[]
patches=(N-1)//16
while patches:
 span=(N-1)//patches
 for j in range(patches):
  for i in range(patches):
   p=norm[j*span:(j+1)*span+1,i*span:(i+1)*span+1]
   bounds.extend([float(p.min()),float(p.max())])
   if span==16:errors.append(0.);continue
   step=span//16;coarse=p[::step,::step];q=np.arange(span+1)/step;lo=np.minimum(q.astype(int),15);t=q-lo
   interp=(1-t[:,None])*((1-t[None,:])*coarse[lo[:,None],lo[None,:]]+t[None,:]*coarse[lo[:,None],lo[None,:]+1])+t[:,None]*((1-t[None,:])*coarse[lo[:,None]+1,lo[None,:]]+t[None,:]*coarse[lo[:,None]+1,lo[None,:]+1])
   errors.append(float(np.abs(p-interp).max()))
 patches//=2
assert len(errors)==len(h['m_PrecomputedError']) and len(bounds)==len(h['m_MinMaxPatchHeights'])
h['m_PrecomputedError']=errors;h['m_MinMaxPatchHeights']=bounds;terrain['m_Name']='Caioba / Enseada das Dunas';f.objects[67].save_typetree(terrain)
# Use the game's sand tile across the new coastline instead of its baked
# aerial map of the old island. Shader binaries remain byte-identical.
for i in [65,66]:
 d=f.objects[i].read_typetree();d['m_DiffuseTexture']={'m_FileID':0,'m_PathID':26};d['m_NormalMapTexture']={'m_FileID':0,'m_PathID':21};d['m_TileSize']={'x':4.,'y':4.};d['m_NormalScale']=.65;f.objects[i].save_typetree(d)
(O/'sharedassets1.assets').write_bytes(f.save())
def ground(x,z):
 ix=int(np.clip(round((x-origin[0])/h['m_Scale']['x']),0,N-1));iz=int(np.clip(round((z-origin[2])/h['m_Scale']['z']),0,N-1))
 return origin[1]+norm[iz,ix]*h['m_Scale']['y']
placements=[(-17,-28),(-22,-24),(-15,-34),(-23,24),(-18,30),(-25,34),(17,40),(22,44),(27,46),(17,-40),(23,-44),(28,-46),(-25,4),(-22,12),(-18,-9),(-24,-15),(-29,19)]
for name in ['level1','level2']:
 sf=UnityPy.load(str(R/'versions/v10-antes-mapas'/name)).file
 ts={o.path_id:o.read_typetree() for o in sf.objects.values() if o.type.name=='Transform'}
 def world(tid):
  t=ts[tid];p=np.array([t['m_LocalPosition'][k] for k in 'xyz']);father=t['m_Father']['m_PathID'];return p+world(father) if father else p
 palms=[o for o in sf.objects.values() if o.type.name=='GameObject' and o.read().m_Name.startswith('Palmtree')]
 oldh=np.array(UnityPy.load(str(R/'versions/v10-antes-mapas/sharedassets1.assets')).file.objects[67].read_typetree()['m_Heightmap']['m_Heights']).reshape(N,N)
 for k,o in enumerate(palms):
  d=o.read_typetree();tid=d['m_Component'][0]['component']['m_PathID'];t=ts[tid];old=world(tid);parent=world(t['m_Father']['m_PathID'])
  ix=int(np.clip(round((old[0]-origin[0])/h['m_Scale']['x']),0,N-1));iz=int(np.clip(round((old[2]-origin[2])/h['m_Scale']['z']),0,N-1))
  oldground=origin[1]+oldh[iz,ix]/32766*h['m_Scale']['y'];offset=old[1]-oldground
  px,pz=placements[k%len(placements)];pos=np.array([px,ground(px,pz)+offset,pz])-parent
  t['m_LocalPosition']=dict(zip('xyz',map(float,pos)));sf.objects[tid].save_typetree(t)
  d['m_IsActive']=True;o.save_typetree(d)
  for c in d['m_Component']:
   ob=sf.objects[c['component']['m_PathID']]
   if ob.type.name=='MeshRenderer':
    rd=ob.read_typetree();rd['m_LightmapIndex']=65535;ob.save_typetree(rd)
 # New terrain must not receive old baked island shadows.
 for o in sf.objects.values():
  if o.type.name=='Terrain':
   d=o.read_typetree();d['m_LightmapIndex']=65535;d['m_HeightmapPixelError']=3.;o.save_typetree(d)
 (O/name).write_bytes(sf.save())
old=UnityPy.load(str(BASE/'sharedassets1.assets')).file;check=UnityPy.load(str(O/'sharedassets1.assets')).file
assert old.objects.keys()==check.objects.keys() and len(old.types)==len(check.types)
for i,o in old.objects.items():
 if o.type.name=='Shader':assert o.get_raw_data()==check.objects[i].get_raw_data()
for px,pz in [(0,0),(-4.5,-9),(4.5,9),(0,-12),(0,12)]:assert abs(ground(px,pz))<.001
report={'version':'Caioba-praia-v12','changed_height_fraction':float(np.mean(values.ravel()!=np.array(old.objects[67].read_typetree()['m_Heightmap']['m_Heights']))),'runtime_tested':False,'files':[]}
for name in ['level1','level2','sharedassets1.assets']:
 p=O/name;report['files'].append({'name':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'before_sha256':hashlib.sha256((BASE/name).read_bytes()).hexdigest()})
(O/'manifest.json').write_text(json.dumps(report,indent=2));np.savez(O/'terrain-preview-data.npz',height=H,x=x,z=z,palms=placements)
print(json.dumps(report,indent=2))
