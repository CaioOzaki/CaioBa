"""Execute v16 menu/RPC/score hooks with explicit Unity and Photon stubs."""
from pathlib import Path
source=Path(__file__).with_name('test_volley_riot_v16.py')
__file__=str(source)
exec(source.read_text().split('\nfor base in (')[0])

class RiotEngine(CelebrationEngine):
 def __init__(self,base):
  super().__init__(base);self.master=False;self.wire=[];self.rebuilds=0;self.destroyed=[];self.pressed={};self.clones=[];self.anchor={};self.canvas_modes={};self.scales={};self.indoor=True;self.written={}
  self.menu=self.alloc();button=self.alloc();self.ptr(self.menu+0x30,button)
  event=self.alloc();self.ptr(event,self.klass);self.ptr(button+0xf0,event);self.fresh_events=[]
  self.parent=self.alloc();self.attach(button)
  self.online=True;self.flag('online_version_ready',1);self.flag('online_format',2)
  self.score=self.alloc(0x300);self.ptr(self.game+0x30,self.score);self.ptr(self.score+0xc8,self.string('12 - 10'))
  self.attach(self.score);self.score_root=self.alloc()
  self.score_array=self.alloc();self.ptr(self.game+0xa8,self.score_array);self.integer(self.score_array+0x18,2);self.integer(self.score_array+0x20,12);self.integer(self.score_array+0x24,10)
  self.transforms[self.game]=self.alloc();self.pos[self.transforms[self.game]]=(0,0,0)
  bots=self.q(self.teams[1]+0x30);arr=self.q(bots+0x10);self.integer(bots+0x18,3)
  for j,p in enumerate(self.members[1][1:]):self.ptr(arr+0x20+j*8,p)
 def attach(self,obj):
  t=self.alloc();self.transforms[obj]=t;self.pos[t]=(0,0,0)
  child=self.alloc();self.transforms[child]=child;self.parents[t]=self.parent
  label=self.newtext('Resume');self.render[child]=label;self.children=getattr(self,'children',{});self.children[t]=[child]
  return t
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c,d=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9)]
  if r in [ex['riot_menu_trampoline'],ex['riot_score_trampoline']]:self.ret()
  elif r==0xa0b160:
   obj=self.alloc(0x300);self.attach(obj);self.ptr(obj+0xf0,self.q(a+0xf0));self.clones.append(obj);self.ret(obj)
  elif r==0x1c22e0:self.ret(self.alloc())
  elif r==0x40dea0:self.fresh_events.append(a);self.ret()
  elif r==0xb739d0:self.ret(self.parents.get(a,0))
  elif r==0xb74340:self.parents[a]=b;self.ret()
  elif r==0xa16c60:self.anchor[a]=struct.unpack('<ff',struct.pack('<Q',b));self.ret()
  elif r==0xb74800:self.ret(len(self.children.get(a,[])))
  elif r==0xb73930:self.ret(self.children[a][b])
  elif r==0x94f410:self.ret(self.render.get(a,0))
  elif r==0x83c810:self.ret(self.pressed.get(a,False))
  elif r==0x6054c0:self.ret(a)
  elif r==0xe6e1b0:self.ret(self.ids.get(a,1))
  elif r==ex['choose_team_trampoline']:
   self.wire.append((a,b));u.reg_write(UC_X86_REG_RIP,self.b+ex['riot_choose_hook'])
  elif r==ex['riot_choose_trampoline']:self.integer(a+0x28,b);self.ret()
  elif r==0x61f230:self.ret(self.master)
  elif r==0x2527d0:self.rebuilds+=1;self.ret()
  elif r==0x254a00:self.ret()
  elif r==0x60cb40:self.destroyed.append(a);self.ret()
  elif r==0x94f3d0:self.ret(self.score_root if self.indoor else 0)
  elif r==0xece020:self.canvas_modes[a]=b;self.ret()
  elif r==0xb75560:self.scales[a]=self.vec(b);self.ret()
  elif r==0xb75750:self.ret()
  elif r==0x2405f0:self.written[a]=self.text[b];self.ptr(a+0xc8,b);self.ret()
  else:super().hook(u,addr,size,user)

checks=[]
for base in (0x180000000,0x190000000):
 e=RiotEngine(base);e.call('riot_menu_hook',e.menu)
 assert len(e.clones)==2
 assert len(e.fresh_events)==2 and e.q(e.clones[0]+0xf0)!=e.q(e.clones[1]+0xf0)
 change,skin=e.clones
 e.call('riot_menu_hook',e.menu);assert len(e.clones)==2
 assert sorted(round(v[1]) for v in e.anchor.values())==[-93,-55]
 e.pressed[skin]=True;e.call('riot_menu_hook',e.menu);assert len(e.wire)==1 and e.wire[0][1]&0xfffffff0==0x5610
 e.call('riot_menu_hook',e.menu);assert len(e.wire)==1,'held button must not repeat every frame'
 e.pressed[skin]=False;e.call('riot_menu_hook',e.menu)
 e.pressed[change]=True;e.call('riot_menu_hook',e.menu);assert e.wire[-1][1]==0x5621
 assert e.q(e.player+0x28)&0xffffffff==0,'request must not move teams during rally'
 e.master=True;e.call('client_end_hook',e.game,0,e.pv)
 assert e.q(e.player+0x28)&0xffffffff==1 and e.rebuilds==1
 assert len(e.destroyed)==6,'old bots must be removed before rebuilding rosters'
 e.call('riot_score_hook',e.game);scores=e.clones[2:]
 expected='<color=#E74750>12</color>  -  <color=#2468DF>10</color>'
 assert len(scores)==2 and all(e.written[x]==expected for x in scores)
 e.integer(e.player+0x28,1);e.integer(e.score_array+0x20,13);e.call('riot_score_hook',e.game)
 expected=expected.replace('12','13')
 assert len(e.clones)==4 and all(e.written[x]==expected for x in scores)
 assert sorted(e.pos[e.transforms[x]][2] for x in scores)==[-12.350000381469727,12.350000381469727]
 assert all(v==2 for v in e.canvas_modes.values())
 e.online=False;e.call('riot_menu_hook',e.menu);assert not e.visible[change] and not e.visible[skin]
 checks.append(hex(base))
report={'passed':True,'ASLR_bases':checks,'checks':['menu adds exactly two buttons','skin RPC handled without corrupting team field','held button sends once','team move deferred until point','host roster rebuild removes old bots','wall scores mirror live string','world-space canvases on opposite walls','online controls hidden offline'],'limits':'Unity/Photon calls stubbed; live VR and two-PC validation still required'}
(R/'analysis/v16-menu-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
