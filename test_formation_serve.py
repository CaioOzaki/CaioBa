"""Compiled hooks: role rotation, tactical receivers and either-hand serve."""
exec(open(__file__.replace('test_formation_serve.py','test_2v2.py')).read().split('def run(base):')[0])
class FormationEngine(Engine):
 def __init__(self,base):
  super().__init__(base);self.ids={};self.members=[];self.render={};self.assessed=[];self.tactics=[];self.grab=False;self.parents={};self.local_hands=set()
  self.ptr(base+0x1519208,self.klass)
  self.player=self.alloc();self.integer(self.player+0x28,0)
  self.call('game_go_hook',self.game)
  for team in range(2):
   members=[]
   for i,area in enumerate(self.areas[team]):
    obj=self.player if team==0 and i==1 else self.alloc()
    self.ptr(obj+0x20,area);self.integer(obj+0x28,team);self.ids[obj]=10*team+i+1
    self.flt(obj+0x3c,2);self.flt(obj+0x44,2);self.flt(obj+0x4c,.5);self.flt(obj+0x50,.2);self.integer(obj+0xa4,1)
    t=self.alloc();self.transforms[obj]=t;self.pos[t]=self.pos[self.transforms[area]];members.append(obj)
   self.members.append(members)
   for offset,items in ((0x28,members),(0x30,[x for x in members if x!=self.player]),(0x38,[x for x in members if x==self.player])):
    lst=self.alloc();arr=self.alloc();self.ptr(self.teams[team]+offset,lst);self.ptr(lst+0x10,arr);self.integer(lst+0x18,len(items))
    for i,obj in enumerate(items):self.ptr(arr+0x20+i*8,obj)
  self.call('add_player_hook',self.teams[0],self.player,1)
  self.u.mem_write(self.game+0x78,b'\1\0');self.integer(self.game+0x7c,1)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==ex['team_update_trampoline']:
   for row in self.members:
    for obj in row:self.u.mem_write(obj+0x70,b'\1')
   self.ret()
  elif r==ex['bot_assess_trampoline']:self.assessed.append(self.u.mem_read(a+0x38,1)[0]);self.integer(a+0xa4,1);self.ret()
  elif r==ex['bot_hit_trampoline']:self.tactics.append((struct.unpack('<i',u.mem_read(a+0xa4,4))[0],self.flt(a+0x4c)));self.ret()
  elif r==ex['local_serve_trampoline']:self.integer(a+0x10,1);self.ret(1)
  elif r==ex['hand_find_trampoline']:self.ret(0)
  elif r==10597104:self.render[a]=bool(b);self.ret()
  elif r==0x30cb70:self.ret(self.ids[a])
  elif r==0x270680:self.ret(self.target)
  elif r==0x1c21b0:self.ret()
  elif r==0x3130b0:self.ret(self.grab)
  elif r==0xa0c080:self.ret(a!=b)
  elif r==0xa0be40:self.ret(a==b)
  elif r==12008720:self.ret(a in self.local_hands);
  elif r==0xb755b0:self.parents[a]=b;self.ret()
  elif addr==H+0xfb000:self.u.mem_write(a+0xd0,b'\0');self.ret()
  else:super().hook(u,addr,size,user)
 def used(self,team,n,last=0):self.integer(self.game+0x7c,team);self.integer(self.game+0x9c,n);self.integer(self.game+0x98,last)

def run(base):
 e=FormationEngine(base)
 for team in range(2):
  for i,area in enumerate(e.areas[team]):
   role=(i-2)%4;p=e.pos[e.transforms[area]]
   assert p[0]==(-3 if role==1 else 3 if role==3 else 0)
   assert p[2]==(1 if team else -1)*(7 if role==0 else 1.5 if role==2 else 4)
   assert e.u.mem_read(area+0x39,1)==bytes([role==0])
  bot=e.members[team][2]
  e.call('bot_body_hook',bot);assert abs(e.calls[-1][1]-(3.2 if team==0 else 2.8))<1e-5 and e.flt(bot+0x3c)==2
  e.ptr(bot+0x20,e.areas[team][3]);e.call('bot_body_hook',bot);assert abs(e.calls[-1][1]-(3.2 if team==0 else 2.8))<1e-5
  e.ptr(bot+0x20,e.areas[team][2])
  # First bot touch targets setter; setter alone approaches the second.
  e.used(1-team,1);e.call('bot_hit_hook',bot,0);assert e.tactics[-1][0]==2 and e.tactics[-1][1]>1
  e.call('pass_target_hook',bot);point=e.vec(e.target+0x10)
  setter=e.members[team][0];sp=e.pos[e.transforms[setter]]
  assert abs(point[0])<1e-5 and abs(abs(point[2])-.85)<1e-5
  e.used(team,1,e.ids[bot]);e.call('team_update_hook',e.teams[team])
  for obj in e.members[team]:
   if obj!=e.player:assert e.u.mem_read(obj+0x70,1)==bytes([obj==setter])
  # Second touch targets a wing; third is not forced into another pass.
  e.call('pass_target_hook',setter);point=e.vec(e.target+0x10);assert abs(abs(point[0])-2.65)<1e-5 and abs(abs(point[2])-1.15)<1e-5
  e.call('bot_hit_hook',setter,0);assert e.tactics[-1][0]==2
  e.used(team,2,e.ids[setter]);e.call('team_update_hook',e.teams[team])
  e.call('bot_hit_hook',bot,0);assert e.tactics[-1][0]==1
 # All quartet roles now share doubles movement speed.
 e.ptr(e.player+0x20,e.areas[0][2]);e.call('player_speed_hook')
 speed=struct.unpack('<f',struct.pack('<I',e.u.reg_read(UC_X86_REG_XMM0)&0xffffffff))[0];assert abs(speed-2.4)<1e-5
 e.ptr(e.player+0x20,e.areas[0][1]);e.call('player_speed_hook')
 speed=struct.unpack('<f',struct.pack('<I',e.u.reg_read(UC_X86_REG_XMM0)&0xffffffff))[0];assert abs(speed-2.4)<1e-5
 # Doubles ally won't block; can still jump to attack its own team's set.
 e.flag('quartet_enabled',0);e.flag('doubles_enabled',1);bot=e.members[0][2];e.u.mem_write(bot+0x38,b'\1')
 e.used(1,2);e.call('bot_assess_hook',bot);assert e.assessed[-1]==0 and struct.unpack('<i',e.u.mem_read(bot+0xa4,4))[0]==2
 e.used(0,2);e.call('bot_assess_hook',bot);assert e.assessed[-1]==1 and struct.unpack('<i',e.u.mem_read(bot+0xa4,4))[0]==1
 # Both hands can retrieve frozen hidden ball from anywhere, only once.
 for right,fmt in ((0,2),(1,2),(0,4),(1,4)):
  e.flag('online_format',fmt)
  e.online=bool(right);e.flag('online_version_ready',right)
  ball=e.alloc(0x200);renderer=e.alloc();bt=e.alloc();e.ptr(ball+0x40,renderer);e.transforms[ball]=bt;e.pos[bt]=(0,1,-10)
  e.u.mem_write(ball+0x89,b'\1');e.u.mem_write(e.game+0x7a,b'\1')
  routine=e.alloc();closure=e.alloc();e.ptr(routine+0x28,closure);e.ptr(closure+0x10,ball)
  v=e.alloc();e.vec(v,(0,1,-10));e.call('hand_serve_position_hook',bt,v);assert e.pos[bt]==(0,-100,0)
  e.call('local_serve_hook',routine);assert e.render[renderer] is False
  hand=e.alloc();center=e.alloc();e.ptr(hand+0x18,center);e.pos[center]=(3 if right else -3,1.2,-11);e.u.mem_write(hand+0x24,bytes([right]))
  # Run the ORIGINAL Hand.Update and ORIGINAL StartInteraction through
  # the patched FindClosestInteractable call, not just the helper alone.
  e.transforms[hand]=center;klass=e.alloc(0x200);e.ptr(ball,klass)
  if right:
   nk=e.alloc(0x200);st=e.alloc();body=e.alloc(0x200);body_t=e.alloc()
   e.ptr(e.b+0x1542650,nk);e.ptr(nk+0xb8,st);e.ptr(st,e.player);e.ptr(e.player+0x80,body);e.transforms[body]=body_t
   e.local_hands.add(center)
   remote=e.alloc();rt=e.alloc();e.transforms[remote]=rt;e.ptr(remote+0x18,rt);e.pos[rt]=(9,2,9)
   assert e.call('hand_find_hook',remote)==0 and not e.render[renderer]

  e.ptr(klass+0x190,e.b+0x77f660);e.ptr(klass+0x1a0,H+0xfb000)
  ex['hand_update_native']=0x312f60
  e.grab=False;e.call('hand_update_native',hand);assert not e.render[renderer] and e.q(hand+0x30)==0
  e.grab=True;e.call('hand_update_native',hand)
  assert e.q(hand+0x30)==ball and e.q(ball+0xd8)==hand and e.parents[bt]==center and e.render[renderer]
  assert all(abs(a-b)<1e-5 for a,b in zip(e.pos[bt],e.pos[center]))
  e.call('hand_update_native',hand);assert e.q(hand+0x30)==ball
  e.grab=False;e.call('hand_update_native',hand);assert e.q(hand+0x30)==0
  assert e.call('hand_find_hook',hand)==0
 # Leaving offline modes restores original geometry.
 e.flag('online_version_ready',0);e.online=True;e.call('game_go_hook',e.game)
 for area,t in e.transforms.items():
  if t in e.original_pos:assert e.pos[t]==e.original_pos[t]
for base in (0x180000000,0x190000000):run(base)
report={'passed':True,'bases':2,'checks':['cross on both teams','rear role rotation bot and human','first pass to setter','second pass to wing','receiver selection','third touch attack','2v2 ally receives without block','2v2 ally attack jump preserved','hidden waiting ball','left hand','right hand','no duplicate grab','online geometry restored'],'scope':'Compiled hooks with engine stubs; VR playtest required.'}
(R/'analysis/formation-serve-test-results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
