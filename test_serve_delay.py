exec(open(__file__.replace('test_serve_delay.py','test_2v2.py')).read().split('def run(base):')[0])
class ServeEngine(Engine):
 def __init__(self,base):
  super().__init__(base);self.human=False;self.waits=[];self.resumes=[]
  self.ptr(base+0x1514f48,self.klass)
  self.routine=self.alloc();self.ptr(self.routine+0x20,self.game);self.integer(self.routine+0x28,1);self.integer(self.game+0x90,1)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a=u.reg_read(UC_X86_REG_RCX)
  if r==0x253580:self.ret(self.bot if self.human else 0)
  elif r==0x1c22e0:assert a==self.klass;self.ret(self.alloc())
  elif r==0xb7b820:self.waits.append(struct.unpack('<f',struct.pack('<I',u.reg_read(UC_X86_REG_XMM1)&0xffffffff))[0]);self.ret()
  elif r==ex['serve_routine_trampoline']:self.resumes.append(struct.unpack('<i',u.mem_read(a+0x10,4))[0]);self.integer(a+0x10,4);self.ret(0)
  else:super().hook(u,addr,size,user)
def check(base):
 for doubles in (0,1):
  for state in (1,2):
   e=ServeEngine(base);e.flag('doubles_enabled',doubles);e.integer(e.routine+0x10,state)
   assert (e.call('serve_routine_hook',e.routine)&255)==1
   assert e.waits==[3] and e.resumes==[] and e.q(e.routine+0x18)!=0
   assert (e.call('serve_routine_hook',e.routine)&255)==0
   assert e.waits==[3] and e.resumes==[state]
  e=ServeEngine(base);e.flag('doubles_enabled',doubles);e.integer(e.routine+0x10,1);e.integer(e.game+0x90,0)
  e.call('serve_routine_hook',e.routine);assert not e.waits and e.resumes==[1],'Must allow rotation before new delay'
  for state in (0,3,4,-1):
   e=ServeEngine(base);e.integer(e.routine+0x10,state);e.call('serve_routine_hook',e.routine);assert not e.waits and e.resumes==[state]
  for reason in ('human','bomb'):
   e=ServeEngine(base);e.integer(e.routine+0x10,2)
   if reason=='human':e.human=True
   else:e.u.mem_write(e.game+0x68,b'\1')
   e.call('serve_routine_hook',e.routine);assert not e.waits and e.resumes==[2]
check(0x180000000);check(0x190000000)
report={'passed':True,'delay_seconds':3,'formats':['2v2','4v4'],'bases':2,'checks':['delay after rotation','delay on repeated serve','exactly once per serve','no spawn during wait','correct original continuation','human serve unchanged','bomb unchanged','other coroutine states unchanged'],'scope':'Native code emulation with Unity stubs; VR timing requires playtest'}
(R/'analysis/serve-delay-test-results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

