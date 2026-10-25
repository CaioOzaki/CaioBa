"""Exercise real Bot.Update and scoring coroutines, not Jump-only stubs."""
from pathlib import Path
__file__=str(Path(__file__).with_name('test_cloudcourt_v16.py'))
exec(Path(__file__).read_text().split('\nchecks=[]')[0])
import math
import hashlib
_metadata=json.loads((R/'analysis/script.json').read_text())['ScriptMetadata']
_baseline=R/'versions/cloudcourt-v18-antes-v19/fontes/comfort_v14.c'
def protected_setting_source(path):
 text=path.read_text();return text[text.index('EXPORT V3 setting_arc'):text.index('static void* str')]
_setting=protected_setting_source(R/'comfort_v14.c')
assert _setting==protected_setting_source(_baseline),'setting arc or target source changed from v18'

class GameplayEngine(CloudEngine):
 def __init__(self,base):
  super().__init__(base);self.owner=True;self.dt=1/90;self.jump_calls=0;self.set_ended=[];self.rallies=0
  self.fakeclass=self.alloc(0x200)
  # IL2CPP initializes metadata before these original Unity routines run.
  for item in _metadata:
   address=item.get('Address',0);name=item.get('Name') or ''
   if name.endswith('_TypeInfo') and 0<address<p.OPTIONAL_HEADER.SizeOfImage and not self.q(base+address):self.ptr(base+address,self.fakeclass)
  self.ballklass=self.alloc(0x200);self.ballstat=self.alloc();self.ptr(base+0x15426f0,self.ballklass);self.ptr(self.ballklass+0xb8,self.ballstat);self.ptr(self.ballstat,self.ball)
  self.transforms[self.ball]=self.alloc();self.pos[self.transforms[self.ball]]=(0,4.8,-1.15)
  self.bot=self.members[0][0];self.collider=self.alloc();self.ptr(self.bot+0x78,self.collider)
  self.pos[self.transforms[self.bot]]=(0,0,-1.15);self.vec(self.bot+0xa8,(0,0,-1.15));self.u.mem_write(self.bot+0x70,b'\1')
  self.envklass=self.alloc(0x200);self.envstat=self.alloc();self.environment=self.alloc();self.ptr(base+0x15422a0,self.envklass);self.ptr(self.envklass+0xb8,self.envstat);self.ptr(self.envstat,self.environment)
  self.scores=self.alloc();self.wonsets=self.alloc();self.ptr(self.game+0xa8,self.scores);self.ptr(self.game+0xb0,self.wonsets)
  for a in (self.scores,self.wonsets):self.ptr(a+0x18,2)
  self.routine=self.alloc();self.ptr(self.routine+0x20,self.game);self.integer(self.routine+0x28,0)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==0xe6e000:self.ret(self.owner)
  elif r in (0xb72960,0xb72b10):self.ret(f=self.dt)
  elif r==ex['bot_assess_trampoline']:self.integer(a+0xa4,1);self.ret()
  elif r==ex['bot_jump_trampoline']:
   self.jump_calls+=1;self.u.mem_write(a+0x80,b'\1');self.flt(a+0x84,0);self.vec(a+0x88,self.pos[self.transforms[a]]);self.vec(a+0x94,(0,math.sqrt(19.62),0));self.flt(a+0xa0,2*math.sqrt(19.62)/9.81);self.ret()
  elif r==0xec0c30:
   # Hidden return buffer, Collider, Vector3, MethodInfo.
   q=self.vec(c);pos=self.pos[self.transforms[self.bot]];self.vec(a,(pos[0],min(q[1],pos[1]+2.),pos[2]));self.ret(a)
  elif r==0xb77ef0:self.ret(f=math.dist(self.vec(a),self.vec(b)))
  elif r==0xec52d0:self.vec(a,(0,-9.81,0));self.ret(a)
  elif r==0x1ccf3c:
   f=struct.unpack('<f',struct.pack('<I',u.reg_read(UC_X86_REG_XMM0)&0xffffffff))[0];self.ret(f=math.sqrt(f))
  elif r==0xb7a000:
   f=struct.unpack('<f',struct.pack('<I',u.reg_read(UC_X86_REG_XMM2)&0xffffffff))[0];self.vec(a,[v*f for v in self.vec(b)]);self.ret(a)
  elif r==0xb7a040:
   f=struct.unpack('<f',struct.pack('<I',u.reg_read(UC_X86_REG_XMM1)&0xffffffff))[0];self.vec(a,[v*f for v in self.vec(c)]);self.ret(a)
  elif r==0xb79e30:self.vec(a,[v+w for v,w in zip(self.vec(b),self.vec(c))]);self.ret(a)
  elif r==0x956990:self.ret(abs(a if a<2**31 else a-2**32))
  elif r==0x253460:self.set_ended.append(b);self.ret(self.generic)
  elif r==0x2552c0:self.rallies+=1;self.ret(self.generic)
  elif r in (0x253a60,0xa0a0c0,0x14b040):self.ret()
  elif r==0x1c22e0:self.ret(self.alloc())
  else:super().hook(u,addr,size,user)
 def venue(self,name):self.ptr(self.environment+0x18,self.string(name))
 def settings(self,fmt,online):
  self.flag('doubles_enabled',fmt==2);self.flag('quartet_enabled',fmt==4);self.online=online;self.flag('online_version_ready',online);self.flag('online_format',fmt)
 def team_setup(self,team):
  # The inherited high-five fixture turns team 1 slot 0 into a remote human.
  self.bot=self.members[team][2 if team else 0];self.ptr(self.bot+0x78,self.collider);self.u.mem_write(self.bot+0x70,b'\1');self.side=1 if team else -1
  self.pos[self.transforms[self.bot]]=(0,0,self.side*1.15);self.vec(self.bot+0xa8,(0,0,self.side*1.15))
 def ball_at(self,y,vy):self.pos[self.transforms[self.ball]]=(0,y,self.side*1.15);self.vec(self.ball+0x8c,(0,vy,0))
 def grounded(self):self.u.mem_write(self.bot+0x80,b'\0');self.flt(self.bot+0x84,0);self.pos[self.transforms[self.bot]]=(0,0,self.side*1.15)
 def update(self):return self.call('bot_update_hook',self.bot)
 def score_resume(self,blue,red):
  self.integer(self.routine+0x10,1);self.integer(self.scores+0x20,blue);self.integer(self.scores+0x24,red);self.set_ended=[];self.rallies=0
  ex['original_end_rally_resume']=0x258420;self.call('original_end_rally_resume',self.routine)
  return self.set_ended
 def set_resume(self,blue,red):
  self.integer(self.routine+0x10,1);self.integer(self.wonsets+0x20,blue);self.integer(self.wonsets+0x24,red);self.rallies=0
  ex['original_end_set_resume']=0x258830;self.call('original_end_set_resume',self.routine)
  return self.rallies

checks=[]
for base in (0x180000000,0x190000000):
 for fmt in (2,4):
  for online in (False,True):
   for team in (0,1):
    e=GameplayEngine(base);e.settings(fmt,online);e.team_setup(team);e.venue('Indoor')
    # Real inline Jump branch: no call to the separately hooked Bot.Jump.
    e.used(team,1);e.ball_at(3.5,-2);e.update()
    assert e.u.mem_read(e.bot+0x80,1)==b'\1' and e.jump_calls==0,(hex(base),fmt,online,team)
    vy=e.flt(e.bot+0x98);assert abs(vy*vy/19.62-2)<1e-5
    assert abs(e.flt(e.bot+0xa0)-2*vy/9.81)<1e-5
    # A point-blank assisted set is still rising: wait instead of jumping early.
    e.grounded();e.used(team,2);e.ball_at(3.0,8);e.update();assert e.u.mem_read(e.bot+0x80,1)==b'\0'
    # Descending set: preempt the old distance check, then integrate its real jump.
    e.ball_at(4.8,-4);e.used(team,2,e.ids[e.bot]);e.update();assert e.jump_calls==0 and e.u.mem_read(e.bot+0x80,1)==b'\0'
    e.used(team,2)
    e.ball_at(4.8,-4);e.update();assert e.jump_calls==1 and e.u.mem_read(e.bot+0x80,1)==b'\1'
    assert e.pos[e.transforms[e.bot]][1]>0 and abs(e.flt(e.bot+0x98)**2/19.62-2)<1e-5
    peak=e.pos[e.transforms[e.bot]][1]
    for _ in range(114):e.update();peak=max(peak,e.pos[e.transforms[e.bot]][1])
    assert 1.995<peak<2.005 and e.u.mem_read(e.bot+0x80,1)==b'\0',peak
    # Client does not make independent decisions for an opponent-owned bot.
    e.grounded();e.owner=False;e.ball_at(4.8,-4);before=e.jump_calls;e.update();assert e.jump_calls==before and e.u.mem_read(e.bot+0x80,1)==b'\0'
    for venue,target in (('Indoor',25),('BeachDay',21),('Beach',21)):
     e.venue(venue);assert e.call('points_per_set_hook')==target and e.call('sets_to_win_hook')==2
     for blue,red,end in ((target-1,target-3,False),(target,target-1,False),(target,target-2,True),(target+1,target-1,True)):
      assert bool(e.score_resume(blue,red))==end,(venue,blue,red)
      assert bool(e.score_resume(red,blue))==end,(venue,red,blue)
     assert e.set_resume(1,0)==1 and e.set_resume(0,1)==1
     assert e.set_resume(2,0)==0 and e.set_resume(1,2)==0
    checks.append({'base':hex(base),'format':fmt,'online':online,'team':team})
report={'passed':True,'cases':checks,'checks':['real Bot.Update inline jump reaches 2m','airtime consistent with height','rising set does not trigger early takeoff','descending set receives timed jump','remote bot ownership respected','real EndRally checks 21/25 and two-point lead on both teams','real EndSet ends after 2 wins (best of 3)'],'setting_arc_and_target_changed':False,'setting_source_sha256':hashlib.sha256(_setting.encode()).hexdigest(),'scope':'Original game control flow with deterministic engine stubs; physical Quest 3 and two-PC playtest pending.'}
(R/'analysis/v19-gameplay-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
