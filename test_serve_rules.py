"""Exercise compiled hooks, including relocated code and both match formats."""
exec(open(__file__.replace('test_serve_rules.py','test_2v2.py')).read().split('def run(base):')[0])
class RulesEngine(Engine):
 def __init__(self,base,doubles):
  super().__init__(base);self.ids={};self.people=[];self.bots=[];self.points=[];self.touches=[];self.assessed=[];self.jump_next=1
  for team in range(2):
   for kind,offset in enumerate((0x38,0x30)):
    obj=self.alloc();self.ids[obj]=team*10+kind+1;self.integer(obj+0x28,team)
    (self.people if kind==0 else self.bots).append(obj)
    lst=self.alloc();arr=self.alloc();self.ptr(self.teams[team]+offset,lst);self.ptr(lst+0x10,arr);self.integer(lst+0x18,1);self.ptr(arr+0x20,obj)
    t=self.alloc();self.transforms[obj]=t;self.pos[t]=(0,0,10 if team else -10)
  self.flag('doubles_requested',doubles);self.call('game_go_hook',self.game)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==0x30cb70:self.ret(self.ids[a])
  elif r==0x2533a0:self.points.append(b);self.u.mem_write(a+0x78,b'\0');self.ret()
  elif r==ex['tracked_touch_trampoline']:
   self.touches.append((b,c));self.u.mem_write(a+0x79,b'\0');self.integer(a+0x7c,c);self.ret()
  elif r==ex['bot_assess_trampoline']:
   self.assessed.append(self.u.mem_read(a+0x38,1)[0]);self.integer(a+0xa4,1);self.ret()
  elif r==ex['player_jump_trampoline']:self.integer(a+0x10,self.jump_next);self.ret(self.jump_next!=-1)
  elif r==ex['serve_routine_trampoline']:
   state=struct.unpack('<i',u.mem_read(a+0x10,4))[0]
   if state==3:self.u.mem_write(self.q(a+0x20)+0x78,b'\1\0')
   self.ret(0)
  else:super().hook(u,addr,size,user)
 def touch(self,obj):self.call('tracked_touch_hook',self.game,self.ids[obj],struct.unpack('<i',self.u.mem_read(obj+0x28,4))[0])
 def prepare(self,team):self.u.mem_write(self.game+0x78,b'\1\1');self.integer(self.game+0x7c,team)
 def jump(self,obj):
  routine=self.alloc();self.ptr(routine+0x20,obj);self.jump_next=1;self.call('player_jump_hook',routine);return routine
 def land(self,routine):self.jump_next=3;self.call('player_jump_hook',routine)

def run_rules(base,doubles):
 e=RulesEngine(base,doubles)
 for team in (0,1):
  player=e.people[team];bot=e.bots[team];opponent=e.bots[1-team];t=e.transforms[player]
  for z,bad in ((0,True),(-4 if team==0 else 4,True),(-9 if team==0 else 9,True),(-9.1 if team==0 else 9.1,False)):
   e.pos[t]=(0,0,z);e.prepare(team);before=len(e.points);e.touch(player)
   assert len(e.points)==before+bad
   if bad:assert e.points[-1]==1-team
  # Jump serve: takeoff behind the baseline remains legal.
  e.pos[t]=(0,0,-10 if team==0 else 10);jump=e.jump(player);e.pos[t]=(0,0,0)
  e.prepare(team);before=len(e.points);e.touch(player);assert len(e.points)==before;e.land(jump)
  # Grounded first contact allowed; a subsequent jump in this rally is legal.
  e.prepare(1-team);e.touch(opponent);before=len(e.points);e.touch(player);assert len(e.points)==before
  jump=e.jump(player);e.touch(player);assert len(e.points)==before;e.land(jump)
  # Airborne first contact awards opponent, only once.
  e.prepare(1-team);e.touch(opponent);jump=e.jump(player);e.touch(player);assert e.points[-1]==1-team and len(e.points)==before+1
  e.touch(player);assert len(e.points)==before+1;e.land(jump)
  # Grounded during cooldown must NOT be a fault, despite native jumping flag.
  e.prepare(1-team);e.touch(opponent);e.u.mem_write(player+0x70,b'\1');before=len(e.points);e.touch(player);assert len(e.points)==before
  # Bot's own jump serve is allowed; airborne direct reception is a fault.
  e.u.mem_write(bot+0x80,b'\1');e.prepare(team);before=len(e.points);e.touch(bot);assert len(e.points)==before
  e.prepare(1-team);e.touch(opponent);e.touch(bot);assert len(e.points)==before+1 and e.points[-1]==1-team
  e.u.mem_write(bot+0x80,b'\0');e.prepare(1-team);e.touch(opponent);before=len(e.points);e.touch(bot);assert len(e.points)==before
  # AI remains grounded before and during enemy serve, then resumes normal tactics.
  e.u.mem_write(bot+0x38,b'\1');e.prepare(1-team)
  for phase in range(2):
   if phase:e.touch(opponent)
   e.call('bot_assess_hook',bot);assert e.assessed[-1]==0 and struct.unpack('<i',e.u.mem_read(bot+0xa4,4))[0]==2
   assert e.u.mem_read(bot+0x38,1)==b'\1'
  e.touch(bot);e.call('bot_assess_hook',bot);assert e.assessed[-1]==1 and struct.unpack('<i',e.u.mem_read(bot+0xa4,4))[0]==1
  e.prepare(team);e.call('bot_assess_hook',bot);assert e.assessed[-1]==1
  # Real human serve order: accepted hit precedes ballInPlay. The old
  # tests incorrectly set ballInPlay before every serving contact.
  e.call('game_go_hook',e.game)
  body=e.alloc(0x200);torso=e.alloc();e.ptr(player+0x80,body);e.ptr(body+0x38,torso)
  e.pos[t]=(0,0,-10 if team==0 else 10);e.pos[torso]=(0,1.6,-3 if team==0 else 3)
  e.u.mem_write(e.game+0x78,b'\0\1');e.u.mem_write(e.game+0x94,b'\1')
  before=len(e.points);e.touch(player);assert len(e.points)==before
  routine=e.alloc();e.ptr(routine+0x20,e.game);e.integer(routine+0x10,3)
  e.call('serve_routine_hook',routine);assert len(e.points)==before+1 and e.points[-1]==1-team
  e.call('serve_routine_hook',routine);assert len(e.points)==before+1
  # Outside body remains legal even with a misleading root inside.
  e.call('game_go_hook',e.game);e.pos[t]=(0,0,0);e.pos[torso]=(0,1.6,-10 if team==0 else 10)
  e.u.mem_write(e.game+0x78,b'\0\1');before=len(e.points);e.touch(player)
  e.call('serve_routine_hook',routine);assert len(e.points)==before and e.val('serve_flight_team')==team
  # Serving team cannot play its own serve again, including net rebounds.
  e.call('bot_assess_hook',bot);assert struct.unpack('<i',e.u.mem_read(bot+0xa4,4))[0]==0
  e.touch(bot);assert len(e.points)==before+1 and e.points[-1]==1-team
  e.ptr(player+0x80,0)
 return True
for base in (0x180000000,0x190000000):
 for doubles in (0,1):assert run_rules(base,doubles)
report={'passed':True,'formats':['4v4','2v2'],'teams':2,'ASLR_bases':2,'checks':['inside and baseline fault','outside legal','legal jump serve takeoff','grounded receive','later jumping contact','airborne receive fault once','landed cooldown legal','bot own serve legal','bot airborne fault','bot grounded legal','AI avoids receive jump before and after serve','normal AI restored'],'scope':'Actual compiled hooks with deterministic engine stubs; headset playtest required.'}
(R/'analysis/serve-rules-test-results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
