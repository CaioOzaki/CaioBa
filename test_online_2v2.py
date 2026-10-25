"""Compiled online wrappers with deterministic Photon/Unity service stubs."""
exec(open(__file__.replace('test_online_2v2.py','test_2v2.py')).read().split('def run(base):')[0])
class OnlineEngine(Engine):
 def __init__(self,base,teams):
  super().__init__(base);self.online=True;self.people=[];self.ids={};self.assists=[];self.points=[]
  klass=self.alloc(0x200);self.statics=self.alloc();self.ptr(base+0x1542650,klass);self.ptr(klass+0xb8,self.statics)
  for team in teams:
   player=self.alloc();self.integer(player+0x28,team);self.people.append(player);self.ids[player]=len(self.people)
   t=self.alloc();self.transforms[player]=t;self.pos[t]=(0,0,-10 if team==0 else 10)
  self.ptr(self.statics,self.people[0]);self.listfield(self.statics,8,self.people)
  for team in (0,1):self.listfield(self.teams[team],0x38,[p for p in self.people if self.team(p)==team])
  self.settings=self.alloc();self.app=self.alloc();self.ptr(self.settings+0x18,self.app)
  self.call('network_version_hook',self.alloc());self.call('clear_teams_hook',self.game)
 def listfield(self,obj,offset,values):
  lst=self.alloc();arr=self.alloc();self.ptr(obj+offset,lst);self.ptr(lst+0x10,arr);self.integer(lst+0x18,len(values))
  for i,value in enumerate(values):self.ptr(arr+0x20+8*i,value)
 def team(self,player):return struct.unpack('<i',self.u.mem_read(player+0x28,4))[0]
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==ex['network_version_trampoline']:self.ret()
  elif r==0x61fcd0:self.ret(self.settings)
  elif r==0x60acf0:
   assert self.text[self.q(a+0x28)]==('Cloudcourt-2v2-v17' if self.val('online_format')==2 else 'Cloudcourt-4v4-v17');self.ret(1)
  elif r==0x60abf0:
   assert self.text[self.q(self.app+0x28)]==('Cloudcourt-2v2-v17' if self.val('online_format')==2 else 'Cloudcourt-4v4-v17');self.ret(1)
  elif r==ex['clear_teams_trampoline']:self.calls.append(('clear',));self.ret()
  elif r==ex['choose_team_trampoline']:self.integer(a+0x28,b);self.calls.append(('choose',a,b));self.ret()
  elif r==ex['online_setup_trampoline']:self.calls.append(('setup',tuple(self.team(p) for p in self.people)));self.ret()
  elif r==ex['client_motion_trampoline']:self.ret()
  elif r==ex['client_end_trampoline']:self.ret()
  elif r==0x253e30:self.ret()
  elif r==0x30cb70:self.ret(self.ids[a])
  elif r==0x2533a0:self.points.append(b);self.u.mem_write(a+0x78,b'\0');self.ret()
  elif r==ex['tracked_touch_trampoline']:self.u.mem_write(a+0x79,b'\0');self.integer(a+0x7c,c);self.ret()
  elif r==ex['collision_trampoline']:
   sp=u.reg_read(UC_X86_REG_RSP)-0x30;u.reg_write(UC_X86_REG_RSP,sp);self.ptr(sp,H+0xfa000)
   u.reg_write(UC_X86_REG_RCX,0);u.reg_write(UC_X86_REG_RDX,1);u.reg_write(UC_X86_REG_R8,0)
   u.reg_write(UC_X86_REG_RIP,self.b+ex['reception_assist_hook'])
  elif addr==H+0xfa000:
   self.assists.append(u.reg_read(UC_X86_REG_RAX));u.reg_write(UC_X86_REG_RSP,u.reg_read(UC_X86_REG_RSP)+0x28);self.ret()
  else:super().hook(u,addr,size,user)
 def call(self,name,*args):
  u=self.u;sp=S+0x80008;u.reg_write(UC_X86_REG_RSP,sp);self.ptr(sp,STOP)
  for reg,v in zip((UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9),list(args)+[0]*4):u.reg_write(reg,v)
  for i,v in enumerate(list(args)[4:]+[0]*8):self.ptr(sp+0x28+8*i,v)
  u.emu_start(self.b+ex[name],STOP,count=100000);assert u.reg_read(UC_X86_REG_RIP)==STOP,name
  return u.reg_read(UC_X86_REG_RAX)
 def motion(self,team,hit=True):
  vec=self.alloc();self.vec(vec,(0,1,0));self.call('client_motion_hook',self.alloc(),vec,vec,hit,100+team,team,0,0)
 def receive(self,player):
  body=self.alloc(0x200);self.ptr(body+0x168,player);self.call('collision_hook',body,0,0,0,0);return self.assists[-1]

def run(base):
 e=OnlineEngine(base,(0,1));e.call('solo_awake_hook',e.page)
 e.call('online_entry_hook',e.page)
 assert e.val('online_selector')==1 and e.label(0x40)=='4v4' and e.label(0x48)=='2v2'
 assert e.text[e.labels[e.q(e.page+0x38)]]=='Online - Modo de jogo'
 e.call('solo_day_hook',e.page);assert e.val('online_format')==4 and e.val('online_selector')==0
 e.call('connect_default_hook');assert e.text[e.q(e.app+0x28)]=='Cloudcourt-4v4-v17'
 e.call('clear_teams_hook',e.game);assert e.val('doubles_enabled')==0
 for row in e.areas:
  for i,a in enumerate(row):assert e.q(a+0x28)==row[(i+1)%4]
 e.calls=[]
 for slot in range(4):e.call('spawn_bot_hook',e.game,123,1,slot)
 assert len(e.calls)==4
 e.call('online_entry_hook',e.page);e.call('solo_night_hook',e.page)
 assert e.val('online_format')==2
 e.call('connect_settings_hook',e.app,0);e.call('clear_teams_hook',e.game);assert e.val('doubles_enabled')==1
 e.call('online_entry_hook',e.page);e.call('solo_back_hook',e.page);assert e.val('online_selector')==0
 e.call('solo_entry_hook',e.page);assert e.text[e.labels[e.q(e.page+0x38)]]=='Solo - Modo de jogo'

 for teams in ((0,1),(0,0),(1,1),(0,0,1),(0,1,1),(0,0,1,1),(0,0,0,0),(1,1,1,1)):
  e=OnlineEngine(base,teams)
  assert e.text[e.q(e.app+0x28)]=='Cloudcourt-2v2-v17'
  # The production connect routine inlines and overwrites AppVersion.
  e.ptr(e.app+0x28,e.string('1.7'));e.flag('online_version_ready',0)
  assert e.call('connect_default_hook')&255 and e.val('online_version_ready')==1
  copy=e.alloc();e.ptr(copy+0x28,e.string('1.7'));e.flag('online_version_ready',0)
  assert e.call('connect_settings_hook',copy,0)&255 and e.val('online_version_ready')==1
  assert e.val('doubles_enabled')==1 and e.val('quartet_enabled')==0
  # Remote clear-teams callback must configure geometry without host Go.
  for row in e.areas:
   assert e.q(row[2]+0x28)==row[0] and e.q(row[0]+0x28)==row[2]
   assert e.vec(row[2]+0x18)[2]==9
  e.call('online_setup_hook',e.game);assigned=e.calls[-1][1]
  assert max(assigned.count(0),assigned.count(1))<=2 and len(assigned)==len(teams)
  # Simulate the slots emitted by the original host assignment loop.
  for team in (0,1):
   members=[p for p in e.people if e.team(p)==team];e.calls=[]
   for slot,player in enumerate(members):e.call('add_player_hook',e.teams[team],player,slot)
   for slot in range(len(members),4):e.call('spawn_bot_hook',e.game,123,team,slot)
   slots=[c[-1] for c in e.calls if c[0] in ('member','spawn')]
   assert len(slots)==2 and sorted(slots)==[0,2],(teams,team,e.calls)
  e.call('player_speed_hook');speed=struct.unpack('<f',struct.pack('<I',e.u.reg_read(UC_X86_REG_XMM0)&0xffffffff))[0]
  assert abs(speed-2.4)<1e-5
 # Client reception must work on either team, even though host-owned rules
 # do not set ballInPlay on that client.
 for localteam in (0,1):
  e=OnlineEngine(base,(localteam,1-localteam));player=e.people[0]
  e.u.mem_write(e.game+0x78,b'\0\0')
  e.call('net_new_rally_hook',e.game,1-localteam);assert e.receive(player)==0
  e.motion(1-localteam,False);assert e.receive(player)==0
  e.motion(1-localteam);assert e.receive(player)==1
  assert e.receive(e.people[1])==0
  e.motion(localteam);assert e.receive(player)==0
  e.motion(1-localteam);assert e.receive(player)==1
  e.call('net_new_rally_hook',e.game,localteam);e.motion(localteam);assert e.receive(player)==0
  e.call('net_new_rally_hook',e.game,1-localteam);e.motion(1-localteam)
  v=e.alloc();e.vec(v,(0,0,0));e.call('client_end_hook',e.game,0,v);assert e.receive(player)==0
 # Prevent choosing a full side; allow moving to a free side.
 e=OnlineEngine(base,(0,0,1,1));p=e.people[0];e.call('choose_team_hook',p,1);assert e.team(p)==0
 e=OnlineEngine(base,(0,1));p=e.people[0];e.call('choose_team_hook',p,1);assert e.team(p)==1
 # Authoritative fault for a remote player's GAME jump, not head height.
 e=OnlineEngine(base,(0,1));remote=e.people[1];body=e.alloc(0x200);e.ptr(remote+0x80,body)
 e.u.mem_write(e.game+0x78,b'\1\0');e.flag('serve_flight_team',0);e.flt(body+0xb8,.5)
 e.call('tracked_touch_hook',e.game,e.ids[remote],1);assert e.points==[0]
 # Offline selection still controls solo after leaving the room.
 e.online=False;e.flag('doubles_requested',0);e.call('game_go_hook',e.game);assert e.val('quartet_enabled')==1 and e.val('doubles_enabled')==0
for base in (0x180000000,0x190000000):run(base)
report={'passed':True,'bases':2,'layouts':8,'checks':['separate Photon app version','client initialization without Go','two slots per side','2/3/4 humans plus remaining bots','host resolves overfull choices','human speed 1.6 on both teams','remote reception state from RPCs','full team selection guard','remote jump fault','solo restored'],'scope':'Actual compiled hooks with Photon/Unity stubs; no live two-PC headset session performed.'}
(R/'analysis/online-2v2-test-results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
