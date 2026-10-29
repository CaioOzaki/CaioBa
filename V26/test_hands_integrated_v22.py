"""Actual integrated v22 DLL: grip visibility, synchronized poses and end/NewRally/serve event wiring.
ASLR at two bases; deterministic API stubs plus hierarchical skeletons, no live files mutated.
"""
from pathlib import Path
import json,hashlib,struct,math
REAL_FILE=Path(__file__);R=REAL_FILE.parent
__file__=str(R/'test_serve_feedback_v21.py')
exec(Path(__file__).read_text().split('\ncases=[]')[0])
PATHS=['Hand Root L/Open/Cloudcourt Open Glove','Hand Root L/Closed/Cloudcourt Closed Glove','Hand Root R/Open/Cloudcourt Open Glove','Hand Root R/Closed/Cloudcourt Closed Glove','Hand Root L/CC_ThumbsUp','Hand Root R/CC_ThumbsUp','Hand Root L/CC_SettingOpen','Hand Root R/CC_SettingOpen']
COLORS=[(1.,.85,.74,1.),(.91,.69,.49,1.),(.76,.49,.29,1.),(.58,.32,.17,1.),(.36,.18,.10,1.),(.19,.085,.05,1.)]
def qmul(a,b):
 x,y,z,w=a;X,Y,Z,W=b;return(w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z)
def inv(q):return(-q[0],-q[1],-q[2],q[3])
def rot(q,v):return qmul(qmul(q,(*v,0)),inv(q))[:3]
class IntegratedHandsV22(ServeFeedbackEngine):
 def __init__(self,base):
  self.children={};self.renderers={};self.materials={};self.colors={};self.localrot={};self.boneparents={};self.offsets={};self.scales={};self.finds=0;self.materialreads=0;self.activewrites=0;self.atlaswrites=[];self.solvercalls=0
  super().__init__(base)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX)]
  if r==ex['bot_ik_trampoline']:
   self.solvercalls+=1
   # This is the exact post-hook boundary: previous cosmetic hand scaling
   # must be restored before the native IK receives the skeleton.
   if hasattr(self,'bones'):assert self.scales[self.bones[2]]==(1.,1.,1.)
   self.ret()
  elif r==0xb73890 and (a,self.text.get(b)) in self.children:self.finds+=1;self.ret(self.children[a,self.text[b]])
  elif r==0x94f410 and a in self.renderers:self.ret(self.renderers[a])
  elif r in (0xa1ae90,0xa1af10) and a in self.materials:self.materialreads+=1;self.ret(self.materials[a])
  elif r==0xa1b0e0:self.atlaswrites.append((a,b));self.ret()
  elif r==0x956610:self.colors[a]=struct.unpack('<4f',u.mem_read(b,16));self.ret()
  elif r==0x94f700 and a in self.renderers:self.activewrites+=1;self.visible[a]=bool(b);self.ret()
  elif r in (0xb74b50,0xb74fd0) and b in self.localrot:self.u.mem_write(a,struct.pack('<4f',*(self.localrot[b] if r==0xb74b50 else self.worldq(b))));self.ret(a)
  elif r in (0xb754c0,0xb75750) and a in self.localrot:
   q=struct.unpack('<4f',u.mem_read(b,16));p=self.boneparents.get(a);self.localrot[a]=q if r==0xb754c0 or p is None else qmul(inv(self.worldq(p)),q);self.ret()
  elif r==0xb74bf0 and b in self.scales:self.vec(a,self.scales[b]);self.ret(a)
  elif r==0xb75560 and a in self.scales:self.scales[a]=self.vec(b);self.ret()
  elif r==0xb74de0 and b in self.offsets:self.vec(a,self.bonepos(b));self.ret(a)
  else:super().hook(u,addr,size,user)
 def worldq(self,t):
  p=self.boneparents.get(t);return self.localrot[t] if p is None else qmul(self.worldq(p),self.localrot[t])
 def bonepos(self,t):
  p=self.boneparents.get(t)
  if p is None:return self.offsets[t]
  v=rot(self.worldq(p),self.offsets[t]);return tuple(a+b for a,b in zip(self.bonepos(p),v))
 def body_visuals(self,player):
  body=self.alloc(0x200);t=self.alloc();self.transforms[body]=t;self.ptr(body+0x168,player);visuals=[];mats=[]
  for path in PATHS:
   v=self.alloc();renderer=self.alloc();mat=self.alloc();self.children[t,path]=v;self.renderers[v]=renderer;self.materials[renderer]=mat;visuals.append(v);mats.append(mat)
  return body,visuals,mats
 def verify(self,v,m,tone,pose):
  expected=[pose not in (1,3,4),pose not in (1,3,4),pose not in (2,3,4),pose not in (2,3,4),pose in (1,3),pose in (2,3),pose==4,pose==4]
  assert [self.visible[x] for x in v]==expected,(pose,self.visible)
  assert all(all(abs(a-b)<1e-5 for a,b in zip(self.colors[x],COLORS[tone])) for x in m)
 def bot_rig(self,bot):
  bt=self.transforms[bot];self.pos[bt]=(0,0,0);ik=self.alloc();look=self.alloc();reach=self.alloc();refs=self.alloc();self.ptr(bot+0xb8,reach);self.ptr(reach+0x28,ik);self.ptr(reach+0x38,look);self.ptr(ik+0x38,refs)
  self.transforms[ik]=self.alloc();visual=self.alloc();self.children[bt,'CC_WinThumb']=visual;self.renderers[visual]=self.alloc();self.localrot[visual]=(0.,0.,0.,1.)
  mesh=self.alloc();self.children[self.transforms[ik],'Base_mesh']=mesh;renderer=self.alloc();self.renderers[mesh]=renderer;self.materials[renderer]=self.alloc()
  self.bones=[self.alloc() for _ in range(3)];self.boneparents[self.bones[1]]=self.bones[0];self.boneparents[self.bones[2]]=self.bones[1]
  for i,t in enumerate(self.bones):
   self.localrot[t]=(0.,0.,0.,1.);self.scales[t]=(1.,1.,1.);self.offsets[t]=(-.28,1.13,0) if i==0 else ((-.262721,0,0) if i==1 else (-.245490,0,0));self.ptr(refs+0x68+i*8,t)
  self.ptr(self.player+0x80,self.body);torso=self.alloc();self.ptr(self.body+0x38,torso);self.pos[torso]=(2,1,0)
  return ik,look,visual

def run():
 cases=[]
 for base in (0x180000000,0x190000000):
  for fmt in (2,4):
   for online in (False,True):
    e=IntegratedHandsV22(base);e.online_mode(online);e.flag('online_format',fmt);e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4)
    # Actual main client_end -> NewRally -> delayed server placement wiring.
    bot=e.members[0][2];ik,look,thumb=e.bot_rig(bot);original=bytes(e.u.mem_read(bot,0xc0))
    e.call('client_end_hook',e.game,0,e.pv);e.call('bot_body_hook',bot);assert not e.visible.get(thumb,False)
    e.call('bot_ik_hook',ik);assert e.visible[thumb] and all(abs(a-b)<1e-5 for a,b in zip(e.pos[thumb],e.bonepos(e.bones[2]))),(e.visible.get(thumb),e.pos.get(thumb),e.bonepos(e.bones[2]))
    assert len(e.atlaswrites)==1 and e.scales[e.bones[2]][0]<.01
    e.call('net_new_rally_hook',e.game,0);e.now+=12
    finds=e.finds;writes=e.activewrites;reads=e.materialreads
    for _ in range(5):e.call('bot_body_hook',bot);e.call('bot_ik_hook',ik);e.call('bot_ik_hook',look)
    assert e.visible[thumb] and (e.finds,e.activewrites,e.materialreads)==(finds,writes,reads),'NewRally/delay or frame work regressed'
    assert bytes(e.u.mem_read(bot,0xc0))==original,'cosmetic gesture changed Bot fields'
    e.motion();assert e.whistle_plays==1 and not e.visible[thumb]
    assert e.scales[e.bones[2]]==(1.,1.,1.) and all(abs(e.localrot[t][3]-1)<1e-5 for t in e.bones)
    e.motion();assert e.whistle_plays==1
    # Native main hand helper receives actual GetGrip input and synchronized
    # game touch state. Exactly eligible second touch opens both meshes.
    body,v,m=e.body_visuals(e.player)
    if online:e.call('net_new_rally_hook',e.game,1);e.receive(1);e.receive(0)
    e.used(0,1);assert e.call('setting_ready',body)==1
    for grips,pose in [([1,1],4),([1,0],1),([0,1],2),([0,0],0)]:
     e.grips=grips;e.call('avatar_hands_v21',body);e.verify(v,m,0,pose)
    if online:e.receive(0)
    e.used(0,2);e.grips=[1,1];e.call('avatar_hands_v21',body);e.verify(v,m,0,3)
    counts=(e.finds,e.materialreads,e.activewrites)
    for _ in range(5):e.call('avatar_hands_v21',body)
    assert (e.finds,e.materialreads,e.activewrites)==counts
    remote=e.members[1][0];rb,rv,rm=e.body_visuals(remote)
    for pose in (range(5) if online else []):
     for tone in range(6):
      e.call('client_choose_hook',remote,0x5c210000|1|(tone<<10)|(pose<<13));e.call('avatar_hands_v21',rb);e.verify(rv,rm,tone,pose)
    cases.append([hex(base),fmt,online]);print('passed',hex(base),fmt,online,flush=True)
 report=dict(passed=True,actual_integrated_dll=True,sha256=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest(),cases=cases,checks=['two ASLR bases','2v2/4v4 offline+online','Client_EndRally through bot_body through post-IK arm','NewRally and 12-second delay preserve connected gesture','serve placement/whistle clears once and restores skeletal pose/scale','original Bot fields byte-identical','no warm-frame Find/material/SetActive','main local both-GRAB eligible 2nd touch open mesh; release and 3rd touch restore thumb','remote RPC poses 0..4 and all six tones'],scope='Actual main native DLL with hierarchical Unity/Photon API stubs; no headset or live two-PC claim.')
 (R/'analysis/v22-hands-integrated-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':run()
