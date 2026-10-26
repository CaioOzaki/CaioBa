"""Actual v21 bot celebration target list, decorative aim and lifecycle."""
from pathlib import Path
import hashlib,json,math,struct
__file__=str(Path(__file__).with_name('test_cloudcourt_v16.py'))
exec(Path(__file__).read_text().split('\nchecks=[]')[0])
class BotGestureEngine(CloudEngine):
 def __init__(self,base):
  self.now=20.;self.lookups=0;self.transforms_read=0;self.positions_read=0;self.clocks=0;self.thumbs={};self.rotations={}
  super().__init__(base)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX)]
  if r==0xb72b40:self.clocks+=1;self.ret(f=self.now)
  elif r==0xb73890 and self.text.get(b)=='CC_WinThumb':self.lookups+=1;self.ret(self.thumbs.get(a,0))
  elif r==0x94b620:self.transforms_read+=1;super().hook(u,addr,size,user)
  elif r==0xb74de0:self.positions_read+=1;super().hook(u,addr,size,user)
  elif r==0xb75750:self.rotations[a]=struct.unpack('<4f',u.mem_read(b,16));self.ret()
  else:super().hook(u,addr,size,user)
 def baseline(self):return self.lookups,self.transforms_read,self.positions_read,self.clocks
 def torso(self,player,p):
  body=self.q(player+0x80)
  if not body:body=self.alloc();self.ptr(player+0x80,body)
  torso=self.alloc();self.ptr(body+0x38,torso);self.pos[torso]=p

cases=[]
for base in (0x180000000,0x190000000):
 for online in (False,True):
  e=BotGestureEngine(base);e.online=online;e.flag('online_version_ready',online);e.flag('doubles_enabled',1);e.u.mem_write(e.game+0x78,b'\0')
  bot=e.members[0][2];loser=e.members[1][2];bt=e.transforms[bot];e.pos[bt]=(0.,0.,0.)
  thumb=e.alloc();e.thumbs[bt]=thumb
  lst=e.q(e.teams[0]+0x38);arr=e.q(lst+0x10);near=e.alloc();e.integer(near+0x28,0)
  e.ptr(arr+0x20,e.player);e.ptr(arr+0x28,near);e.integer(lst+0x18,2)
  e.torso(e.player,(4.,1.,0.));e.torso(near,(-2.,1.,0.))
  # A closer opponent in the wrong team must never become the target.
  opponent=e.members[1][0];e.torso(opponent,(.1,1.,0.));e.ptr(arr+0x30,opponent);e.integer(lst+0x18,3)
  before=e.baseline();e.call('celebration_bot_v21',bot);assert e.baseline()==before
  e.call('celebration_point_v21',e.game,0);e.call('celebration_bot_v21',bot)
  assert e.visible[thumb] and all(abs(a-b)<1e-5 for a,b in zip(e.pos[thumb],(-.45,1.35,0.))),e.pos
  assert abs(sum(q*q for q in e.rotations[thumb])-1)<1e-5
  before=e.baseline();e.call('celebration_bot_v21',loser);assert e.baseline()==before
  assert e.lookups==1,'visual child must bind only once'
  # If the closer human changes team, the remaining own-team human becomes
  # the target immediately. Opponents in the stale list are ignored.
  e.integer(near+0x28,1);e.call('celebration_bot_v21',bot)
  assert all(abs(a-b)<1e-5 for a,b in zip(e.pos[thumb],(.45,1.35,0.)))
  e.now=23.;e.call('celebration_bot_v21',bot);assert not e.visible[thumb]
  e.now=30.;e.call('celebration_point_v21',e.game,0);e.call('celebration_bot_v21',bot);assert e.visible[thumb]
  e.call('celebration_reset_v21');assert not e.visible[thumb]
  before=e.baseline();e.call('celebration_bot_v21',bot);assert e.baseline()==before,'ordinary play must avoid Transform/Find/position/time work'
  e.call('celebration_point_v21',e.game,0);e.integer(lst+0x18,0);lookups=e.lookups;e.call('celebration_bot_v21',bot)
  assert not e.visible[thumb] and e.lookups==lookups,'no own-team human must show no gesture'
  cases.append([hex(base),online])
report=dict(passed=True,actual_integrated_dll=True,sha256=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest(),cases=cases,checks=['nearest same-team human selected','closer opponent ignored','losing bot no gesture/search','team changes retarget visual only','visual cached once','timer expiry hides','NewRally reset hides','no own-team human no gesture','ordinary baseline no Transform/Find/position/time calls'],scope='Actual integrated native DLL with engine stubs; no live headset/two-PC claim.')
(R/'analysis/v21-bot-celebration-integrated-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
