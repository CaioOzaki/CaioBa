"""Actual delivered v28 helper plus original native touch accounting and Go's
inlined Bomb opponent roster branch, with deterministic Unity/Photon fixtures.
No Unity VR / Quest / two-PC playtest claim.
"""
exec(open(__file__.replace('test_rules_bomb_v28.py','test_2v2.py')).read().split('def run(base):')[0])
import hashlib,math
class Rules28(Engine):
 def __init__(self,base,fmt=2,bomb=False,indoor=False):
  self.ids={};self.points=[];self.touch_calls=0;self.master=True;self.jump_next=1;self.native_roster=False;self.stopped=False;self.prefabs=[]
  super().__init__(base)
  self.flag('doubles_requested',fmt==2);self.u.mem_write(self.game+0x68,bytes([bomb]));self.call('game_go_hook',self.game)
  self.integer(self.game+0x98,-1);self.integer(self.game+0x7c,1);self.integer(self.game+0x9c,0)
  self.people=[];self.bots=[]
  for team in (0,1):
   for kind,offset in enumerate((0x38,0x30)):
    obj=self.alloc(0x200);self.ids[obj]=10*team+kind+1;self.integer(obj+0x28,team)
    (self.people if not kind else self.bots).append(obj)
    lst=self.alloc();arr=self.alloc();self.ptr(self.teams[team]+offset,lst);self.ptr(lst+0x10,arr);self.integer(lst+0x18,1);self.ptr(arr+0x20,obj)
    t=self.alloc();self.transforms[obj]=t;self.pos[t]=(0,0,-.7 if team==0 else .7)
    self.ptr(obj+0x20,self.areas[team][2])
  self.ball=self.alloc(0x200);t=self.alloc();self.transforms[self.ball]=t;self.pos[t]=(0,2.8,-.3)
  k=self.alloc(0x200);st=self.alloc();self.ptr(self.b+0x15426f0,k);self.ptr(k+0xb8,st);self.ptr(st,self.ball)
  k=self.alloc(0x200);st=self.alloc();env=self.alloc();self.ptr(self.b+0x15422a0,k);self.ptr(k+0xb8,st);self.ptr(st,env)
  text=self.alloc();word='IndoorArenaScene' if indoor else 'Scene';self.integer(text+0x10,len(word));self.u.mem_write(text+0x14,word.encode('utf-16le'));self.ptr(env+0x18,text)
  # Skip only the generated metadata initialization; execute original native
  # PlayerTouchedBall itself, reached through its delivered trampoline.
  self.u.mem_write(self.b+0x14ffd30,b'\1')
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c,d=[u.reg_read(x) for x in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9)]
  if r==0x30cb70:self.ret(self.ids[a])
  elif r==0x61f230:self.ret(self.master)
  elif r==0x2533a0:self.points.append(b);self.u.mem_write(a+0x78,b'\0');self.ret()
  elif r==0x1c21b0:self.ret()
  elif r==0x1c22e0:self.ret(self.alloc())
  elif r==0xb7b820:self.ret()
  elif r==0xb79db0:self.vec(a,(0,0,0));self.ret(a)
  elif r==0x77eb50:self.fuse_calls=getattr(self,'fuse_calls',0)+1;self.ret()
  elif r==0xef3470:self.ret(0)
  elif r==0x77fe10:self.ret(f=.105)
  elif r==ex['tracked_touch_trampoline']:self.touch_calls+=1 # execute production/native code
  elif r==ex['player_jump_trampoline']:self.integer(a+0x10,self.jump_next);self.ret(self.jump_next!=-1)
  elif r==0x253832 and self.native_roster:self.stopped=True;u.reg_write(UC_X86_REG_RIP,STOP)
  elif r==0x253e30:self.ret()
  elif r==ex['client_motion_trampoline']:
   self.last_native_context=struct.unpack('<i',u.mem_read(u.reg_read(UC_X86_REG_RSP)+0x38,4))[0];self.ret()
  elif r==ex.get('change_motion_v28_trampoline'):
   self.sent_context=struct.unpack('<I',u.mem_read(u.reg_read(UC_X86_REG_RSP)+0x40,4))[0];self.sent_position=self.vec(b);self.sent_velocity=self.vec(c);self.ret()
  elif r==0x60acf0:self.ret(1)
  elif r==0x60fb50:self.prefabs.append(self.text.get(a,'base'));self.ret(123)
  else:super().hook(u,addr,size,user)
 def touch(self,member):self.call('tracked_touch_hook',self.game,self.ids[member],struct.unpack('<i',self.u.mem_read(member+0x28,4))[0])
 def state(self,team=1,count=3,id=99,serving=False):
  self.call('game_go_hook',self.game)
  self.u.mem_write(self.game+0x78,bytes([1,serving]));self.integer(self.game+0x7c,team);self.integer(self.game+0x9c,count);self.integer(self.game+0x98,id);self.flag('serve_flight_team',-1)
 def count(self):return struct.unpack('<i',self.u.mem_read(self.game+0x9c,4))[0]
 def allowed(self,member):return self.call('allowed_hit_v28_hook',self.game,self.ids[member],struct.unpack('<i',self.u.mem_read(member+0x28,4))[0],0)&255
 def jump(self,member):
  routine=self.alloc();self.ptr(routine+0x20,member);self.call('player_jump_hook',routine);return routine
 def native_enemy_roster(self):
  self.native_roster=True;self.calls=[];self.stopped=False;self.u.reg_write(UC_X86_REG_RSP,S+0x80000)
  self.u.reg_write(UC_X86_REG_RDI,self.game);self.u.reg_write(UC_X86_REG_RSI,0)
  self.u.emu_start(self.b+0x253750,STOP,count=100000);assert self.stopped
  return [x for x in self.calls if x[0]=='spawn']

 def native_bot_serve(self,team):
  # Execute original StartNewRallyRoutine's bot placement, motion RPC,
  # state4 wait, then its actual state4 continuation and Bomb StartFuse.
  routine=self.alloc();self.ptr(routine+0x20,self.game);self.ptr(routine+0x30,self.ball);self.integer(routine+0x28,team)
  self.integer(self.game+0x7c,team);self.u.mem_write(self.game+0x78,b'\0\1')
  points=self.alloc();self.ptr(self.game+0x20,points);self.integer(points+0x18,2)
  for i in (0,1):
   t=self.alloc();self.pos[t]=(0,3.31,-2.25 if i==0 else 2.25);self.ptr(points+0x20+8*i,t)
  klass=self.alloc(0x200);self.ptr(self.b+0x15190a0,klass)
  u=self.u;sp=S+0x80008;self.ptr(sp,STOP);u.reg_write(UC_X86_REG_RSP,sp-0xa8)
  u.reg_write(UC_X86_REG_RSI,routine);u.reg_write(UC_X86_REG_RBP,self.game);u.reg_write(UC_X86_REG_R15,0)
  u.emu_start(self.b+0x25ad2c,STOP,count=100000)
  assert u.reg_read(UC_X86_REG_RIP)==STOP and struct.unpack('<i',u.mem_read(routine+0x10,4))[0]==4
  before=getattr(self,'fuse_calls',0);self.call('serve_routine_hook',routine)
  assert u.mem_read(self.game+0x78,2)==b'\1\0'
  return getattr(self,'fuse_calls',0)-before

 def motion(self,member,context=0,sender=False):
  u=self.u;sp=S+0x80008;u.reg_write(UC_X86_REG_RSP,sp);self.ptr(sp,STOP)
  pos=self.alloc();self.vec(pos,self.pos[self.transforms[self.ball]]);vel=self.alloc();self.vec(vel,(0,-1,2))
  for reg,value in zip((UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9),(self.ball,pos,vel,1)):u.reg_write(reg,value)
  team=struct.unpack('<i',u.mem_read(member+0x28,4))[0]
  values=(0,self.ids[member],team,context,0) if sender else (self.ids[member],team,context,0)
  for i,v in enumerate(values):self.ptr(sp+0x28+8*i,v&0xffffffffffffffff)
  u.emu_start(self.b+ex['change_motion_v28_hook' if sender else 'client_motion_hook'],STOP,count=100000)
  assert u.reg_read(UC_X86_REG_RIP)==STOP

def run():
 cases=[]
 for base in (0x180000000,0x190000000):
  e=Rules28(base);e.call('solo_awake_hook',e.page)
  assert e.label(0x58)=='Extras'
  e.call('solo_bomb_v28_hook',e.page);assert e.label(0x40)=='Bomb 4v4' and e.label(0x48)=='Bomb 2v2'
  e.call('solo_back_hook',e.page);assert e.val('solo_stage')==0
  e.call('solo_bomb_v28_hook',e.page);e.call('solo_night_hook',e.page);e.call('solo_start_hook',e.page,0,1);assert e.val('doubles_requested')==1
  e.call('online_entry_hook',e.page);e.call('solo_bomb_v28_hook',e.page);e.call('solo_day_hook',e.page)
  assert e.val('online_format')==4 and e.val('online_bomb_v28')==1
  e.call('online_entry_hook',e.page);e.call('solo_night_hook',e.page)
  assert e.val('online_format')==2 and not e.val('online_bomb_v28')
 for base in (0x180000000,0x190000000):
  for fmt in (2,4):
   for indoor in (False,True):
    for team in (0,1):
     e=Rules28(base,fmt,indoor=indoor);bot=e.bots[team];mate=e.people[team]
     z=-.3 if team==0 else .3;e.pos[e.transforms[e.ball]]=(0,2.8,z);e.u.mem_write(bot+0x80,b'\1')
     e.state(1-team);e.touch(bot);assert e.count()==(0 if indoor else 1) and e.allowed(bot)
     e.touch(bot);assert e.count()==(1 if indoor else 2) and not e.allowed(bot)
     before=len(e.points);e.touch(bot);assert len(e.points)==before+1 and e.points[-1]==1-team
     # Three team hits after Indoor block; Beach block + two further hits.
     e.state(1-team);e.touch(bot);e.touch(bot);e.touch(mate)
     if indoor:assert e.allowed(bot);e.touch(bot)
     assert e.count()==3 and not e.allowed(mate)
     before=len(e.points);e.touch(mate);assert len(e.points)==before+1
     # Grounded, low and backcourt contacts are ordinary receptions.
     for airborne,mp,bp in ((False,(0,0,z),(0,2.8,z)),(True,(0,0,z),(0,2.39,z)),(True,(0,0,-4 if team==0 else 4),(0,2.8,z))):
      e.state(1-team);e.u.mem_write(bot+0x80,bytes([airborne]));e.pos[e.transforms[bot]]=mp;e.pos[e.transforms[e.ball]]=bp;e.touch(bot)
      assert e.count()==1 and not e.allowed(bot)
     # A teammate's jumping set never earns the block exception.
     e.state(team,1,99);e.u.mem_write(bot+0x80,b'\1');e.pos[e.transforms[bot]]=(0,0,z);e.pos[e.transforms[e.ball]]=(0,2.8,z);e.touch(bot)
     assert e.count()==2 and not e.allowed(bot)
     # Human jump state follows the actual mod jump coroutine wrapper.
     e.state(1-team);e.jump(mate);e.touch(mate);assert e.count()==(0 if indoor else 1) and e.allowed(mate)
     # Receiving a serve as a net block remains a fault, once.
     e.state(1-team);e.jump(mate);e.flag('serve_flight_team',1-team);before=len(e.points);e.touch(mate);assert len(e.points)==before+1
     e.touch(mate);assert len(e.points)==before+1
     # An airborne pass away from the net is not a serve block.
     e.state(1-team);e.jump(mate);e.flag('serve_flight_team',1-team);e.pos[e.transforms[mate]]=(0,0,-4 if team==0 else 4);before=len(e.points);e.touch(mate);assert len(e.points)==before
     assert e.touch_calls>0
     cases.append(dict(base=hex(base),format=fmt,indoor=indoor,team=team))
   for bomb in (False,True):
    e=Rules28(base,fmt,bomb=bomb)
    # Actual original inlined Go() roster path + delivered SpawnBot filter.
    spawned=e.native_enemy_roster();assert len(spawned)==fmt,(fmt,bomb,spawned)
    assert e.u.mem_read(e.game+0x68,1)[0]==bomb
    # Serve ball is placed above the actual serving bot on either court.
    for team in (0,1):
     e.integer(e.game+0x7c,team);bot=e.bots[team];e.ptr(bot+0x20,e.areas[team][2]);e.pos[e.transforms[bot]]=(1,0,-2.25 if team==0 else 2.25)
     out=e.alloc();fallback=e.alloc();e.pos[fallback]=(0,3.31,-2.25 if team==0 else 2.25)
     e.call('bot_serve_position_hook',out,fallback);assert e.vec(out)==(1.,struct.unpack('<f',struct.pack('<f',2.8))[0],-2.25 if team==0 else 2.25)
     assert e.native_bot_serve(team)==int(bomb)
     assert e.sent_position==e.vec(out) and e.sent_velocity==(0.,0.,0.) and e.sent_context==3
    if bomb:
     for x,z,inside in ((0,2,True),(2,2,False),(2.01,2,False),(0,4.5,False),(0,4.49,True),(3,6,False),(-2.01,-2,False),(0,-4.51,False)):
      for last in (0,1):
       e.state(last,1,99);e.pos[e.transforms[e.ball]]=(x,.105,z);n=len(e.points);e.call('bomb_ground_v28_hook',e.game,e.ball)
       assert len(e.points)==n+1 and e.points[-1]==((1 if z<0 else 0) if inside else 1-last)
    # Namespace and original prefabs are separated for all four room modes.
    e.flag('online_bomb_v28',bomb);e.flag('online_format',fmt);e.online=True
    app=e.alloc();e.call('connect_settings_hook',app,0);value=e.q(app+0x28)
    assert e.text[value]==f'Cloudcourt-{"Bomb-" if bomb else ""}{fmt}v{fmt}-v28'
    pos=e.alloc();e.vec(pos,(0,0,0));rot=e.alloc();name=e.string('original')
    e.call('online_rules_prefab_v28',name,pos,rot,0);e.call('online_ball_prefab_v28',name,pos,rot,0)
    assert e.prefabs==(['GameRulesBomb','VolleyballBomb'] if bomb else ['original','original'])
 # Explicit reliable marker keeps a remote client's counts correct even
 # when its remote Bot.jumping flag is false (it is not serialized).
 online_cases=[]
 for base in (0x180000000,0x190000000):
  for fmt in (2,4):
   for indoor in (False,True):
    e=Rules28(base,fmt,indoor=indoor);e.online=True;e.flag('online_version_ready',1);e.master=False
    for session in (1,2):
     e.call('net_new_rally_hook',e.game,1)
     e.motion(e.bots[1]);e.motion(e.people[0]);e.motion(e.bots[1])
     # Wire captured by a sender with its local real jump flag.
     bot=e.bots[0];e.u.mem_write(bot+0x80,b'\1');e.pos[e.transforms[e.ball]]=(0,2.8,-.3)
     e.motion(bot,2,sender=True);assert e.sent_context==0x48000002
     spin=e.alloc();e.vec(spin,(12,-24,36));packed=e.call('encode_spin',spin,2)&0xffffffff
     e.motion(bot,packed,sender=True);wire=e.sent_context
     assert wire&0xf8000000==0x58000000 and wire&0x07ffffff==packed&0x07ffffff
     # Remote receiving peer has no jumping bool, but accepts the marker.
     e.u.mem_write(bot+0x80,b'\0');e.motion(bot,wire);assert e.last_native_context==2 and e.allowed(bot)
     e.motion(bot,2);assert not e.allowed(bot) and e.allowed(e.people[0])
     e.motion(e.people[0],2)
     if indoor:assert e.allowed(bot);e.motion(bot,2)
     assert not e.allowed(e.people[0])
     # A new rally clears prior id/count/serve marker in the same scene.
     e.call('net_new_rally_hook',e.game,0);assert e.allowed(bot) and e.allowed(e.people[0])
    online_cases.append(dict(base=hex(base),format=fmt,indoor=indoor,sessions=2))
 report=dict(passed=True,online_cases=online_cases,cases=cases,actual_production_c=True,actual_original_touch_accounting=True,actual_native_inlined_opponent_roster=True,checks=['Indoor block uses zero hits; Beach one','same blocker next contact once only','teammate and backcourt contacts ordinary','human and bot airborne states','serve net block fault once; backcourt jump receive legal','both teams and both formats','original native GameRules touch accounting','Bomb exact small-court boundary winners','native bot-serve coroutine placement and state4 continuation','Bomb fuse starts exactly once after native wait','bot serve above serving bot','all four v28 room namespaces/prefabs','sender block marker preserves full spin payload','remote client without Bot.jumping gets exact block counts','same blocker next touch once on client','two rally epochs reset ids/counts'],scope='Actual full patched DLL CPU emulation with deterministic Unity/Photon fixtures. No headset, live Unity physics or two-PC claim.',sha256=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest())
 (R/'analysis/v28-rules-bomb-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':run()
