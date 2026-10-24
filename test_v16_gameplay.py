"""Run compiled v16 boundary, first-contact and set-target decisions."""
from pathlib import Path
source=Path(__file__).with_name('test_volley_riot_v16.py');__file__=str(source)
exec(source.read_text().split('\nfor base in (')[0])
class GameplayEngine(CelebrationEngine):
 def __init__(self,base):
  super().__init__(base);self.assists=[]
 def hook(self,u,addr,size,user):
  r=addr-self.b
  if r==ex['collision_trampoline']:
   sp=u.reg_read(UC_X86_REG_RSP)-0x30;u.reg_write(UC_X86_REG_RSP,sp);self.ptr(sp,H+0xfa000)
   u.reg_write(UC_X86_REG_RCX,0);u.reg_write(UC_X86_REG_RDX,1);u.reg_write(UC_X86_REG_R8,0)
   u.reg_write(UC_X86_REG_RIP,self.b+ex['reception_assist_hook'])
  elif addr==H+0xfa000:
   self.assists.append(u.reg_read(UC_X86_REG_RAX));u.reg_write(UC_X86_REG_RSP,u.reg_read(UC_X86_REG_RSP)+0x28);self.ret()
  else:super().hook(u,addr,size,user)
 def assist(self):self.call('collision_hook',self.body,0,0,0,0);return self.assists[-1]

count=0
for base in (0x180000000,0x190000000):
 e=GameplayEngine(base);e.ptr(e.player+0x80,e.body)
 t=e.transforms[e.player]
 for team in (0,1):
  e.integer(e.player+0x28,team)
  for z in (-2.,-.05,0.,.05,2.):
   for offset in (-.75,0.,.75):
    e.pos[t]=(0,0,z);e.vec(e.body+0xe8,(0,1.8,z+offset));e.call('net_clamp_hook',e.player)
    expected=min(max(z,-10),-.12-offset) if team==0 else max(min(z,10),.12-offset)
    assert abs(e.pos[t][2]-expected)<1e-5,(team,z,offset,e.pos[t],expected);count+=1
 e.online=False
 for fmt in (2,4):
  e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4)
  for team in (0,1):
   e.integer(e.player+0x28,team)
   for last in (0,1):
    for touches in (0,1,2):
     e.u.mem_write(e.game+0x78,b'\1\0');e.integer(e.game+0x7c,last);e.integer(e.game+0x9c,touches)
     assert e.assist()==int(last!=team or touches==0),(fmt,team,last,touches)
     assert e.call('reception_assist_hook',0,1)==0,'context leaked outside collision';count+=1
 e.online=True;e.flag('online_version_ready',1)
 for fmt in (2,4):
  e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4)
  e.call('net_new_rally_hook',e.game,0);assert e.assist()==0
  e.receive(0)
  e.integer(e.player+0x28,1);assert e.assist()==1
  e.integer(e.player+0x28,0);assert e.assist()==0
  e.receive(1);e.integer(e.player+0x28,1);assert e.assist()==0
  e.integer(e.player+0x28,0);assert e.assist()==1
  e.receive(0);assert e.assist()==0;count+=5
 for fmt in (2,4):
  e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4)
  for team in (0,1):
   e.online=False;e.used(team,1);bot=e.members[team][2]
   e.vec(e.target+0x10,(9,1,-4 if team==0 else 4));e.call('pass_target_hook',bot)
   point=e.vec(e.target+0x10)
   assert abs(point[2]-(-.85 if team==0 else .85))<1e-5 and abs(point[1]-1.65)<1e-5 and abs(point[0])<=3.5,point
   count+=1
report={'passed':count,'ASLR_bases':2,'checks':['symmetric tracked-head net clearance','room-scale offset compensation','all first contacts in both formats and teams','no assist leak to later touches','serve exclusion','second bot touch near net'],'limits':'Unity and Photon calls stubbed; gameplay feel requires headset'}
(R/'analysis/v16-gameplay-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
