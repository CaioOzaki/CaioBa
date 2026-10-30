"""Execute actual native Awake/Detach/MakeSolid/Transparent and ball art code.

The former test invented an attached hierarchy. This regression executes the
original game method that detaches it, for both prefab identities and peers.
"""
from pathlib import Path
import os,hashlib
R=Path(__file__).resolve().parent
scope=dict(__file__=str(R/'test_ball_style_integrated_v26.py'))
source=(R/'test_ball_style_integrated_v26.py').read_text().split('\ndef run():')[0]
exec(source,scope)
globals().update({n:scope[n] for n in ('BallStyleEngineV26','ex','pefile','json','struct','UC_X86_REG_RCX','UC_X86_REG_RDX','UC_X86_REG_R8')})
fixture=Path(os.environ.get('BALL_V28_FIXTURE',R))
scope['p']=pefile.PE(str(fixture/'working/GameAssembly.dll'))
ex.clear();ex.update(json.loads((fixture/'analysis/native-patch-manifest.json').read_text())['exports'])

class SpawnEngine(BallStyleEngineV26):
 def __init__(self,b):
  self.native_renderers=set();self.native_reads=0;self.floats={};self.keywords={};self.alpha={};self.queues={};self.parents={};self.render_writes=[];self.native_awakes=0
  super().__init__(b)
  self.vklass=self.alloc(0x200);self.vstat=self.alloc();self.ptr(b+0x15426f0,self.vklass);self.ptr(self.vklass+0xb8,self.vstat)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==0xa1af10 and a in self.native_renderers:self.native_reads+=1;self.ret(self.assigned[a])
  elif r==0xa1b1e0:self.ret(self.enabled.get(a,False))
  elif r==0xa1b2f0:self.enabled[a]=bool(b);self.render_writes.append((a,bool(b)));self.ret()
  elif r==0x9558b0:
   from unicorn.x86_const import UC_X86_REG_XMM2
   self.floats[a,self.text[b]]=struct.unpack('<f',struct.pack('<I',u.reg_read(UC_X86_REG_XMM2)&0xffffffff))[0];self.ret()
  elif r==0x956610:self.alpha[a]=struct.unpack('<4f',u.mem_read(b,16));self.ret()
  elif r in (0x9550e0,0x955090):
   keywords=self.keywords.setdefault(a,set());(keywords.add if r==0x9550e0 else keywords.discard)(self.text[b]);self.ret()
  elif r==0x956900:self.queues[a]=b&0xffffffff;self.ret()
  elif r==0xa1b090:self.assigned[a]=self.q(b+0x20);self.ret()
  elif r==0x1c21b0:self.ret()
  elif r==0x1c22e0:self.ret(self.alloc())
  elif r==0x94f8d0:self.transforms[a]=self.alloc();self.ret()
  elif r==0x94fb00:self.ret(self.transforms[a])
  elif r==0x2d0180:self.ret(self.alloc())
  elif r==0x2cffd0:self.ret(self.alloc())
  elif r==0xec58c0:self.ret(2)
  elif r==0xec23c0:self.ret()
  elif r==0xb755b0:
   self.parents[a]=b
   for rec in self.records:
    if a==rec['visual']:
     for path in ('VisualVolleyball/RegularMesh','VisualVolleyball/RegularMesh/DavidVolleyball'):self.children.pop((rec['t'],path),None)
   self.ret()
  else:super().hook(u,addr,size,user)
 def ball(self,ready=True):
  rec=super().ball(ready);visual=self.alloc();local=self.alloc();self.transforms[local]=self.alloc()
  rec.update(visual=visual,local=local);self.ptr(rec['ball']+0x38,visual);self.ptr(rec['ball']+0x30,local)
  self.ptr(rec['ball']+0x40,rec['fallback']);self.native_renderers.add(rec['fallback']);self.assigned[rec['fallback']]=self.alloc();self.enabled[rec['fallback']]=False;self.enabled[rec['renderer']]=True
  self.children[visual,'RegularMesh']=rec['regular']
  if ready:self.children[visual,'RegularMesh/DavidVolleyball']=rec['dedicated']
  default=self.alloc();frozen=self.alloc();self.integer(default+0x18,1);self.integer(frozen+0x18,1);self.ptr(default+0x20,self.assigned[rec['fallback']]);self.ptr(frozen+0x20,self.alloc());self.ptr(rec['ball']+0x18,default);self.ptr(rec['ball']+0x20,frozen)
  self.ptr(rec['ball']+0x60,self.alloc());self.ptr(rec['ball']+0x80,self.alloc())
  if not hasattr(self,'records'):self.records=[]
  self.records.append(rec);return rec
 def ready(self,rec):self.children[rec['visual'],'RegularMesh/DavidVolleyball']=rec['dedicated']
 def rva(self,addr,*args):
  ex['_ball_test_rva']=addr
  try:return self.call('_ball_test_rva',*args)
  finally:ex.pop('_ball_test_rva')

def run():
 dll=fixture/'working/GameAssembly.dll';start=hashlib.sha256(dll.read_bytes()).hexdigest();rows=[]
 for base in (0x180000000,0x190000000):
  for peer in ('offline','master','remote'):
   for prefab in ('Volleyball','VolleyballBomb'):
    e=SpawnEngine(base);e.online=peer!='offline';e.venue('Indoor');rec=e.ball();ball=rec['ball']
    assert e.children.get((rec['t'],'VisualVolleyball/RegularMesh/DavidVolleyball'))
    # Execute native Awake, including both Transform.set_parent calls.
    e.call('lobby_ball_awake_trampoline',ball,0)
    assert rec['visual'] in e.parents and not e.children.get((rec['t'],'VisualVolleyball/RegularMesh/DavidVolleyball'))
    fields=bytes(e.u.mem_read(ball+0x18,0x70));e.apply(rec)
    assert len(e.clones)==1 and not e.enabled[rec['fallback']] and e.enabled[rec['renderer']]
    material=e.assigned[rec['renderer']];assert e.offsets[-1]==(material,(0.,0.))
    warm=e.snapshot();writes=len(e.render_writes);next_alloc=e.next
    for _ in range(50):e.apply(rec)
    assert e.snapshot()==warm and len(e.render_writes)==writes and e.next==next_alloc,'warm frame allocated, searched or wrote state'
    e.enabled[rec['fallback']]=True;e.enabled[rec['renderer']]=False;e.apply(rec)
    assert not e.enabled[rec['fallback']] and e.enabled[rec['renderer']]
    # Execute the actual native material swaps, not a boolean invented by test.
    e.rva(0x77ee60,ball,0);e.apply(rec)
    assert e.floats[material,'_Mode']==3 and e.floats[material,'_DstBlend']==10 and e.alpha[material][3]<.53
    assert '_ALPHAPREMULTIPLY_ON' in e.keywords[material] and e.queues[material]==3000
    e.rva(0x77ee30,ball,0);e.apply(rec)
    assert e.floats[material,'_Mode']==0 and e.alpha[material][3]==1 and not e.keywords[material]
    assert bytes(e.u.mem_read(ball+0x18,0x70))==fields,'changed native serialized fields/Bomb references'
    e.rva(0x77e340,ball,0);e.apply(rec);assert len(e.clones)==1,'second detach lost cached art'
    for venue,offset in [('Beach Day',.5),('Beach Night',.5),('Indoor Practice',0)]:
     e.venue(venue);e.apply(rec);assert e.offsets[-1]==(material,(offset,0))
    e.call('lobby_enter_hook',e.page,0);assert e.destroyed==[material] and e.assigned[rec['renderer']]==rec['shared']
    rows.append(dict(base=hex(base),peer=peer,prefab=prefab,native_awake_detached=True,native_solid_transparent_mirrored=True,no_warm_allocations=True))
 assert hashlib.sha256(dll.read_bytes()).hexdigest()==start
 result=dict(passed=True,actual_integrated_dll=True,fixture=str(fixture),sha256=start,cases=rows,scope='Native x64 executed in Unicorn with Unity API stubs; actual original Awake/Detach/MakeSolid/MakeTransparent; Unity GPU probe reported separately')
 (R/'analysis/v28-ball-spawn-integrated-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
