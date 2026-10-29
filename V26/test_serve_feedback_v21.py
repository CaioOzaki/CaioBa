"""Execute shipped v21 hooks: marker lifetime and one whistle per real spawn.

This uses the actual integrated native DLL, relocated twice. Unity and Photon
are deterministic stubs, including the original native Hand.Update trigger
path. It does not claim physical headset or two-PC validation.
"""
from pathlib import Path
import hashlib
__file__=str(Path(__file__).with_name('test_landing_v20.py'))
exec(Path(__file__).read_text().split('\nchecks=0')[0])

class ServeFeedbackEngine(LandingEngine):
 def __init__(self,base):
  self.now=20.;self.room_active=False;self.server=0;self.whistle_plays=0;self.whistle_clips=0;self.whistle_sources=0;self.sample_uploads=0
  super().__init__(base)
  self.whistle_samples=self.alloc(0x20+6174*4);self.whistle_clip=self.alloc();self.whistle_source=self.alloc()
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c,d=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9)]
  if r==0xb72b40:self.ret(f=self.now)
  elif r==0x14ba70:
   boxed=self.alloc();self.integer(boxed+0x10,struct.unpack('<i',u.mem_read(b,4))[0]);self.ret(boxed)
  elif r==0x253580:self.ret(self.server if self.server and struct.unpack('<i',u.mem_read(self.server+0x28,4))[0]==b else 0)
  elif r==0x14a4f0 and b==6174:self.ret(self.whistle_samples)
  elif r==0xeba090 and b==6174:
   assert self.text[a]=='Cloudcourt_Original_Serve_Whistle' and c==1 and d==22050
   self.whistle_clips+=1;self.ret(self.whistle_clip)
  elif r==0x94f240:self.whistle_sources+=1;self.ret(self.whistle_source)
  elif r==0xeba5f0 and a==self.whistle_clip:
   samples=struct.unpack('<6174f',u.mem_read(b+0x20,6174*4))
   assert all(__import__('math').isfinite(x) and abs(x)<=.681 for x in samples)
   assert samples[0]==0 and max(abs(x) for x in samples[:100])<max(abs(x) for x in samples[220:500])
   assert sum(x*x for x in samples[-220:])<sum(x*x for x in samples[220:440])
   self.sample_uploads+=1;self.ret(True)
  elif r==0xebbe30 and a==self.whistle_source:self.whistle_plays+=1;self.ret()
  elif r in (0xebc370,0xebc500,0xebc460):self.ret()
  elif r in (ex.get('lobby_enter_trampoline',-1),ex.get('lobby_start_trampoline',-1),ex.get('lobby_ball_awake_trampoline',-1)):self.ret()
  elif r==0x9478e0:self.ret(self.room_active)
  elif r==0x61efc0:self.ret(True)
  else:super().hook(u,addr,size,user)
 def marker(self):
  self.vec(self.pv,(1.,.02,-3.));self.call('client_end_hook',self.game,0x4346,self.pv)
  assert [self.marker_active.get(g,False) for g in self.go_markers]==[True,False]
 def marked(self):return any(self.marker_active.values())
 def motion(self,hit=0,touch=-1,team=-1,context=3,p=(0,2.8,-10),v=(0,0,0),ball=None):
  self.vec(self.pv,p);self.vec(self.vv,v);self.call('client_motion_hook',ball or self.ball,self.pv,self.vv,hit,touch&0xffffffffffffffff,team&0xffffffffffffffff,context,0)
 def online_mode(self,enabled=True):self.online=enabled;self.flag('online_version_ready',enabled)
 def human_waiting(self,right=0):
  self.u.mem_write(self.game+0x7a,b'\1');self.u.mem_write(self.ball+0x89,b'\1')
  renderer=self.alloc();self.ptr(self.ball+0x40,renderer)
  routine=self.alloc();closure=self.alloc();self.ptr(routine+0x28,closure);self.ptr(closure+0x10,self.ball)
  self.call('local_serve_hook',routine);assert self.render[renderer] is False
  hand=self.alloc();center=self.alloc();self.ptr(hand+0x18,center);self.transforms[hand]=center;self.pos[center]=(1,1.3,-10)
  self.u.mem_write(hand+0x24,bytes([right]));self.local_hands.add(center)
  if self.online:
   body_t=self.alloc();self.transforms[self.body]=body_t
  klass=self.alloc(0x200);self.ptr(self.ball,klass);self.ptr(klass+0x190,self.b+0x77f660);self.ptr(klass+0x1a0,H+0xfb000)
  return hand,renderer

cases=[]
for base in (0x180000000,0x190000000):
 for fmt in (2,4):
  for online in (False,True):
   e=ServeFeedbackEngine(base);e.online_mode(online);e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4)
   e.marker();e.call('net_new_rally_hook',e.game,0);assert e.marked() and e.whistle_plays==0,'NewRally erased point before serve existed'
   for kwargs in [dict(context=2),dict(hit=1),dict(touch=0),dict(team=0),dict(v=(0,.02,0)),dict(p=(0,-100,0)),dict(p=(0,2.8,20))]:
    e.motion(**kwargs);assert e.marked() and e.whistle_plays==0,'non-serve motion consumed pending feedback'
   e.motion();assert not e.marked() and e.whistle_plays==1
   for _ in range(3):e.motion()
   assert e.whistle_plays==1 and e.whistle_clips==e.sample_uploads==e.whistle_sources==1
   e.marker();e.call('net_new_rally_hook',e.game,0);assert e.marked();e.motion();assert e.whistle_plays==2 and not e.marked()
   assert e.whistle_clips==e.sample_uploads==e.whistle_sources==1,'whistle recreated per serve'
   cases.append((hex(base),fmt,online,'bot_spawn_and_cache'))
   # Native Hand.Update must see trigger input before it can retrieve the
   # waiting ball. No trigger or invalid remote hand can clear the marker.
   e.marker();e.call('net_new_rally_hook',e.game,0);hand,renderer=e.human_waiting()
   ex['hand_update_native']=0x312f60;e.grab=False;e.call('hand_update_native',hand)
   assert e.marked() and e.whistle_plays==2 and not e.render[renderer]
   if online:
    remote=e.alloc();rt=e.alloc();e.transforms[remote]=rt;self_player=e.player;e.ptr(remote+0x18,rt);e.pos[rt]=(9,1,9)
    assert e.call('hand_find_hook',remote)==0 and e.marked()
   e.grab=True;e.call('hand_update_native',hand)
   assert not e.marked() and e.whistle_plays==3 and e.render[renderer] and e.q(hand+0x30)==e.ball
   if online:assert e.selected[-1]==0x5c220000, (e.selected,hex(base),fmt,online)
   e.call('hand_update_native',hand);assert e.whistle_plays==3
   cases.append((hex(base),fmt,online,'human_native_trigger'))
 # Separate client instances consume the same original reliable bot placement
 # or authorized human event. An opponent or non-serving teammate cannot clear.
 clients=[ServeFeedbackEngine(base),ServeFeedbackEngine(base)]
 for e in clients:
  e.online_mode();e.integer(e.game+0x7c,0);e.server=e.player
  e.marker();e.call('net_new_rally_hook',e.game,0)
  wrong=e.members[1][0];e.call('client_choose_hook',wrong,0x5c220000);assert e.marked() and not e.whistle_plays
  teammate=e.members[0][0];e.call('client_choose_hook',teammate,0x5c220000);assert e.marked() and not e.whistle_plays
  # Original Client_NewRally discards its servingTeam argument. On a non-host
  # rules.currentTeam can remain from an older point; it must not reject the
  # actual current serving player resolved by the synchronized player roles.
  e.integer(e.game+0x7c,1)
  e.call('lobby_enter_hook',e.page);e.room_active=True
  e.call('client_choose_hook',e.player,0x5c220000);assert e.marked() and not e.whistle_plays
  e.room_active=False;e.call('client_choose_hook',e.player,0x5c220000);assert not e.marked() and e.whistle_plays==1
  e.call('client_choose_hook',e.player,0x5c220000);assert e.whistle_plays==1
 cases.append((hex(base),'two isolated clients','server event accepted despite stale currentTeam; wrong player and lobby rejected'))
 # Practice balls never consume the match marker/whistle.
 e=ServeFeedbackEngine(base);e.online_mode();e.marker();e.call('net_new_rally_hook',e.game,0)
 e.call('lobby_enter_hook',e.page);e.room_active=True;e.call('lobby_ball_awake_hook',e.ball)
 e.motion();assert e.marked() and not e.whistle_plays
 cases.append((hex(base),'lobby ball excluded'))

report=dict(passed=True,cases=cases,bases=2,actual_integrated_dll=True,sha256=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest(),checks=['marker persists during NewRally','only exact bot placement clears','native trigger required for human serve','whistle once per serve','audio source/clip cached','wrong player/team/lobby rejected','same human event on isolated clients','practice balls excluded'],scope='Actual integrated native DLL with deterministic Unity/Photon stubs. No Quest or real two-PC claim.')
(R/'analysis/v21-serve-feedback-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
