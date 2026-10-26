"""Execute Cloudcourt native hooks with two relocated memory layouts."""
__file__=__file__.replace('test_cloudcourt_v16.py','test_celebration_v15.py')
exec(open(__file__).read().split('\nfor base in ')[0])
class CloudEngine(CelebrationEngine):
 def __init__(self,base):
  super().__init__(base);self.names={};self.selected=[];self.probe_reception=False;self.a_button=False;self.submit=False;self.assists=[];self.prefs={}
  self.ui_samples=self.alloc(0x20+1764*4);self.ui_clip=self.alloc()
  self.ptr(base+0x15260b8,self.alloc());self.ptr(base+0x15269d0,self.alloc())
 def string(self,s):
  v=self.alloc(0x400);self.text[v]=s;self.integer(v+0x10,len(s));self.u.mem_write(v+0x14,s.encode('utf-16le'));return v
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==ex['collision_trampoline'] and self.probe_reception:
   sp=u.reg_read(UC_X86_REG_RSP)-0x30;u.reg_write(UC_X86_REG_RSP,sp);self.ptr(sp,H+0xfa000)
   u.reg_write(UC_X86_REG_RCX,0);u.reg_write(UC_X86_REG_RDX,0);u.reg_write(UC_X86_REG_R8,0);u.reg_write(UC_X86_REG_RIP,self.b+ex['reception_assist_hook'])
  elif addr==H+0xfa000:
   self.assists.append(u.reg_read(UC_X86_REG_RAX));u.reg_write(UC_X86_REG_RSP,u.reg_read(UC_X86_REG_RSP)+0x28);self.ret()
  elif r==ex['clamp_player_trampoline']:self.ret()
  elif r==0xa0bdd0:self.ret(self.string(self.names.get(a,'')))
  elif r==0x6054c0:self.ret(self.generic)
  elif r==0xe6e1b0:self.ret(1)
  elif r==0xa12870:self.prefs[self.text[a]]=b;self.ret()
  elif r==0xa12690:self.ret(self.prefs.get(self.text[a],b))
  elif r in (0x478bf0,0x83c7f0):self.ret(a!=0)
  elif r==0x14a4f0 and b==1764:self.ret(self.ui_samples)
  elif r==0xeba090 and b==1764:self.ret(self.ui_clip)
  elif r==0xeba5f0 and a==self.ui_clip:self.ret(True)
  elif r in (0xebc370,0xebc500,0xebc460):self.ret()
  elif r==0x1c1f90:
   assert b==1;arr=self.alloc();self.ptr(arr+0x18,1);self.ret(arr)
  elif r==0x14ba70:
   boxed=self.alloc();self.integer(boxed+0x10,struct.unpack('<i',u.mem_read(b,4))[0]);self.ret(boxed)
  elif r==0xe6bb50:
   assert self.text[b]=='Client_ChooseTeam' and c==5
   args=u.reg_read(UC_X86_REG_R9);boxed=self.q(args+0x20);value=struct.unpack('<i',u.mem_read(boxed+0x10,4))[0];self.selected.append(value)
   u.reg_write(UC_X86_REG_RCX,self.player);u.reg_write(UC_X86_REG_RDX,value);u.reg_write(UC_X86_REG_R8,0);u.reg_write(UC_X86_REG_RIP,self.b+ex['client_choose_hook'])
  elif r==ex['choose_team_trampoline']:self.selected.append(b);u.reg_write(UC_X86_REG_RIP,self.b+ex['client_choose_hook'])
  elif r==0x14a510:
   arr=self.alloc(0x100);self.ptr(arr,a);self.ptr(arr+0x18,b);self.ret(arr)
  elif r==0xb75750:self.ret()
  elif r==0x452d40:self.ret(self.a_button)
  elif r==ex['ui_submit_trampoline']:self.submit=bool(a);self.ret()
  else:super().hook(u,addr,size,user)
 def reception(self):
  self.probe_reception=True;self.call('collision_hook',self.body,0,0,0);self.probe_reception=False;return self.assists[-1]

checks=[]
for base in (0x180000000,0x190000000):
 e=CloudEngine(base)
 for fmt in (2,4):
  e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4)
  for team in (0,1):
   player=e.player;e.integer(player+0x28,team);t=e.transforms[player];e.pos[t]=(0,0,0)
   torso=e.alloc();e.ptr(e.body+0x38,torso);e.ptr(player+0x80,e.body);e.pos[torso]=(0,1.2,.3 if team==0 else -.3)
   e.call('clamp_player_hook',player);assert abs(e.pos[t][2]-(-.48 if team==0 else .48))<1e-5
  e.integer(e.player+0x28,0)
  for last,used,expected in [(1,1,1),(0,1,0),(1,2,1),(0,0,1),(0,2,0)]:
   e.used(last,used);assert e.reception()==expected,(fmt,last,used)
  e.used(0,1);v=e.hit();import math
  duration=(v[1]+math.sqrt(v[1]**2-19.62*1.15))/9.81
  assert abs(v[0]*duration)<=3.6501 and abs(-4+v[2]*duration+1.15)<1e-4
  bot=e.members[0][2];e.call('bot_jump_hook',bot);vy=e.flt(bot+0x98);assert abs((vy*vy-e.jump_speed**2)/19.62-.7)<1e-5
  e.used(0,2);e.call('bot_hit_hook',bot,e.ball);assert abs(e.apex[-1]-2.6)<1e-5 and e.flt(bot+0x44)==2
 e.online=True;e.flag('online_version_ready',1)
 e.call('net_new_rally_hook',e.game,1);e.receive(1);assert e.reception()==1
 e.receive(0);assert e.reception()==0;e.receive(1);assert e.reception()==1
 # Lobby and rally both permit high fives; sweeping across contact is detected.
 e.tracked_hands(.5);e.call('high_five_update',e.body);e.tracked_hands(.08);e.call('high_five_update',e.body);assert e.played==1
 for _ in range(60):e.tracked_hands(.5);e.call('high_five_update',e.body)
 e.tracked_hands(-.5);e.call('high_five_update',e.body);assert e.played==2
 for _ in range(8):e.tracked_hands(.08);e.call('high_five_update',e.body)
 assert e.played==2
 # Skin selection is broadcast via an existing reliable RPC and decoded per player.
 button=e.alloc();e.names[button]='PuloSkin2';e.call('button_press_hook',button);assert e.selected[-1]==0x5c210044
 assert struct.unpack('<i',e.u.mem_read(e.player+0x28,4))[0]==0
 old_area=e.q(e.player+0x20);other=e.members[1][0];new_area=e.q(other+0x20)
 e.names[button]='PuloTeams';e.call('button_press_hook',button)
 assert struct.unpack('<i',e.u.mem_read(e.player+0x28,4))[0]==0 # queued until the point ends
 e.call('client_end_hook',e.game,0,e.pv)
 assert struct.unpack('<i',e.u.mem_read(e.player+0x28,4))[0]==1 and e.q(e.player+0x20)==new_area
 assert struct.unpack('<i',e.u.mem_read(other+0x28,4))[0]==0 and e.q(other+0x20)==old_area
 e.a_button=True;e.call('ui_submit_hook',0);assert e.submit
 e.a_button=False;e.call('ui_submit_hook',0);assert not e.submit
 e.call('ui_submit_hook',1);assert e.submit
 checks.append(hex(base))
report={'passed':True,'ASLR_bases':checks,'checks':['symmetric net limits with room-scale torso offset','first team touch each possession in both formats','second touch still unassisted','setting window 1.15m from net','bot jump apex +70cm from original','third-touch attack clearance and restored fields','high five during rally','swept fast hand contact','clap cooldown','explicit skin RPC','team swap queued until next point, updates membership and areas','A and trigger menu input'],'scope':'Compiled native code with engine stubs; VR and real two-PC session still required.'}
(R/'analysis/v16-feature-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
