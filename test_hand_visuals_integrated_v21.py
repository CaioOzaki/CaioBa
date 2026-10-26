"""Actual v21 remote hand visuals, per-player tone/pose caches and late binding."""
from pathlib import Path
import hashlib,json,struct
__file__=str(Path(__file__).with_name('test_cloudcourt_v16.py'))
exec(Path(__file__).read_text().split('\nchecks=[]')[0])
PATHS=['Hand Root L/Open/Cloudcourt Open Glove','Hand Root L/Closed/Cloudcourt Closed Glove','Hand Root R/Open/Cloudcourt Open Glove','Hand Root R/Closed/Cloudcourt Closed Glove','Hand Root L/CC_ThumbsUp','Hand Root R/CC_ThumbsUp','Hand Root L/CC_SettingOpen','Hand Root R/CC_SettingOpen']
COLORS=[(1.,.85,.74,1.),(.91,.69,.49,1.),(.76,.49,.29,1.),(.58,.32,.17,1.),(.36,.18,.10,1.),(.19,.085,.05,1.)]
class HandEngine(CloudEngine):
 def __init__(self,base):
  self.finds=0;self.material_reads=0;self.active_writes=0;self.color_writes=0;self.children={};self.renderers={};self.materials={};self.colors={};self.unready=set()
  super().__init__(base);self.online=True;self.flag('online_version_ready',1)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX)]
  if r==0xb73890 and (a,self.text.get(b)) in self.children:self.finds+=1;self.ret(self.children[a,self.text[b]])
  elif r==0x94f410 and a in self.renderers:assert self.text[b]=='MeshRenderer';self.ret(self.renderers[a])
  elif r==0xa1ae90 and a in self.materials:self.material_reads+=1;self.ret(0 if a in self.unready else self.materials[a])
  elif r==0x956610:self.color_writes+=1;self.colors[a]=struct.unpack('<4f',u.mem_read(b,16));self.ret()
  elif r==0x94f700 and a in self.renderers:self.active_writes+=1;self.visible[a]=bool(b);self.ret()
  else:super().hook(u,addr,size,user)
 def make_body(self,player):
  body=self.alloc(0x200);t=self.alloc();self.transforms[body]=t;self.ptr(body+0x168,player);visuals=[];mats=[]
  for path in PATHS:
   visual=self.alloc();renderer=self.alloc();mat=self.alloc();self.children[t,path]=visual;self.renderers[visual]=renderer;self.materials[renderer]=mat;visuals.append(visual);mats.append(mat)
  return body,visuals,mats
 def packet(self,player,tone,pose):
  team=struct.unpack('<i',self.u.mem_read(player+0x28,4))[0]
  self.call('client_choose_hook',player,0x5c210000|team|(tone<<10)|(pose<<13))
 def counts(self):return self.finds,self.material_reads,self.active_writes,self.color_writes
 def verify(self,visuals,mats,tone,pose):
  expected=[pose not in (1,3,4),pose not in (1,3,4),pose not in (2,3,4),pose not in (2,3,4),pose in (1,3),pose in (2,3),pose==4,pose==4]
  assert [self.visible[v] for v in visuals]==expected,(pose,self.visible)
  assert all(all(abs(a-b)<1e-5 for a,b in zip(self.colors[m],COLORS[tone])) for m in mats)
cases=[]
for base in (0x180000000,0x190000000):
 e=HandEngine(base);players=[e.members[1][0],e.members[1][1]];bodies=[e.make_body(p) for p in players]
 for i,(player,(body,visuals,mats)) in enumerate(zip(players,bodies)):
  e.packet(player,i+2,0);e.call('avatar_hands_v21',body);e.verify(visuals,mats,i+2,0)
 assert e.finds==16 and e.material_reads==16 and e.active_writes==16 and e.color_writes==16
 before=e.counts()
 for _ in range(4):
  for body,_,_ in bodies:e.call('avatar_hands_v21',body)
 assert e.counts()==before,'ready repeated pose/tone frames should not Find/read materials/SetActive/recolor'
 for pose in range(5):
  for i,(player,(body,visuals,mats)) in enumerate(zip(players,bodies)):
   tone=(pose+i)%6;other=i^1;other_visuals=bodies[other][1];snapshot=[e.visible[v] for v in other_visuals]
   e.packet(player,tone,pose);finds=e.finds;e.call('avatar_hands_v21',body)
   e.verify(visuals,mats,tone,pose);assert e.finds==finds and [e.visible[v] for v in other_visuals]==snapshot
   before=e.counts();e.call('avatar_hands_v21',body);assert e.counts()==before
 # A new avatar whose one material is not ready retries that material from its
 # cached visual, avoiding another Find and preserving independent first slots.
 extra=e.alloc();e.integer(extra+0x28,1);body,visuals,mats=e.make_body(extra);renderer=e.renderers[visuals[-1]];e.unready.add(renderer)
 e.packet(extra,5,4);e.call('avatar_hands_v21',body);finds=e.finds;active=e.active_writes
 e.unready.remove(renderer);e.call('avatar_hands_v21',body);e.verify(visuals,mats,5,4)
 assert e.finds==finds and e.active_writes==active and e.material_reads==25
 before=e.counts();e.call('avatar_hands_v21',body);assert e.counts()==before
 cases.append(hex(base))
report=dict(passed=True,actual_integrated_dll=True,sha256=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest(),bases=cases,checks=['two independent player caches','remote synchronized poses0..4 and six tones','8 visuals/materials bind once per player','no Find/material read/SetActive/recolor on unchanged ready frames','pose changes reuse cached visuals','other player stays unchanged','late material retries cached visual then becomes idle'],scope='Actual integrated native DLL with deterministic engine API stubs; visual physics and live headset testing not claimed.')
(R/'analysis/v21-hand-visuals-integrated-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
