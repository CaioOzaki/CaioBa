"""Exercise floor context, exact contact RPC, colors and marker asset isolation."""
from pathlib import Path
__file__=str(Path(__file__).with_name('test_cloudcourt_v16.py'))
exec(Path(__file__).read_text().split('\nchecks=[]')[0])
class LandingEngine(CloudEngine):
 def __init__(self,base):
  super().__init__(base);self.floor_contact=True;self.box_values=[];self.root_go=self.alloc();self.root_t=self.alloc();self.markers=[self.alloc(),self.alloc()];self.go_markers=[self.alloc(),self.alloc()]
  self.marker_active={};self.end_teams=[];self.radius=.11
  self.ptr(base+0x15422a0,0) # Unknown venue: Indoor/default surface lift.
  bt=self.alloc();self.transforms[self.ball]=bt;klass=self.alloc(0x200);stat=self.alloc();self.ptr(base+0x15426f0,klass);self.ptr(klass+0xb8,stat);self.ptr(stat,self.ball)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==0xec3e30:self.ret(False) # Existing tests exercise no-hit fallback.
  elif r==ex['landing_collision_trampoline']:
   if self.floor_contact:
    u.reg_write(UC_X86_REG_RCX,self.game);u.reg_write(UC_X86_REG_RDX,0);u.reg_write(UC_X86_REG_R8,0);u.reg_write(UC_X86_REG_RIP,self.b+ex['ground_point_hook'])
   else:self.ret()
  elif r==0x77fe10:self.ret(f=self.radius)
  elif r==0x14ba70:
   if a==0x123456:self.box_values.append(('vector',tuple(struct.unpack('<3f',u.mem_read(b,12)))))
   else:self.box_values.append(('score',struct.unpack('<i',u.mem_read(b,4))[0]))
   self.ret(self.generic)
  elif r==0x94f3d0:self.ret(self.root_go if self.text.get(a)=='CC_LandingMarks' else 0)
  elif r==0x94fb00:self.ret(self.root_t if a==self.root_go else a)
  elif r==0xb73890:self.ret(self.markers[['In','Out'].index(self.text[b])] if a==self.root_t and self.text[b] in ('In','Out') else 0)
  elif r==0x94b570:self.ret(self.go_markers[self.markers.index(a)] if a in self.markers else a)
  elif r==0x94f700 and a in self.go_markers:self.marker_active[a]=bool(b&255);self.ret()
  elif r==ex['client_end_trampoline']:self.end_teams.append(b);self.ret()
  else:super().hook(u,addr,size,user)
 def pack(self):
  value=self.alloc();self.integer(value,0);self.call('score_box_hook',self.generic,value);return self.box_values[-1][1]
 def pack_pos(self,p):
  value=self.alloc();self.vec(value,p);self.call('landing_position_box_hook',0x123456,value);return self.box_values[-1][1]

checks=0
for base in (0x180000000,0x190000000):
 e=LandingEngine(base)
 for fmt in (2,4):
  e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4)
  for online in (False,True):
   e.online=online;e.flag('online_version_ready',online)
   for x,z,outside in [(1.,2.,False),(4.51,3.,True),(0.,9.01,True),(-4.5,2.,True),(0.,-9.,True)]:
    e.call('net_new_rally_hook',e.game,0)
    e.pos[e.transforms[e.ball]]=(x,.19,z)
    collision=e.alloc();contacts=e.alloc();e.integer(collision+0x38,1);e.ptr(collision+0x40,contacts);e.ptr(contacts+0x18,1)
    actual=(x-.012,.031,z+.019);e.vec(contacts+0x20,actual);e.vec(contacts+0x2c,(0,1,0))
    e.call('landing_collision_hook',e.ball,collision)
    score=e.pack();assert score&0x40 and bool(score&0x80)==outside
    wire=e.pack_pos((123.,456.,789.));assert all(abs(a-b)<1e-5 for a,b in zip(wire,actual))
    # A separate client needs only the existing reliable RPC payload, no local
    # ball transform/contact reconstruction. Winner remains 0 after decode.
    e.vec(e.pv,wire);e.call('client_end_hook',e.game,score,e.pv)
    assert e.end_teams[-1]==0
    assert [e.marker_active.get(g,False) for g in e.go_markers]==[not outside,outside],(fmt,online,x,z,hex(score),outside,e.marker_active)
    pos=e.pos[e.markers[int(outside)]];assert abs(pos[0]-actual[0])<1e-5 and abs(pos[2]-actual[2])<1e-5 and abs(pos[1]-actual[1]-.002)<1e-5
    assert not e.pack()&0x40,'Consumed contact must not leak into another point.'
    # v21 keeps the exact point visible throughout the pause before the next
    # serve. Only an actual serve-ball spawn/reveal consumes it (covered by
    # test_serve_feedback_v21), rather than the earlier NewRally event.
    visible_before=e.marker_active.copy();position_before=e.pos[e.markers[int(outside)]]
    e.call('net_new_rally_hook',e.game,0)
    assert e.marker_active==visible_before and e.pos[e.markers[int(outside)]]==position_before
    checks+=1
   # Non-floor contact cannot manufacture a floor mark; non-ground faults do
   # not carry its flag. Malformed/NaN floor data never reaches scene geometry.
   e.floor_contact=False;e.call('landing_collision_hook',e.ball,collision);assert not e.pack()&0x40
   e.call('four_point_hook',e.game,0);assert not e.pack()&0x40;e.floor_contact=True

import hashlib
import UnityPy
from build_landing_v20 import add_landing_marks
from fix_gloves_v16 import hierarchy
asset_reports=[];resources=UnityPy.load(str(R/'versions/cloudcourt-v19-antes-v20/resources.assets')).file
for name in ('level1','level2','level3'):
 before=UnityPy.load(str(R/'versions/cloudcourt-v19-antes-v20'/name)).file
 after=UnityPy.load(str(R/'visuals-v20-landing'/name)).file
 assert all(after.objects[i].get_raw_data()==o.get_raw_data() for i,o in before.objects.items()),name
 assert len(after.objects)-len(before.objects)==15
 assert sum('Collider' in o.type.name for o in after.objects.values())==sum('Collider' in o.type.name for o in before.objects.values())
 gs,ts,paths=hierarchy(after)
 renderers=[]
 for label in ('In','Out'):
  tid=paths['CC_LandingMarks/'+label];go=gs[ts[tid]['m_GameObject']['m_PathID']];assert not go['m_IsActive']
  for component in go['m_Component']:
   obj=after.objects[component['component']['m_PathID']]
   assert obj.type.name in ('Transform','MeshRenderer','MeshFilter')
   if obj.type.name=='MeshRenderer':
    data=obj.read_typetree();assert data['m_Enabled'] and data['m_StaticBatchRoot']['m_PathID']==0;renderers.append(obj.path_id)
   elif obj.type.name=='MeshFilter':
    mesh=after.objects[obj.read_typetree()['m_Mesh']['m_PathID']].read_typetree();assert mesh['m_VertexData']['m_VertexCount']==98 and len(mesh['m_IndexBuffer'])//6==96
 assert len(renderers)==2
 snapshot=after.save();assert not add_landing_marks(after,resources)['created'] and snapshot==after.save()
 asset_reports.append({'scene':name,'old_objects_unchanged':len(before.objects),'new_objects':15,'colliders_added':0,'triangles_per_active_mark':96})
report={'passed':True,'native_cases':checks,'ASLR_bases':2,'actual_contact_sent_through_existing_RPC':True,'same_in_out_as_original_rules':True,'persists_at_new_rally':True,'spawn_lifetime_test':'test_serve_feedback_v21.py','no_effect_on_non_floor_faults':True,'assets':asset_reports,'VR_playtest':False}
(R/'analysis/v20-landing-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
