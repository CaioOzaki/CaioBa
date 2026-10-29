"""Actual integrated DLL: recipient packet, two peers, head/arm, whistle lifetime.

Each native solver pass deliberately turns the head back to a different ball.
Only the post-solver production hook can satisfy the recipient ray checks.
"""
from pathlib import Path
import hashlib
THIS=Path(__file__);R=THIS.parent
START_DLL_SHA256=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest()
__file__=str(R/'test_hands_integrated_v22.py')
exec(Path(__file__).read_text().split('\ndef run():')[0])

def unit(v):
 n=math.sqrt(sum(x*x for x in v));return tuple(x/n for x in v)
def near(a,b):return max(abs(x-y) for x,y in zip(a,b))<2e-4
class BotTargetEngineV24(IntegratedHandsV22):
 def __init__(self,base):
  self.random_pick=0;self.random_calls=0;self.look_calls=0;self.solver_leaks=0;self.head=0
  super().__init__(base)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX)]
  if r==0xa14da0:self.random_calls+=1;self.ret(self.random_pick%b)
  elif r==ex['tracked_touch_trampoline']:
   # Original pending-human-serve path exits while ballInPlay is false.
   self.ret()
  elif r==0xafe880:
   self.look_calls+=1;head=self.q(a+0x10);direction=self.vec(b);forward=rot(self.worldq(head),(0,0,1))
   weight=struct.unpack('<f',struct.pack('<I',u.reg_read(UC_X86_REG_XMM2)&0xffffffff))[0];assert abs(weight-1)<1e-6
   c=(forward[1]*direction[2]-forward[2]*direction[1],forward[2]*direction[0]-forward[0]*direction[2],forward[0]*direction[1]-forward[1]*direction[0])
   q=(*c,1+sum(x*y for x,y in zip(forward,direction)));length=math.sqrt(sum(x*x for x in q));q=tuple(x/length for x in q) if length>1e-6 else (0,1,0,0)
   self.localrot[head]=qmul(q,self.worldq(head));self.ret()
  elif r==ex['bot_ik_trampoline']:
   if self.head and self.look_calls:assert abs(rot(self.worldq(self.head),(0,0,1))[0])<1e-5,'recipient head leaked into native solver'
   super().hook(u,addr,size,user)
   if self.head:self.localrot[self.head]=(0,1,0,0)
  else:super().hook(u,addr,size,user)
 def rig(self):
  self.bot=self.members[0][2];self.ik,self.look,self.thumb=self.bot_rig(self.bot)
  self.head=self.alloc();solver=self.alloc();bone=self.alloc();self.ptr(self.look+0x38,solver);self.ptr(solver+0x68,bone);self.ptr(bone+0x10,self.head);self.vec(bone+0x60,(0,0,1))
  self.localrot[self.head]=(0,0,0,1);self.offsets[self.head]=(0,1.6,0);self.scales[self.head]=(1,1,1)
  self.humans=[self.player]
  for id in (50003,700004):
   human=self.alloc();body=self.alloc(0x200);torso=self.alloc();t=self.alloc();self.ptr(human+0x80,body);self.ptr(body+0x38,torso);self.transforms[human]=t;self.integer(human+0x28,0);self.ids[human]=id;self.humans.append(human)
  for i,human in enumerate(self.humans):
   self.ptr(self.q(human+0x80)+0x30,self.alloc());self.humanpos(human,((i+1)*2,1.6,(i+1)*1.5))
  self.roster(self.humans)
 def humanpos(self,h,p):
  self.pos[self.transforms[h]]=p;body=self.q(h+0x80);self.pos[self.q(body+0x38)]=p;self.pos[self.q(body+0x30)]=(p[0],p[1]+.2,p[2])
 def roster(self,humans):
  listing=self.q(self.teams[0]+0x38);array=self.q(listing+0x10);self.integer(listing+0x18,len(humans))
  for i,h in enumerate(humans):self.ptr(array+0x20+8*i,h)
 def packed(self,last=None,team=0):
  if last is not None:self.used(team,3,last)
  value=self.alloc();self.integer(value,0);obj=self.call('score_box_hook',self.generic,value);return struct.unpack('<i',self.u.mem_read(obj+0x10,4))[0]
 def end(self,wire):self.call('client_end_hook',self.game,wire,self.pv)
 def step(self,target):
  self.call('bot_body_hook',self.bot)
  for solver in (self.ik,self.look):
   self.call('bot_ik_hook',solver);body=self.q(target+0x80);p=self.pos[self.q(body+0x30)]
   assert near(rot(self.worldq(self.head),(0,0,1)),unit(tuple(x-y for x,y in zip(p,self.bonepos(self.head))))),'head retained ball or wrong player'
   handforward=rot(self.worldq(self.thumb),(0,0,1));assert near(handforward,unit((p[0],0,p[2]))),'hand points at different recipient'
   assert near(self.pos[self.thumb],self.bonepos(self.bones[2])) and self.visible[self.thumb]

def run_v24():
 cases=[];ace_cases=[]
 for base in (0x180000000,0x190000000):
  peers=[BotTargetEngineV24(base),BotTargetEngineV24(base)]
  for e in peers:e.online_mode(True);e.rig()
  for fmt in (2,4):
   for e in peers:
    e.flag('online_format',fmt);e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4);e.roster(e.humans);e.call('net_new_rally_hook',e.game,0)
   peers[1].roster(peers[1].humans[::-1]);host=peers[0];random_before=host.random_calls
   wire=host.packed(700004);assert wire&0xffff==0x4306 and wire>>16&7==3 and host.random_calls==random_before
   for e in peers:e.end(wire);e.step(e.humans[2])
   # Walking closer never retargets; NewRally and score/serve delays preserve.
   for e in peers:
    e.humanpos(e.humans[0],(.1,1.6,.1));e.humanpos(e.humans[2],(-3,1.7,4));e.call('net_new_rally_hook',e.game,0);e.now+=12;e.step(e.humans[2])
    # The tracked head can crouch independently of the torso and ground root.
    body=e.q(e.humans[2]+0x80);head=e.q(body+0x30);p=e.pos[head];e.pos[head]=(p[0],.8,p[2]);e.step(e.humans[2])
   # Actual bot scored: authority chooses one random human, peers consume it.
   host.random_pick=1;wire=host.packed(host.ids[host.bot]);assert host.random_calls==random_before+1 and wire>>16&7==2
   for e in peers:e.end(wire);e.step(e.humans[1])
   assert peers[1].random_calls==0
   # Removing a still-alive player from the synchronized human roster retargets.
   for e in peers:
    e.roster([e.humans[2],e.humans[0]]);e.step(e.humans[0]);e.motion();assert not e.visible[e.thumb] and e.scales[e.bones[2]]==(1,1,1)
    assert near(e.localrot[e.head],(0,1,0,0));e.call('bot_ik_hook',e.look);assert not e.visible[e.thumb]
   cases.append([hex(base),fmt,True])
  # Reuse the host fixture for a real pre-ballInPlay accepted human serve.
  e=host;e.online_mode(False);e.roster(e.humans);e.call('net_new_rally_hook',e.game,0);e.used(0,0,-1);e.u.mem_write(e.game+0x78,b'\0\1');e.u.mem_write(e.game+0x94,b'\1')
  e.humanpos(e.humans[1],(2,1.6,-10));before=e.random_calls
  e.call('tracked_touch_hook',e.game,50003,0)
  assert struct.unpack('<i',e.u.mem_read(e.game+0x98,4))[0]==-1 and struct.unpack('<i',e.u.mem_read(e.game+0x9c,4))[0]==0
  wire=e.packed();assert wire>>16&7==2 and e.random_calls==before;e.end(wire);e.step(e.humans[1])
  # NewRally must remove the old ace when the next point is an opponent fault.
  e.call('net_new_rally_hook',e.game,0);e.used(1,0,-1);e.random_pick=0;wire=e.packed();assert wire>>16&7==1 and e.random_calls==before+1
  ace_cases.append([hex(base),'offline accepted human ace; native attribution untouched; stale cache cleared'])
 assert hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest()==START_DLL_SHA256,'DLL changed during emulator validation'
 result=dict(passed=True,actual_integrated_dll=True,sha256=START_DLL_SHA256,dll_unchanged_during_test=True,cases=cases,ace_cases=ace_cases,peer_instances=4,
   checks=['authoritative actual last hitter wins over receiving human/distance','full Photon id encoded as stable sorted rank across reversed peer rosters','same head and hand recipient after each native solver overwrites head toward ball','independent tracked head crouch versus torso','moving target stable through NewRally and 12-second delay','one host RNG for bot point and no peer RNG','disconnected live Unity object excluded','real serve whistle restores head/arm/scale and hides gesture','accepted pending human serve credits ace without mutating GameRules','next-rally opponent fault cannot reuse old ace'],scope='Actual main x64 DLL executed by Unicorn with hierarchical Unity/Photon API stubs; not live headset or two-PC validation')
 (R/'analysis/v24-bot-target-integrated-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run_v24()
