"""Exercise compiled spawn/jump, score wire format and two-avatar high fives."""
__file__=__file__.replace('test_celebration_v15.py','test_comfort_v14.py')
exec(open(__file__).read().split('\nchecks=0')[0].replace('count=100000','count=1000000'))
class CelebrationEngine(SettingEngine):
 def __init__(self,base):
  super().__init__(base);self.played=0;self.message='';self.jump_speed=4.429447;self.apex=[]
  self.audio=self.alloc();self.clip=self.alloc();self.generic=self.alloc();self.samples=self.alloc(0x20+4410*4)
  self.remote=self.alloc(0x200);self.ptr(self.remote+0x168,self.members[1][0]);self.ptr(self.members[1][0]+0x80,self.remote)
  nk=self.q(base+0x1542650);ns=self.q(nk+0xb8);lst=self.alloc();arr=self.alloc();self.ptr(ns+8,lst);self.ptr(lst+0x10,arr);self.integer(lst+0x18,2)
  self.ptr(arr+0x20,self.player);self.ptr(arr+0x28,self.members[1][0]);self.ptr(self.player+0x80,self.body)
  self.hands=[]
  for body in [self.body,self.remote]:
   row=[]
   for side in range(2):
    arm=self.alloc();t=self.alloc();self.ptr(body+0x40+8*side,arm);self.ptr(arm+0x10,t);row.append(t)
   self.hands.append(row)
  self.ui=self.alloc();self.ptr(self.game+0x28,self.ui)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==ex['bot_jump_trampoline']:self.flt(a+0x98,self.jump_speed);self.ret()
  elif r==ex['bot_hit_trampoline']:self.apex.append(self.flt(a+0x44));self.ret()
  elif r==0x14ba70:self.boxed=struct.unpack('<i',u.mem_read(b,4))[0];self.ret(self.generic)
  elif r==0x2533a0:self.ret()
  elif r==0x2405f0:self.message=self.text[b];self.ret()
  elif r==0xa0bfb0:self.ret(a!=0)
  elif r in (0xb72960,0xb72b10):self.ret(f=1/60)
  elif r==0xb72b40:self.ret(f=10)
  elif r in (0x7911d0,0x2402d0,0x240340):self.ret()
  elif r==0x14b030:self.ret(0) # Optional stripped AudioSource setter unavailable in this stub.
  elif r in (0x14a920,0x14a910,0x14a530,0x14a5a0,0x14b9c0,0x14a710,0x14acb0):self.ret(self.generic)
  elif r==0x14a4f0:assert b==4410;self.ret(self.samples)
  elif r==0x94f240:self.ret(self.audio)
  elif r==0xeba090:assert b==4410 and c==1;self.ret(self.clip)
  elif r==0xeba5f0:
   data=struct.unpack('<4410f',u.mem_read(b+0x20,4410*4));assert max(abs(x) for x in data)<1 and sum(x*x for x in data[:400])>100*sum(x*x for x in data[-400:]);self.ret(1)
  elif r in (0xebc590,0xebc760,0xebc2d0):self.ret()
  elif r==0xebbe30:self.played+=1;self.ret()
  else:super().hook(u,addr,size,user)
 def tracked_hands(self,d):
  for side in (0,1):self.pos[self.hands[0][side]]=(side*2,1,-d);self.pos[self.hands[1][side]]=(side*2,1,0)

for base in (0x180000000,0x190000000):
 e=CelebrationEngine(base)
 for fmt in (2,4):
  e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4)
  for team in (0,1):
   e.used(team,0);server=e.members[team][2];e.ptr(server+0x20,e.areas[team][2]);t=e.transforms[server];e.pos[t]=(2,0,-8 if team==0 else 8)
   out=e.alloc();e.call('bot_serve_position_hook',out,e.transforms[e.areas[team][2]],0);spawn_position=e.vec(out);assert abs(spawn_position[1]-2.8)<1e-5 and spawn_position[0]==2 and spawn_position[2]==e.pos[t][2]
   e.u.mem_write(e.game+0x78,b'\1\1');e.call('bot_body_hook',server);assert e.calls[-1][1]==0 and e.flt(server+0x3c)==2
   e.call('bot_hit_hook',server,e.ball);assert abs(e.apex[-1]-2.65)<1e-5 and e.flt(server+0x44)==2
   e.call('bot_jump_hook',server);v=e.flt(server+0x98);assert abs((v*v-e.jump_speed**2)/19.62-.7)<1e-5;assert abs(e.flt(server+0xa0)-2*v/9.81)<1e-5
 value=e.alloc();e.integer(value,1)
 e.call('four_point_hook',e.game,1);e.call('score_box_hook',e.generic,value);assert e.boxed==0x4303
 e.call('client_end_hook',e.game,e.boxed,e.pv);assert 'RED +1' in e.message and 'Four touches by blue team' in e.message and '<size=42%>' in e.message
 e.call('double_point_hook',e.game,0);e.integer(value,0);e.call('score_box_hook',e.generic,value);e.call('client_end_hook',e.game,e.boxed,e.pv);assert 'Double touch' in e.message
 e.online=True;e.flag('online_version_ready',1)
 e.tracked_hands(.5);e.call('high_five_update',e.body);assert e.played==0
 e.tracked_hands(.08);e.call('high_five_update',e.body);assert e.played==1
 assert e.pos[e.hands[0][0]]==e.pos[e.hands[1][0]]
 for _ in range(12):e.tracked_hands(.08);e.call('high_five_update',e.body)
 assert e.played==1
 e.call('net_new_rally_hook',e.game,0)
 for _ in range(60):e.tracked_hands(.5);e.call('high_five_update',e.body)
 for d in (.5,.08):e.tracked_hands(d);e.call('high_five_update',e.body)
 assert e.played==2
 e.call('client_end_hook',e.game,0,e.pv)
 for _ in range(60):e.tracked_hands(.5);e.call('high_five_update',e.body)
 e.tracked_hands(.08);e.call('high_five_update',e.body);assert e.played==3
report={'passed':True,'ASLR_bases':2,'checks':['spawn above actual server on both teams/formats','server stays under ball','serve arc raised and restored','jump apex +70cm','reason encoded without changing score team','point text with smaller reason','clap only after approaching','hands meet briefly','no repeated clap while touching','clap during rally','clap rearmed after point']}
(R/'analysis/v15-celebration-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
