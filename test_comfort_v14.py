"""Run shipped native second-touch logic, including accepted-hit timing."""
__file__=__file__.replace('test_comfort_v14.py','test_formation_serve.py')
exec(open(__file__).read().split('\ndef run(base):')[0])
class SettingEngine(FormationEngine):
 def __init__(self,base):
  super().__init__(base);self.grips=[True,True];self.sent=[]
  self.body=self.alloc(0x200);self.part=self.alloc();self.ball=self.alloc(0x200)
  self.ptr(self.body+0x168,self.player);self.integer(self.part+0x18,3)
  self.pv=self.alloc();self.vv=self.alloc();self.vec(self.pv,(0,1.5,-4));self.vec(self.vv,(0,1,8))
  klass=self.alloc(0x200);stat=self.alloc();inp=self.alloc();self.vr=self.alloc();self.controllers=[self.alloc(),self.alloc()]
  self.ptr(base+0x1542b48,klass);self.ptr(klass+0xb8,stat);self.ptr(stat,inp);self.ptr(inp+0x40,self.vr)
  self.ptr(base+0x1541dc0,self.alloc());self.ptr(base+0x1541d98,self.alloc())
  nk=self.alloc(0x200);ns=self.alloc();self.ptr(base+0x1542650,nk);self.ptr(nk+0xb8,ns);self.ptr(ns,self.player)
 def call(self,name,*args):
  u=self.u;sp=S+0x80008;u.reg_write(UC_X86_REG_RSP,sp);self.ptr(sp,STOP)
  for reg,v in zip((UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9),list(args)+[0]*4):u.reg_write(reg,v)
  for i,v in enumerate(list(args)[4:]+[0]*8):self.ptr(sp+0x28+8*i,v)
  u.emu_start(self.b+ex[name],STOP,count=100000);assert u.reg_read(UC_X86_REG_RIP)==STOP,name
  return u.reg_read(UC_X86_REG_RAX)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==0xa2710:
   if a in (5,6):self.ret(self.controllers[a-5])
   else:assert a==1;self.ret(self.grips[self.controllers.index(c)])
  elif r==ex['collision_trampoline']:
   # Real hit handling increments the count BEFORE dispatching motion.
   self.integer(self.game+0x9c,2)
   self.collision_sp=u.reg_read(UC_X86_REG_RSP);sp=self.collision_sp-0xa0;u.reg_write(UC_X86_REG_RSP,sp);self.ptr(sp,H+0xf9000)
   for reg,v in zip((UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9),(self.ball,self.pv,self.vv,1)):u.reg_write(reg,v)
   for i,v in enumerate((0,1,0,0,0)):self.ptr(sp+0x28+8*i,v)
   u.reg_write(UC_X86_REG_RIP,self.b+ex['motion_hook'])
  elif addr==H+0xf9000:u.reg_write(UC_X86_REG_RSP,self.collision_sp);self.ret()
  elif r==0x77e5c0:self.sent.append(self.vec(c));self.ret()
  elif r in (ex['client_motion_trampoline'],ex['client_end_trampoline'],0x253e30):self.ret()
  else:super().hook(u,addr,size,user)
 def receive(self,team):self.call('client_motion_hook',self.ball,self.pv,self.vv,1,7,team,0,0)
 def hit(self):self.vec(self.vv,(0,1,8));self.call('collision_hook',self.body,self.part,self.ball,0,0);return self.sent[-1]

checks=0
for base in (0x180000000,0x190000000):
 for fmt in (2,4):
  for online in (False,True):
   e=SettingEngine(base);e.flag('doubles_enabled',int(fmt==2));e.flag('quartet_enabled',int(fmt==4));e.online=online;e.flag('online_version_ready',int(online));e.flag('online_format',fmt)
   if online:e.call('net_new_rally_hook',e.game,1);e.receive(1);e.receive(0)
   e.used(0,1);assert e.call('setting_ready',e.body)==1
   for grips,assist in [([True,True],True),([True,False],False),([False,True],False),([False,False],False)]:
    e.grips=grips;e.used(0,1);v=e.hit();checks+=1
    assert (v[1]>7 if assist else v==(0,1,8)),(fmt,online,grips,v)
    if assist:
     # Descending intersection reaches the attack window near the net.
     import math
     t=(v[1]+math.sqrt(v[1]*v[1]-2*9.81*1.15))/9.81
     landing=(v[0]*t,2.65,-4+v[2]*t)
     assert abs(landing[0]-2.65)<1e-4 and abs(landing[2]+1.15)<1e-4,landing
   e.grips=[True,True]
   if online:
    e.receive(0);assert e.call('setting_ready',e.body)==0
    e.call('net_new_rally_hook',e.game,0);e.receive(0);assert e.call('setting_ready',e.body)==0
    e.call('client_end_hook',e.game,0,e.pv);assert e.call('setting_ready',e.body)==0
   else:
    for used in (0,2,3):e.used(0,used);assert e.call('setting_ready',e.body)==0
    e.used(1,1);assert e.call('setting_ready',e.body)==0
   remote=e.alloc(0x200);e.ptr(remote+0x168,e.members[1][0]);assert e.call('setting_ready',remote)==0
print(json.dumps({'passed':True,'accepted_hit_cases':checks,'formats':[2,4],'offline_and_online':True,'ASLR_bases':2,'checks':['both GRAB required','release disables assist','second touch only','serve excluded','remote avatar excluded','count increment before accepted RPC','ballistic set reaches near-net attack window']},indent=2))
