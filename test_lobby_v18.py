"""Run compiled lobby hooks with actual Hand.Update attachment/release logic."""
from pathlib import Path
__file__=str(Path(__file__).with_name('test_cloudcourt_v16.py'))
exec(Path(__file__).read_text().split('\nchecks=[]')[0])
class LobbyEngine(CloudEngine):
 def __init__(self,base):
  super().__init__(base);self.online=True;self.flag('online_version_ready',1);self.room=True;self.active=True;self.time=10;self.owned=set();self.spawned=[];self.destroyed=[];self.rb_velocity={};self.rb_writes={}
  self.ballklass=self.alloc(0x200);self.ballstat=self.alloc();self.ptr(base+0x15426f0,self.ballklass);self.ptr(self.ballklass+0xb8,self.ballstat);self.ptr(self.ballstat,self.ball)
  self.call('lobby_enter_hook',self.page)
  self.bodyt=self.alloc();self.transforms[self.body]=self.bodyt
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r in (ex['lobby_enter_trampoline'],ex['lobby_start_trampoline']):self.ret()
  elif r==0x9478e0:self.ret(self.active)
  elif r==0x61efc0:self.ret(self.room)
  elif r==0xb72b40:self.ret(f=self.time)
  elif r==0xef3370:self.ret(False)
  elif r==ex['late_trampoline']:self.ret()
  elif r==0xec5940:self.ret(False)
  elif r in (0xec5870,0xec5b90):self.vec(a,(0,0,15) if r==0xec5870 else self.rb_velocity[b]);self.ret(a)
  elif r==0xec60d0:self.rb_velocity[a]=self.vec(b);self.rb_writes[a]=self.rb_writes.get(a,0)+1;self.ret()
  elif r==0xe6e000:self.ret(a in self.owned)
  elif r==0x956d70:
   vals=[struct.unpack('<f',struct.pack('<I',u.reg_read(reg)&0xffffffff))[0] for reg in (UC_X86_REG_XMM0,UC_X86_REG_XMM1,UC_X86_REG_XMM2)];self.ret(f=max(vals[1],min(vals[2],vals[0])))
  elif r==ex['lobby_ball_awake_trampoline']:
   self.ptr(self.ballstat,a);self.ret()
  elif r==0x60fb50:
   assert self.text[a]=='Volleyball';self.spawn_at=self.vec(b);ball=self.alloc(0x200);view=self.alloc();t=self.alloc();self.ptr(ball+0xc8,view);self.owned.add(view);self.transforms[ball]=t;self.pos[t]=self.spawn_at
   self.spawned.append(ball);self.ptr(ball,self.klass);self.ptr(self.klass+0x190,self.b+0x77f660);self.ptr(self.klass+0x1a0,H+0xfb000)
   # Unity calls Awake synchronously inside Instantiate, then returns GameObject.
   self.spawn_sp=u.reg_read(UC_X86_REG_RSP);sp=self.spawn_sp-0x60;u.reg_write(UC_X86_REG_RSP,sp);self.ptr(sp,H+0xf8000);u.reg_write(UC_X86_REG_RCX,ball);u.reg_write(UC_X86_REG_RDX,0);u.reg_write(UC_X86_REG_RIP,self.b+ex['lobby_ball_awake_hook'])
  elif addr==H+0xf8000:u.reg_write(UC_X86_REG_RSP,self.spawn_sp);self.ret(self.spawned[-1])
  elif r==0x94f410:assert self.text[b]=='Volleyball';self.ret(a)
  elif r==0x60cb40:self.destroyed.append(a);self.ret()
  else:super().hook(u,addr,size,user)
 def hand(self,right):
  h=self.alloc();t=self.alloc();self.ptr(h+0x18,t);self.transforms[h]=t;self.local_hands.add(t);self.pos[t]=((-1 if not right else 1),1.4,-4);self.u.mem_write(h+0x24,bytes([right]));return h
checks=[]
for base in (0x180000000,0x190000000):
 for fmt in (2,4):
  e=LobbyEngine(base);e.flag('online_format',fmt);assert e.call('lobby_move_enabled_hook')==1
  t=e.transforms[e.player];e.pos[t]=(0,0,4);e.call('clamp_player_hook',e.player);assert e.pos[t]==(0,0,4)
  pv=e.alloc();e.vec(pv,(20,0,-40));e.call('lobby_move_position_hook',t,pv);assert e.pos[t]==(10,0,-15)
  # An unrelated remote hand can never spawn a local ball.
  remote=e.alloc();rt=e.alloc();e.transforms[remote]=rt;e.ptr(remote+0x18,rt);before=len(e.spawned);assert e.call('hand_find_hook',remote)==0 and len(e.spawned)==before
  for right in (0,1):
   hand=e.hand(right);e.time+=1;ball=e.call('hand_find_hook',hand);assert ball==e.spawned[-1];assert all(abs(a-b)<1e-5 for a,b in zip(e.pos[e.transforms[ball]],e.pos[e.q(hand+0x18)]));assert e.q(e.ballstat)==e.ball
   # Exercise the original Hand.Update/StartInteraction, which uses this hook.
   e.time+=1;e.grab=True;ex['hand_update_native']=0x312f60;e.call('hand_update_native',hand);held=e.q(hand+0x30);assert held and e.q(held+0xd8)==hand
   e.grab=False;e.call('hand_update_native',hand);assert e.q(hand+0x30)==0
  # Every live practice ball gets its own 30Hz spin accumulator. Updating two
  # balls must not let the last-touched one steal the other's physics cadence.
  rbs=[]
  for ball in e.spawned[-2:]:
   rb=e.alloc();e.ptr(ball+0x98,rb);e.ptr(ball+0x30,rb);e.rb_velocity[rb]=(10,0,0);e.u.mem_write(ball+0xd0,b'\0');rbs.append(rb)
  for _ in range(6):
   for ball in e.spawned[-2:]:e.call('late_hook',ball)
  assert all(e.rb_writes[rb]==3 and e.rb_velocity[rb][1]>0 for rb in rbs)
  for _ in range(8):e.time+=1;e.call('hand_find_hook',hand)
  assert len(e.spawned)-len(e.destroyed)==4,(e.spawned,e.destroyed)
  before=len(e.spawned);assert e.call('hand_find_hook',hand)==0 and len(e.spawned)==before
  e.call('lobby_start_hook',e.page);assert len(e.destroyed)==len(e.spawned);assert e.call('lobby_move_enabled_hook')==0
  e.time+=1;assert e.call('hand_find_hook',hand)==0 and len(e.spawned)==before
  # Menu/solo/outside room must not enable practice movement/spawning.
  e.call('lobby_enter_hook',e.page);e.active=False;assert e.call('lobby_move_enabled_hook')==0
  e.active=True;e.room=False;assert e.call('lobby_move_enabled_hook')==0
  # A cached remote object can Awake before the joining client's room UI.
  # Its first active lobby LateUpdate must adopt it and clear the singleton.
  e.room=True;e.active=False;cached=e.alloc(0x200);view=e.alloc();rb=e.alloc();e.ptr(cached+0xc8,view);e.ptr(cached+0x98,rb);e.ptr(cached+0x30,rb);e.rb_velocity[rb]=(10,0,0)
  e.call('lobby_ball_awake_hook',cached);assert e.q(e.ballstat)==cached
  e.active=True;e.call('late_hook',cached);assert e.q(e.ballstat)==0
  assert e.u.mem_read(cached+0x89,1)==b'\1'
  e.call('lobby_start_hook',e.page);assert e.visible[cached] is False
  checks.append((hex(base),fmt))
report={'passed':True,'cases':checks,'checks':['2v2 and 4v4 lobby','cross net movement','bounded map area','own trigger hand','remote hand rejected','native attachment and release','four-ball recycling','spawn cooldown','singleton preserved','cleanup before game','no spawning in match or outside room'],'scope':'Compiled x64 with Unity/Photon stubs; real two-PC headset playtest still required.'}
(R/'analysis/v18-lobby-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
