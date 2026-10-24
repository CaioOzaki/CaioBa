"""New rounded glove geometry, bound to the game's existing hand skeleton."""
import numpy as np
from repair_hair_v16 import repaired_model

def glove(template,side):
 Model=type(repaired_model());m=Model()
 bones=[]
 for b in template['m_BindPose']:
  matrix=np.array([[b[f'e{r}{c}'] for c in range(4)] for r in range(4)])
  bones.append(np.linalg.inv(matrix)[:3,3])
 m.softbox((0,.002,.062),(.026,.047,.064),0,0)
 m.softbox((0,0,.008),(.028,.051,.019),0,1)
 m.softbox((0,0,.018),(.0285,.052,.007),0,2 if side==0 else 3)
 chains=[[1,9,7],[2,5,6],[3,4,8],[10,11,12],[14,13,15]]
 for finger,chain in enumerate(chains):
  for joint,index in enumerate(chain):
   a=bones[index];b=bones[chain[joint+1]] if joint<2 else a+(a-bones[chain[joint-1]])*.70
   width=(.014 if finger==4 else .0125 if finger<3 else .0105)*(1-joint*.10)
   start=len(m.v);m.limb(a,b,width,width,index,0)
   for k in range(start,len(m.v)):
    p=m.v[k];m.uv[k]=(.25+p[1]*1.8,.65+p[2]*.45)
 # Palm uses a broad area of the ivory fabric; wrist gets team accents.
 for k in range((24+1)*(16+1)):
  p=m.v[k];m.uv[k]=(.25+p[1]*1.8,.65+p[2]*.45)
 # Correct constant atlas samples for the navy cuff and colored wrist band.
 start=(24+1)*(16+1)
 for k in range(start,start*2):m.uv[k]=(.75,.75)
 for k in range(start*2,start*3):m.uv[k]=(.25,.25) if side==0 else (.75,.25)
 return m.serialize(template,'Volley Riot rounded glove '+str(side))
