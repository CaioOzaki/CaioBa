"""Exercise reception scope and ally tactics using the actual patched x64 code."""
exec(open(__file__.replace('test_reception.py','test_2v2.py')).read().split('def run(base):')[0])
class ReceptionEngine(Engine):
 def __init__(self,base):
  super().__init__(base);self.assists=[];self.tactics=[];self.pref=1;self.null_target=False
  self.body=self.alloc(0x200);self.player=self.alloc();self.ptr(self.body+0x168,self.player)
  self.integer(self.player+0x28,0);self.integer(self.bot+0x28,0)
  self.integer(self.bot+0xa4,1);self.flt(self.bot+0x4c,.6);self.flt(self.bot+0x50,.2)
  players=self.alloc();arr=self.alloc();self.ptr(self.teams[0]+0x38,players);self.integer(players+0x18,1);self.ptr(players+0x10,arr);self.ptr(arr+0x20,self.player)
  t=self.alloc();self.transforms[self.player]=t;self.pos[t]=(-2,0,-4.5)
  self.flag('doubles_requested',1);self.call('game_go_hook',self.game)
  self.u.mem_write(self.game+0x78,b'\1\1')
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==ex['collision_trampoline']:
   sp=u.reg_read(UC_X86_REG_RSP)-0x30;u.reg_write(UC_X86_REG_RSP,sp);self.ptr(sp,H+0xfa000)
   u.reg_write(UC_X86_REG_RCX,0);u.reg_write(UC_X86_REG_RDX,1);u.reg_write(UC_X86_REG_R8,0)
   u.reg_write(UC_X86_REG_RIP,self.b+ex['reception_assist_hook'])
  elif addr==H+0xfa000:
   self.assists.append(u.reg_read(UC_X86_REG_RAX));u.reg_write(UC_X86_REG_RSP,u.reg_read(UC_X86_REG_RSP)+0x28);self.ret()
  elif r==ex['tracked_touch_trampoline']:
   if self.u.mem_read(a+0x78,1)==b'\1':
    self.u.mem_write(a+0x79,b'\0');self.integer(a+0x7c,c);self.integer(a+0x98,b)
   self.ret()
  elif r==ex['bot_hit_trampoline']:
   self.tactics.append((struct.unpack('<i',u.mem_read(a+0xa4,4))[0],self.flt(a+0x4c),self.flt(a+0x50)));self.ret()
  elif r==0xa12690:self.ret(self.pref)
  elif r==0x30cb70:self.ret(999)
  elif r==ex['pass_target_trampoline'] and self.null_target:self.ret(0)
  elif r==0x270680:self.ret(self.target)
  else:super().hook(u,addr,size,user)
 def receive(self):self.call('collision_hook',self.body,0,0,0);return self.assists[-1]
 def serve(self,team):self.u.mem_write(self.game+0x78,b'\1\1');self.call('tracked_touch_hook',self.game,100+team,team)

def run_reception(base):
 e=ReceptionEngine(base)
 assert e.receive()==0,'No assist before an opponent serve'
 e.serve(1);assert e.val('reception_pending')==1 and e.receive()==1
 assert e.receive()==1,'Rejected contact must not consume reception'
 assert e.call('reception_assist_hook',0,1)==0,'Collision context must not leak'
 e.call('tracked_touch_hook',e.game,200,0);assert e.receive()==0
 e.call('tracked_touch_hook',e.game,101,1);assert e.receive()==0,'Later opponent return is not another serve'
 e.serve(1);e.call('tracked_touch_hook',e.game,201,0);assert e.receive()==0,'Bot reception consumes the first contact'
 e.serve(0);assert e.receive()==0
 e.serve(1);e.u.mem_write(e.game+0x78,b'\0');assert e.receive()==0,'Ended rally cannot enable assist'
 e.u.mem_write(e.game+0x78,b'\1\1');assert e.receive()==0,'Next serve preparation cannot reuse old reception'
 e.serve(1);e.integer(e.player+0x28,1);assert e.receive()==0;e.integer(e.player+0x28,0)
 e.online=True;assert e.receive()==0;e.online=False
 e.flag('doubles_enabled',0);e.pref=0;assert e.receive()==0;e.pref=1;assert e.receive()==1
 e.flag('doubles_enabled',1);e.pref=0;e.serve(1);assert e.receive()==1,'Assist is available even with global preference disabled'
 original=(1,.6,.2)
 for last_team,used,team,serving,enabled,expected in [(1,1,0,0,1,True),(0,1,0,0,1,True),(0,2,0,0,1,False),(1,1,1,0,1,False),(0,0,0,1,1,False),(1,1,0,0,0,False)]:
  e.flag('doubles_enabled',enabled);e.integer(e.game+0x7c,last_team);e.integer(e.game+0x9c,used);e.integer(e.bot+0x28,team);e.u.mem_write(e.game+0x79,bytes([serving]))
  e.call('bot_hit_hook',e.bot,0)
  state=e.tactics[-1]
  assert (state[0]==2 and state[1]>1 and state[2]==0)==expected
  assert struct.unpack('<i',e.u.mem_read(e.bot+0xa4,4))[0]==1 and abs(e.flt(e.bot+0x4c)-.6)<1e-6 and abs(e.flt(e.bot+0x50)-.2)<1e-6
 e.flag('doubles_enabled',1);e.integer(e.game+0x7c,0);e.integer(e.game+0x9c,1);e.integer(e.bot+0x28,0);e.u.mem_write(e.game+0x79,b'\0')
 e.null_target=True;e.call('pass_target_hook',e.bot)
 assert e.vec(e.target+0x10)==(-2,struct.unpack('<f',struct.pack('<f',1.2))[0],-4.5) and abs(e.flt(e.target+0x20)-3.65)<1e-5 and e.u.mem_read(e.target+0x24,1)==b'\1'
 e.call('game_go_hook',e.game);assert e.val('reception_pending')==0

run_reception(0x180000000);run_reception(0x190000000)
report={'passed':20,'relocation_bases':2,'scope':'Patched native code with engine stubs; VR playtest still required','checks':['opponent serve assisted','rejected contact retains assist','assist context cleared','accepted player touch consumes','later rally return unassisted','bot reception consumes','own serve unassisted','ended rally unassisted','serve preparation unassisted','other team unassisted','online guard','4v4 preference preserved','global setting does not disable reception-only help','first ally touch sets','second ally touch sets','third ally touch attacks','opponent tactics preserved','serve tactics preserved','bot fields restored','fallback high set reaches teammate']}
(R/'analysis/reception-test-results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
