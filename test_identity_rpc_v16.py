"""Regressions for delayed appearance packets and non-buffered skin RPCs.

Executes the compiled hooks with real Team/List layouts; engine calls are stubs.
"""
from pathlib import Path
__file__=str(Path(__file__).with_name('test_cloudcourt_v16.py'))
exec(Path(__file__).read_text().split('\nchecks=[]')[0])

class RpcEngine(CloudEngine):
 def __init__(self,base):
  super().__init__(base);self.online=True;self.flag('online_version_ready',1)
  self.rpc_sends=[]
  self.ptr(base+0x15260b8,self.alloc());self.ptr(base+0x15269d0,self.alloc())
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c,d=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9)]
  if r==0x1c1f90:
   assert b==1;array=self.alloc();self.ptr(array+0x18,1);self.ret(array)
  elif r==0x14ba70:
   boxed=self.alloc();self.integer(boxed+0x10,struct.unpack('<i',u.mem_read(b,4))[0]);self.ret(boxed)
  elif r==0xe6bb50:
   assert self.text[b]=='Client_ChooseTeam'
   boxed=self.q(d+0x20);value=struct.unpack('<i',u.mem_read(boxed+0x10,4))[0]
   self.rpc_sends.append((c,value));self.selected.append(value)
   u.reg_write(UC_X86_REG_RCX,self.player);u.reg_write(UC_X86_REG_RDX,value);u.reg_write(UC_X86_REG_R8,0)
   u.reg_write(UC_X86_REG_RIP,self.b+ex['client_choose_hook'])
  else:super().hook(u,addr,size,user)
 def team(self,player=None):return struct.unpack('<i',self.u.mem_read((player or self.player)+0x28,4))[0]
 def contains(self,team,offset,value):
  lst=self.q(self.teams[team]+offset);array=self.q(lst+0x10);n=struct.unpack('<i',self.u.mem_read(lst+0x18,4))[0]
  return value in [self.q(array+0x20+8*i) for i in range(n)]
 def configure(self,fmt):
  self.flag('doubles_enabled',fmt==2);self.flag('quartet_enabled',fmt==4);self.flag('online_format',fmt)
  if fmt==2:
   for side,items in ((0,[self.members[0][0],self.player]),(1,self.members[1][:2])):
    for offset,values in ((0x28,items),(0x30,[p for p in items if p!=self.player]),(0x38,[p for p in items if p==self.player])):
     lst=self.q(self.teams[side]+offset);array=self.q(lst+0x10);self.integer(lst+0x18,len(values))
     for i,value in enumerate(values):self.ptr(array+0x20+8*i,value)

checks=[];failures=[]
for base in (0x180000000,0x190000000):
 for fmt in (2,4):
  for name in ('appearance_does_not_change_roster','delayed_appearance_after_swap','unbuffered_ordered_rpc','lobby_assignment','full_target_team'):
   try:
    e=RpcEngine(base);e.configure(fmt)
    if name=='appearance_does_not_change_roster':
     e.call('client_choose_hook',e.player,0x5601|(2<<2))
     assert e.team()==0 and e.contains(0,0x28,e.player) and not e.contains(1,0x28,e.player),'skin packet changed team without roster move'
    elif name=='delayed_appearance_after_swap':
     e.call('net_new_rally_hook',e.game,0)
     e.call('client_choose_hook',e.player,0x5621)
     assert e.team()==0,'team change not deferred'
     e.call('client_end_hook',e.game,0,e.pv)
     assert e.team()==1 and e.contains(1,0x28,e.player),'team swap did not complete'
     assert e.contains(1,0x38,e.player) and not e.contains(0,0x38,e.player),'human roster did not follow swap'
     e.call('client_choose_hook',e.player,0x5600|(3<<2))
     assert e.team()==1 and e.contains(1,0x28,e.player) and not e.contains(0,0x28,e.player),'delayed skin packet detached team field from membership'
    elif name=='unbuffered_ordered_rpc':
     button=e.alloc();e.names[button]='PuloSkin2';e.call('button_press_hook',button)
     assert e.rpc_sends==[(5,0x5c190044)],f'wrong RPC target or payload: {e.rpc_sends}'
    elif name=='lobby_assignment':
     for side in (0,1):e.integer(e.q(e.teams[side]+0x28)+0x18,0)
     e.call('client_choose_hook',e.player,0x5601)
     assert e.team()==1,'lobby choice was lost'
    else:
     e.integer(e.q(e.teams[1]+0x30)+0x18,0)
     e.call('client_choose_hook',e.player,0x5621)
     assert e.team()==0 and e.contains(0,0x28,e.player),'full destination changed membership'
    checks.append({'base':hex(base),'format':fmt,'case':name})
   except Exception as error:failures.append({'base':hex(base),'format':fmt,'case':name,'error':str(error)})
report={'passed':not failures,'checks':checks,'failures':failures,'scope':'Compiled machine code with Unity/Photon stubs; real two-PC validation still required.'}
(R/'analysis/v16-identity-rpc-tests.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
raise SystemExit(bool(failures))
