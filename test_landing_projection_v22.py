"""Execute the shipped x64 ground projection, query ABI and marker lifetime."""
from pathlib import Path
import hashlib,math
__file__=str(Path(__file__).with_name('test_serve_feedback_v21.py'))
exec(Path(__file__).read_text().split('\ncases=[]')[0])

class ProjectionEngine(ServeFeedbackEngine):
 def __init__(self,base):
  super().__init__(base);self.query_hit=True;self.floor=(0.,0.,0.);self.normal=(0.,1.,0.);self.queries=[]
  self.venue_class=self.alloc(0x200);self.venue_static=self.alloc();self.venue=self.alloc()
  self.ptr(base+0x15422a0,self.venue_class);self.ptr(self.venue_class+0xb8,self.venue_static)
  self.out_vector=self.alloc();self.in_vector=self.alloc()
 def set_venue(self,name):
  self.ptr(self.venue_static,self.venue if name is not None else 0)
  if name is not None:self.ptr(self.venue+0x18,self.string(name))
 def hook(self,u,addr,size,user):
  if addr-self.b==0xec3e30:
   origin,direction,hit=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
   sp=u.reg_read(UC_X86_REG_RSP)
   distance=struct.unpack('<f',struct.pack('<I',u.reg_read(UC_X86_REG_XMM3)&0xffffffff))[0]
   mask=self.q(sp+0x28)&0xffffffff;query=self.q(sp+0x30)&0xffffffff
   assert abs(distance-.4)<1e-6 and mask==1 and query==1,(distance,mask,query)
   assert self.vec(direction)==(0.,-1.,0.)
   self.queries.append(dict(origin=self.vec(origin),direction=self.vec(direction),distance=distance,mask=mask,query=query))
   if self.query_hit:self.vec(hit,self.floor);self.vec(hit+12,self.normal)
   self.ret(self.query_hit)
  elif addr-self.b==ex['late_trampoline']:self.ret()
  else:super().hook(u,addr,size,user)
 def project(self,point):
  # Windows x64 Vector3 return uses RCX for hidden return storage, then RDX
  # points to the by-value input. Both are independently allocated here.
  self.vec(self.in_vector,point);self.call('landing_project_v22',self.out_vector,self.in_vector)
  return self.vec(self.out_vector)
 def show(self,point,outside=False):
  self.vec(self.pv,point);self.call('client_end_hook',self.game,0x4346|(0x80 if outside else 0),self.pv)
  assert [self.marker_active.get(g,False) for g in self.go_markers]==[not outside,outside]
  return self.pos[self.markers[int(outside)]]

def close(a,b):return all(abs(x-y)<2e-6 for x,y in zip(a,b))

cases=[]
for base in (0x180000000,0x190000000):
 e=ProjectionEngine(base)
 for venue,lift in ((None,.002),('Indoor',.002),('Beach',.006)):
  e.set_venue(venue);point=(1.125,.031,-2.375)
  # A real floor at y=0 replaces PhysX contact slop; only Y is projected.
  e.floor=(999.,0.,-999.);e.normal=(0.,1.,0.);e.query_hit=True;n=len(e.queries)
  assert close(e.project(point),(point[0],lift,point[2]))
  assert len(e.queries)==n+1 and close(e.queries[-1]['origin'],(point[0],point[1]+.15,point[2]))
  e.query_hit=False;n=len(e.queries)
  assert close(e.project(point),(point[0],point[1]+lift,point[2])) and len(e.queries)==n+1
  e.query_hit=True
  for normal,accepted in [((0.,1.,0.),True),((.1,.99,.1),True),((.8,.6,0.),False),((1.,0.,0.),False),((0.,-1.,0.),False),((0.,.75,0.),False),((0.,.7501,0.),True)]:
   e.normal=normal;e.floor=(0.,0.,0.)
   expected=lift if accepted else point[1]+lift
   assert close(e.project(point),(point[0],expected,point[2])),(venue,normal)
  e.normal=(0.,1.,0.)
  for dy,accepted in [(-.199,True),(.119,True),(-.20,False),(.12,False),(-.21,False),(.13,False),(1.,False),(-1.,False)]:
   e.floor=(0.,dy,0.);p0=(point[0],0.,point[2])
   assert close(e.project(p0),(point[0],(dy if accepted else 0.)+lift,point[2])),(venue,dy)
  for vector_kind in ('floor','normal'):
   for axis in range(3):
    for bad in (float('nan'),float('inf'),-float('inf')):
     v=[0.,0.,0.] if vector_kind=='floor' else [0.,1.,0.];v[axis]=bad
     e.floor=(0.,0.,0.);e.normal=(0.,1.,0.);setattr(e,vector_kind,tuple(v))
     assert close(e.project(point),(point[0],point[1]+lift,point[2])),(vector_kind,axis,bad)
  e.floor=(0.,0.,0.);e.normal=(0.,1.,0.)
  for axis in range(3):
   for bad in (float('nan'),float('inf'),-float('inf')):
    v=list(point);v[axis]=bad;n=len(e.queries);out=e.project(v)
    assert len(e.queries)==n,'invalid input issued a physics query'
    assert all((math.isnan(x) and math.isnan(y)) or x==y or (math.isfinite(x) and math.isfinite(y) and abs(x-y)<2e-6) for x,y in zip(v,out))
  cases.append((hex(base),venue or 'unknown','projection, finite guards, normal/range guards, query ABI'))
 # Exercise the actual marker path for both colors, formats and online modes.
 e=ProjectionEngine(base);e.set_venue('Indoor')
 for fmt in (2,4):
  for online in (False,True):
   e.online_mode(online)
   e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4)
   for outside in (False,True):
    point=(4.9 if outside else 1.125,.031,-2.375);n=len(e.queries)
    result=e.show(point,outside);assert close(result,(point[0],.002,point[2])) and len(e.queries)==n+1
    e.call('net_new_rally_hook',e.game,0)
    for _ in range(5):
     e.call('late_hook',e.ball);assert e.marked() and len(e.queries)==n+1
    for _ in range(5):
     e.motion(context=2);assert e.marked() and len(e.queries)==n+1
    assert e.pos[e.markers[int(outside)]]==result
    e.motion();assert not e.marked() and len(e.queries)==n+1,'actual serve spawn must clear without reprojection'
    for _ in range(3):e.motion()
    assert len(e.queries)==n+1
   cases.append((hex(base),fmt,online,'in/out colors and x/z, one query per point, lifetime until actual spawn'))

report=dict(passed=True,cases=cases,bases=2,actual_integrated_dll=True,sha256=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest(),checks=['Windows x64 hidden Vector3 return and by-value query ABI','ray origin contact+15cm, downward40cm, default solid mask1, Ignore triggers1','Indoor/default2mm; Beach6mm accounts for4mm dry surface','positive projection removes contact slop','x/z and in/out color unchanged','slopes/walls/downward normals rejected','non-finite hit/input rejected','strict safe vertical window(-.20,.12)','one query per point and none per frame','marker persists at NewRally and clears only on actual serve spawn'],scope='Actual compiled native hooks with deterministic Unity/Photon stubs; no headset or two-PC claim.')
(R/'analysis/v22-landing-projection-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

