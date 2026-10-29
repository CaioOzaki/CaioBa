"""Actual x64 ball material hook: atlas ABI, clones, cache and reset lifecycle."""
from pathlib import Path
import hashlib
THIS=Path(__file__);R=THIS.parent
__file__=str(R/'test_2v2.py')
exec(Path(__file__).read_text().split('\ndef run(base):')[0])

class BallStyleEngineV26(Engine):
 def __init__(self,base):
  self.dead=set();self.children={};self.renderers={};self.assigned={};self.original={};self.instance=set();self.clones=[];self.destroyed=[];self.offsets=[];self.enabled={};self.finds=0;self.reads=0;self.assigns=[];self.api=[]
  super().__init__(base)
  self.envklass=self.alloc(0x200);self.envstat=self.alloc();self.ptr(base+0x15422a0,self.envklass);self.ptr(self.envklass+0xb8,self.envstat)
 def string(self,s):
  v=self.alloc(0x400);self.text[v]=s;self.integer(v+0x10,len(s));self.u.mem_write(v+0x14,s.encode('utf-16le'));return v
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==0xa0bfb0:self.ret(a!=0 and a not in self.dead)
  elif r==0xb73890:self.finds+=1;self.ret(self.children.get((a,self.text[b]),0))
  elif r==0x94f410:self.ret(self.renderers.get(a,0))
  elif r==0xa1af10:
   assert a not in self.dead;self.reads+=1;self.ret(self.assigned[a])
  elif r==0xa1ae90:
   assert a not in self.dead;self.reads+=1;material=self.assigned[a]
   if material in self.dead:self.ret(0)
   elif material in self.instance:self.ret(material)
   else:
    clone=self.alloc();self.instance.add(clone);self.clones.append((a,clone,material));self.assigned[a]=clone;self.ret(clone)
  elif r==0xa1b0e0:
   assert a not in self.dead and b not in self.dead;self.assigned[a]=b;self.assigns.append((a,b));self.ret()
  elif r==0xa0ab40:
   assert a in self.instance and a not in self.destroyed,'destroyed shared asset or duplicate clone'
   # A live renderer must no longer reference a material being destroyed.
   assert all(renderer in self.dead or material!=a for renderer,material in self.assigned.items()),'live renderer retained destroyed material'
   self.destroyed.append(a);self.dead.add(a);self.ret()
  elif r==0xa1b2f0:
   assert a not in self.dead;self.enabled[a]=bool(b);self.ret()
  elif r==0xa1b1e0:self.ret(self.enabled.get(a,False))
  elif r in (0x9558b0,0x956610,0x9550e0,0x955090,0x956900):
   assert a in self.instance and a not in self.dead;self.ret()
  elif r==0x9566d0:
   assert a in self.instance and a not in self.dead
   # Vector2 is 8 bytes and passes by value in RDX on Windows x64. Passing
   # a property string here produces non-atlas offsets and fails this check.
   offset=struct.unpack('<2f',struct.pack('<Q',b));assert offset in ((0.,0.),(.5,0.)),('Vector2 ABI',offset)
   assert c==0,'MethodInfo register wrong';self.offsets.append((a,offset));self.ret()
  elif r==ex['lobby_enter_trampoline']:self.ret()
  else:super().hook(u,addr,size,user)
 def venue(self,name=None):
  if name is None:self.ptr(self.envstat,0);return 0
  env=self.alloc();self.ptr(env+0x18,self.string(name));self.ptr(self.envstat,env);return env
 def ball(self,ready=True):
  ball=self.alloc();t=self.alloc();self.transforms[ball]=t;self.ptr(ball+0x38,t)
  dedicated=self.alloc();regular=self.alloc();renderer=self.alloc();fallback=self.alloc();shared=self.alloc()
  self.children[t,'VisualVolleyball/RegularMesh']=regular;self.renderers[regular]=fallback
  self.children[t,'RegularMesh']=regular
  if ready:self.children[t,'VisualVolleyball/RegularMesh/DavidVolleyball']=dedicated
  if ready:self.children[t,'RegularMesh/DavidVolleyball']=dedicated
  self.renderers[dedicated]=renderer;self.assigned[renderer]=shared;self.original[renderer]=shared
  return dict(ball=ball,t=t,dedicated=dedicated,regular=regular,renderer=renderer,fallback=fallback,shared=shared)
 def ready(self,rec):self.children[rec['t'],'VisualVolleyball/RegularMesh/DavidVolleyball']=rec['dedicated'];self.children[rec['t'],'RegularMesh/DavidVolleyball']=rec['dedicated']
 def apply(self,rec):self.call('ball_appearance_v26',rec['ball'])
 def destroyball(self,rec):
  for key in ('ball','t','dedicated','regular','renderer','fallback'):self.dead.add(rec[key])
 def snapshot(self):return(self.finds,self.reads,len(self.clones),len(self.offsets),len(self.assigns),len(self.destroyed),dict(self.roots))

def run():
 start=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest();cases=[]
 for base in (0x180000000,0x190000000):
  for peer in range(2):
   e=BallStyleEngineV26(base);e.online=bool(peer)
   first=e.ball();e.venue();e.apply(first);assert not e.clones and not e.offsets
   e.venue('Indoor');e.apply(first);assert e.offsets[-1][1]==(0.,0.)
   assert e.assigned[first['renderer']]!=first['shared'] and e.enabled[first['renderer']] and not e.enabled[first['fallback']]
   balls=[first]+[e.ball() for _ in range(7)]
   for rec in balls[1:]:e.apply(rec)
   assert len(e.clones)==8 and len({x[1] for x in e.clones})==8
   warm=e.snapshot()
   for _ in range(40):
    for rec in balls:e.apply(rec)
   assert e.snapshot()==warm,'warm frame performed Find/material/offset/root writes'
   for name,expected in [('Beach Day',.5),('Beach Night',.5),('Indoor Practice',0.)]:
    e.venue(name);before=len(e.offsets)
    for rec in balls:e.apply(rec)
    assert len(e.offsets)==before+8 and all(v==(expected,0.) for m,v in e.offsets[-8:])
    assert len(e.clones)==8
   ninth=e.ball();before=e.snapshot();e.apply(ninth);assert e.snapshot()==before,'exceeded bounded eight-ball cache'
   e.destroyball(first);e.apply(ninth);assert len(e.clones)==9 and len(e.destroyed)==1
   # Match/menu reset on live balls restores original shared materials first.
   before_roots=len(e.roots);e.call('lobby_enter_hook',e.page,0)
   assert len(e.destroyed)==9 and all(rec['renderer'] in e.dead or e.assigned[rec['renderer']]==rec['shared'] for rec in balls+[ninth])
   assert len(e.roots)<before_roots,'reset retained material/ball/environment roots'
   e.apply(ninth);assert len(e.clones)==10 and e.assigned[ninth['renderer']] in e.instance
   e.call('lobby_enter_hook',e.page,0);assert len(e.destroyed)==10
   late=e.ball(False);e.apply(late);clones=len(e.clones);finds=e.finds;e.ready(late)
   for _ in range(29):e.apply(late)
   assert len(e.clones)==clones and e.finds==finds,'missing renderer retry was not bounded'
   e.apply(late);assert len(e.clones)==clones+1 and e.offsets[-1][1]==(0.,0.)
   vanished=e.assigned[late['renderer']];e.dead.add(vanished);e.apply(late)
   assert len(e.clones)==clones+2 and e.assigned[late['renderer']]!=vanished,'destroyed instance was not rebound from shared material'
   e.venue();warm=e.snapshot();e.apply(late);assert e.snapshot()==warm,'missing environment touched cached art'
   e.venue('Beach Day');e.apply(late);assert e.offsets[-1][1]==(.5,0.)
   e.call('lobby_enter_hook',e.page,0)
   assert len(e.destroyed)+1==len(e.clones) and not (set(e.original.values())&set(e.destroyed))
   cases.append([hex(base),peer,'atlas ABI; eight-ball bound; stable cache; reset/rebind; late-ready'])
 assert hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest()==start
 result=dict(passed=True,actual_integrated_dll=True,dll_unchanged_during_test=True,sha256=start,cases=cases,checks=['Vector2 by value RDX and null MethodInfo','indoor/beach day/beach night/practice atlas half','unique renderer material clones; shared assets untouched','eight live ball cache capacity and dead slot reuse','warm 40-frame cache has no Find/material/offset/root writes','live reset restores original material before clone destruction','cached ball rebind after reset','missing environment and late renderer ready retry'],scope='Actual main native DLL executed in Unicorn with faithful material ownership/API stubs; no live GPU/VR claim')
 (R/'analysis/v26-ball-style-integrated-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
