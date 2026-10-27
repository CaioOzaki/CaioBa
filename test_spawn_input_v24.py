"""Actual Hand.Update attachment: GRAB never requests a serve/practice spawn."""
from pathlib import Path
import hashlib,json
__file__=str(Path(__file__).with_name('test_lobby_v18.py'))
exec(Path(__file__).read_text().split('\nchecks=[]')[0])

class SpawnInputEngine(LobbyEngine):
 def __init__(self,base):
  super().__init__(base);self.triggers=[False,False];self.grips=[False,False];self.queried=[]
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==0xa2710:
   if b==self.q(self.b+0x1541dc0) and a in (5,6):self.ret(self.controllers[a-5])
   else:
    side=self.controllers.index(c);self.queried.append((side,a))
    if a==4:self.ret(self.triggers[side])
    elif a==1:self.ret(self.grips[side])
    elif a==5:self.ret(f=1. if self.triggers[side] else 0.)
    else:raise AssertionError(a)
  # No synthesized audio is needed in this attachment-only fixture.
  elif r==0x14a920:self.ret(0)
  # Record the existing serve-whistle notification at the Photon boundary;
  # this fixture checks spawn/attachment, not remote whistle delivery.
  elif r==0xe6bb50:
   assert self.text[b]=='Client_ChooseTeam' and c==5
   args=u.reg_read(UC_X86_REG_R9);boxed=self.q(args+0x20)
   assert struct.unpack('<i',u.mem_read(boxed+0x10,4))[0]==0x5c220000
   self.ret()
  else:super().hook(u,addr,size,user)
 def update(self,hand,trigger,grip):
  side=self.u.mem_read(hand+0x24,1)[0]
  self.triggers[side]=trigger;self.grips[side]=grip
  # Original WantsToGrab combines the two buttons; spawn must filter grip.
  self.grab=trigger or grip
  try:self.call('lobby_hand_update_hook',hand)
  except Exception:
   print('spawn fixture failure',hex(self.b),self.val('online_format'),self.online,side,trigger,grip,hex(self.u.reg_read(UC_X86_REG_RIP)-self.b))
   raise
 def waiting(self):
  ball=self.alloc(0x200);renderer=self.alloc();t=self.alloc();klass=self.alloc(0x200)
  self.ptr(ball,klass);self.ptr(klass+0x190,self.b+0x77f660);self.ptr(klass+0x1a0,H+0xfb000)
  self.ptr(ball+0x40,renderer);self.transforms[ball]=t;self.pos[t]=(0,-100,0)
  self.u.mem_write(ball+0x89,b'\1');self.u.mem_write(self.game+0x7a,b'\1')
  routine=self.alloc();closure=self.alloc();self.ptr(routine+0x28,closure);self.ptr(closure+0x10,ball)
  self.call('local_serve_hook',routine)
  return ball,renderer

cases=[]
for base in (0x180000000,0x190000000):
 for fmt in (2,4):
  for online in (False,True):
   for side in (0,1):
    e=SpawnInputEngine(base);e.room=False;e.online=online;e.flag('online_version_ready',int(online))
    e.flag('online_format',fmt);e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4)
    ball,renderer=e.waiting();hand=e.hand(side)
    for _ in range(3):e.update(hand,False,True)
    assert e.q(hand+0x30)==0 and not e.render[renderer] and e.pos[e.transforms[ball]]==(0,-100,0)
    e.update(hand,True,True)
    assert e.q(hand+0x30)==ball and e.q(ball+0xd8)==hand and e.render[renderer]
    assert all(abs(a-b)<1e-5 for a,b in zip(e.pos[e.transforms[ball]],e.pos[e.q(hand+0x18)]))
    e.update(hand,False,False);assert not e.q(hand+0x30)
    cases.append(dict(base=hex(base),mode=fmt,online=online,hand=side,serve=True))
  e=SpawnInputEngine(base);e.flag('online_format',fmt);left=e.hand(0);right=e.hand(1)
  e.update(left,False,True);e.update(right,False,True)
  assert e.spawned==[]
  e.update(left,True,True);ball=e.q(left+0x30);assert ball and e.spawned==[ball]
  for _ in range(3):e.update(right,False,True)
  assert e.q(left+0x30)==ball and not e.q(right+0x30) and e.spawned==[ball]
  e.update(right,True,True)
  assert not e.q(left+0x30) and e.q(right+0x30)==ball and e.spawned==[ball]
  e.update(left,True,True);assert e.q(right+0x30)==ball,'held old trigger must not steal back'
  e.update(left,False,False);e.update(left,True,False)
  assert e.q(left+0x30)==ball and e.spawned==[ball]
  # Remote hands cannot request or recall the local player's practice ball.
  remote=e.alloc();rt=e.alloc();e.transforms[remote]=rt;e.ptr(remote+0x18,rt)
  before=list(e.spawned);e.update(remote,True,True);assert e.spawned==before and not e.q(remote+0x30)
  cases.append(dict(base=hex(base),mode=fmt,online=True,lobby=True))
report=dict(passed=True,sha256=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest(),
 cases=cases,checks=['GRAB-only hidden serve stays hidden','left/right trigger spawns and attaches',
 '2v2/4v4 solo and online serve','lobby GRAB cannot spawn or transfer','single lobby ball recall',
 'fresh-trigger transfer','held previous hand cannot steal','remote hand excluded'],
 scope='Integrated compiled native hooks and original Hand.Update with separate trigger/grip stubs; no headset claim.')
(R/'analysis/v24-spawn-input-tests.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(passed=True,cases=len(cases),sha256=report['sha256'])))
