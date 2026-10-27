"""Exercise the built v26 game DLL; read-only Unicorn hierarchy/peer fixture."""
from pathlib import Path
import hashlib,json,math
import test_bot_target_integrated_v24 as old
R=Path(__file__).resolve().parent

class BotPoseEngineV26(old.BotTargetEngineV24):
 def hook(self,u,addr,size,user):
  r=addr-self.b
  if r==0xafe880:
   self.look_calls+=1;a=u.reg_read(old.UC_X86_REG_RCX);b=u.reg_read(old.UC_X86_REG_RDX);head=self.q(a+0x10);direction=self.vec(b);forward=old.rot(self.worldq(head),(0,0,1))
   cross=(forward[1]*direction[2]-forward[2]*direction[1],forward[2]*direction[0]-forward[0]*direction[2],forward[0]*direction[1]-forward[1]*direction[0])
   q=(*cross,1+sum(x*y for x,y in zip(forward,direction)));length=math.sqrt(sum(x*x for x in q));q=tuple(x/length for x in q) if length>1e-6 else (0,1,0,0)
   world=old.qmul(q,self.worldq(head));parent=self.boneparents.get(head)
   self.localrot[head]=old.qmul(old.inv(self.worldq(parent)),world) if parent else world;self.ret()
  elif r==0x23e790:self.ret(self.generic)
  elif r==0x955630:self.ret(True)
  elif r==0x9550e0:self.ret()
  else:super().hook(u,addr,size,user)
 def rig(self):
  super().rig()
  self.skeleton=self.alloc();self.localrot[self.skeleton]=(0.,0.,0.,1.);self.offsets[self.skeleton]=(0.,0.,0.);self.scales[self.skeleton]=(1.,1.,1.)
  self.children[self.transforms[self.ik],'Root_jnt']=self.skeleton
  self.boneparents[self.bones[0]]=self.skeleton;self.boneparents[self.head]=self.skeleton
 def step(self,target):
  self.call('bot_body_hook',self.bot)
  for solver in (self.ik,self.look):
   self.call('bot_ik_hook',solver)
   body=self.q(target+0x80);p=self.pos[self.q(body+0x30)];ground=self.pos[self.transforms[target]]
   toward=old.unit((ground[0],0,ground[2]));f=old.rot(self.worldq(self.skeleton),(0,0,1))
   assert old.near(f,toward),'visible body did not follow recipient'
   head=old.rot(self.worldq(self.head),(0,0,1));horizontal=math.hypot(head[0],head[2])
   assert abs(head[1])<=horizontal*math.tan(math.radians(35))+1e-5
   assert sum(x*y for x,y in zip(head,toward))>=horizontal*.5-1e-5
   assert old.rot(self.worldq(self.head),(0,1,0))[1]>=math.cos(math.radians(35))-1e-4,'head retained native ball-look roll'
   delta=old.unit(tuple(x-y for x,y in zip(p,self.bonepos(self.head))))
   if abs(delta[1])<math.sin(math.radians(34)) and sum(x*y for x,y in zip(delta,toward))>math.hypot(delta[0],delta[2])*.51:
    assert old.near(head,delta),'head looked at different human'
   assert old.near(old.rot(self.worldq(self.thumb),(0,0,1)),toward)
   assert old.near(self.pos[self.thumb],self.bonepos(self.bones[2])) and self.visible[self.thumb]

def run():
 start=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest();cases=[]
 for base in (0x180000000,0x190000000):
  peers=[BotPoseEngineV26(base),BotPoseEngineV26(base)]
  for e in peers:e.online_mode(True);e.rig()
  for fmt in (2,4):
   for e in peers:
    e.flag('online_format',fmt);e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4);e.roster(e.humans);e.call('net_new_rally_hook',e.game,0)
    e.humanpos(e.humans[2],(0,1.6,-4))
   peers[1].roster(peers[1].humans[::-1]);host=peers[0];wire=host.packed(700004)
   for e in peers:
    original=bytes(e.u.mem_read(e.bot,0xc0));e.end(wire);e.step(e.humans[2])
    e.humanpos(e.humans[2],(-3,1.7,-4));e.call('net_new_rally_hook',e.game,0);e.now+=12;e.step(e.humans[2])
    body=e.q(e.humans[2]+0x80);e.pos[e.q(body+0x30)]=(50,100,100);e.step(e.humans[2])
    assert bytes(e.u.mem_read(e.bot,0xc0))==original,'gesture changed Bot gameplay fields'
    e.motion();assert not e.visible[e.thumb] and e.scales[e.bones[2]]==(1.,1.,1.)
    assert old.near(e.localrot[e.skeleton],(0,0,0,1)) and old.near(e.localrot[e.head],(0,1,0,0))
    e.call('bot_ik_hook',e.look);assert not e.visible[e.thumb]
    # Reuse the same gameplay bot with a newly allocated visual rig, as when
    # a new match creates fresh visual components. Reset must rebind it.
    previous=e.skeleton;e.rig();assert e.skeleton!=previous;e.end(wire);e.step(e.humans[2]);e.motion()
   assert peers[1].random_calls==0
   cases.append([hex(base),fmt,'two peers; behind/moving/tracked head; whistle; replacement rig'])
 assert hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest()==start
 result=dict(passed=True,actual_integrated_dll=True,dll_unchanged_during_test=True,sha256=start,cases=cases,scope='Built main x64 DLL through Unicorn hierarchical Unity/Photon stubs; no live VR/two-PC claim')
 (R/'analysis/v26-bot-pose-integrated-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
