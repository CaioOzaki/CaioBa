"""Shipped avatar appearance protocol, material offsets and independent choices."""
from pathlib import Path
__file__=str(Path(__file__).with_name('test_identity_rpc_v16.py'))
exec(Path(__file__).read_text().split('\nchecks=[]')[0])
class AvatarEngine(RpcEngine):
 def __init__(self,base):
  super().__init__(base);self.offsets={};self.materials=[self.alloc(),self.alloc()];self.renderer=[self.alloc(),self.alloc()];self.children=[self.alloc(),self.alloc()]
  self.u.mem_map(H+0x100000,0x300000) # Missing fixture hand assets retry bindings across all 81 styles.
  self.rt=self.alloc();self.transforms[self.remote]=self.rt;self.menu=self.alloc();self.mt=self.alloc();self.panel=self.alloc();self.overlay_children={};self.preview={};self.colors={};self.curved_dirty={};self.graphic_dirty={}
  for name in ['CC_FaceLabel','CC_OutfitLabel','CC_FacePreview','CC_OutfitPreview','CC_HandToneLabel','CC_HandToneSwatch']:
   self.overlay_children[name]=self.alloc()
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==ex['avatar_update_trampoline']:self.ret()
  elif r==0xb73890:
   name=self.text[b]
   if a==self.rt and name in ['Physical Head/Visual Head Root/Head','Physical Torso/Scaler (1)/Body']:self.ret(self.children[int(name.startswith('Physical Torso'))])
   elif a==self.mt and name=='CC_Customization':self.ret(self.panel)
   elif a==self.panel:self.ret(self.overlay_children.get(name,0))
   else:self.ret(0)
  elif r==0x94f410:
   self.ret(self.renderer[self.children.index(a)] if a in self.children else a)
  elif r==0xa1ae90:self.ret(self.materials[self.renderer.index(a)])
  elif r==0x9566d0:self.offsets[a]=struct.unpack('<ff',struct.pack('<Q',b));self.ret()
  elif r==0x956610:self.ret()
  elif r==0x94f3d0:self.ret(self.menu if self.text[a]=='Menu' else 0)
  elif r==0x94fb00:self.ret(self.mt if a==self.menu else a)
  elif r==0x832190:self.preview[a]=tuple(struct.unpack('<4f',u.mem_read(b,16)));self.ret()
  elif r==0x7910f0:self.colors[a]=tuple(struct.unpack('<4f',u.mem_read(b,16)));self.ret()
  elif r==0x24bb80:self.curved_dirty[a]=self.curved_dirty.get(a,0)+1;self.ret()
  elif r==0x790530:self.graphic_dirty[a]=self.graphic_dirty.get(a,0)+1;self.ret()
  else:super().hook(u,addr,size,user)
 def press(self,name):
  b=self.alloc();self.names[b]=name;self.call('button_press_hook',b)
cases=0
for base in (0x180000000,0x190000000):
 for fmt in (2,4):
  e=AvatarEngine(base);e.configure(fmt);remote=e.q(e.remote+0x168);old_team=e.team(remote)
  for face in range(9):
   for outfit in range(9):
    packet=0x5c190000|(1-old_team)|(face<<1)|(outfit<<5)
    e.call('client_choose_hook',remote,packet)
    assert e.call('avatar_style_v19',remote)==face+9*outfit and e.team(remote)==old_team
    e.call('avatar_update_hook',e.remote)
    for mat,index in zip(e.materials,(face,outfit)):
     actual=e.offsets[mat];expected=(index%3/3,(2-index//3)/3);assert all(abs(a-b)<1e-6 for a,b in zip(actual,expected)),(fmt,face,outfit,actual)
    cases+=1
  before=e.call('avatar_style_v19',remote)
  for packet in (0x5c190000|(9<<1),0x5c190000|(15<<5),0x5c190000|(0xf<<1),123456789):
   e.call('client_choose_hook',remote,packet);assert e.call('avatar_style_v19',remote)==before and e.team(remote)==old_team
  e.press('CC_CustomizeOpen');assert e.visible[e.panel]
  assert e.colors[e.overlay_children['CC_FacePreview']]==(1,1,1,1)
  e.press('CC_FaceNext');assert e.prefs['Cloudcourt.Face']==1 and e.prefs['Cloudcourt.Outfit']==2
  e.press('CC_OutfitPrev');assert e.prefs['Cloudcourt.Face']==1 and e.prefs['Cloudcourt.Outfit']==1
  assert e.rpc_sends[-1]==(5,0x5c210000|(1<<1)|(1<<5))
  for name,index in [('CC_FacePreview',1),('CC_OutfitPreview',1)]:
   raw=e.overlay_children[name]
   assert e.curved_dirty[raw]==e.graphic_dirty[raw]>=3,'CurvedUI UV cache was not invalidated on every click'
   assert abs(e.preview[raw][0]-index/3)<1e-6
  e.press('CC_HandToneNext');assert e.prefs['Cloudcourt.HandTone.v21']==1
  assert e.rpc_sends[-1]==(5,0x5c210000|(1<<1)|(1<<5)|(1<<10))
  e.press('CC_HandTonePrev');assert e.prefs['Cloudcourt.HandTone.v21']==0
  e.press('CC_CustomizeBack');assert not e.visible[e.panel]
  e.press('CC_FacePrev');assert e.prefs['Cloudcourt.Face']==0 and e.prefs['Cloudcourt.Outfit']==1
  e.press('CC_FacePrev');assert e.prefs['Cloudcourt.Face']==8
  e.press('CC_MapNext');assert e.prefs['Cloudcourt.Map']==1
  e.press('CC_MapNext');assert e.prefs['Cloudcourt.Map']==0
  assert not any(c[0]=='spawn' for c in e.calls)
report={'passed':True,'remote_material_combinations':cases,'formats':[2,4],'ASLR_bases':2,'checks':['nine faces and nine outfits independent','remote material UVs correct','appearance cannot change existing team','malformed style rejected','modal opens without restarting match','preview alpha and UV','separate preferences retained','choice wraps','non-buffered reliable style RPC','host map toggle persists'],'VR_playtest':False}
(R/'analysis/v19-customization-runtime-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
