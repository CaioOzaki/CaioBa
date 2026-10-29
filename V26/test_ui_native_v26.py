"""Read-only integrated SDF material and preview lifecycle regressions."""
from pathlib import Path
import hashlib,json,struct
R=Path(__file__).resolve().parent
source=(R/'test_score_outline_v20.py').read_text()
exec(source.split('\ncases=[]')[0],globals())
class PopupV26(OutlineEngine):
 def __init__(self,b):
  super().__init__(b);self.mats={};self.keywords={};self.supports=True
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==0x23e790:
   if a not in self.mats:self.mats[a]=self.alloc()
   self.ret(self.mats[a])
  elif r==0x955630:
   assert self.text[b]=='_OutlineWidth';self.ret(self.supports)
  elif r==0x9550e0:
   self.keywords.setdefault(a,set()).add(self.text[b]);self.ret()
  else:super().hook(u,addr,size,user)

rows=[]
for b in (0x180000000,0x190000000):
 e=PopupV26(b);t=e.score_text('Scoreboard')
 e.call('score_outline_tmp_force_v21',t);m=e.mats[t]
 assert e.keywords[m]=={'OUTLINE_ON'} and e.tmp[t]['rgba']==0xff000000
 e.call('score_outline_tmp_force_v21',t);assert e.mats[t]==m
 # Font replacement may produce a new material: the same hook must enable it.
 fresh=e.alloc();e.mats[t]=fresh;e.call('score_outline_tmp_v20',t)
 assert e.keywords[fresh]=={'OUTLINE_ON'}
 e.supports=False;t2=e.score_text('Scoreboard');e.call('score_outline_tmp_force_v21',t2)
 assert e.mats[t2] not in e.keywords
 old=dict(e.mats);e.call('score_outline_tmp_force_v21',0);assert e.mats==old
 rows.append(dict(base=hex(b),instance_material_keyword_enabled=True,font_replacement_covered=True,shared_asset_unmodified=True))

space=dict(__file__=str(R/'test_customization_v19.py'))
exec((R/'test_customization_v19.py').read_text().split('\ncases=0')[0],space)
AvatarEngine=space['AvatarEngine']
class PreviewV26(AvatarEngine):
 def __init__(self,b):
  super().__init__(b);self.lifecycle=[];self.curving=[]
  for n in ('CC_FacePreview','CC_OutfitPreview'):self.visible[self.overlay_children[n]]=True
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==0x24cfc0:self.curving.append((a,b));self.ret()
  elif r==0x94f700:
   self.lifecycle.append((a,bool(b)));self.visible[a]=bool(b);self.ret()
  elif r==0x94f9a0:self.ret(self.visible.get(a,False))
  else:super().hook(u,addr,size,user)
for b in (0x180000000,0x190000000):
 for fmt in (2,4):
  e=PreviewV26(b);e.configure(fmt);e.press('CC_CustomizeOpen')
  for visit in range(2):
   if visit:e.press('CC_CustomizeBack');e.press('CC_CustomizeOpen')
   for button in ('CC_FaceNext','CC_OutfitNext','CC_FacePrev','CC_OutfitPrev'):
    start=len(e.lifecycle);e.press(button)
    expected=[]
    for name in ('CC_FacePreview','CC_OutfitPreview'):
     obj=e.overlay_children[name];expected.extend([(obj,False),(obj,True)])
    assert e.lifecycle[start:]==expected,'Selection re-entered a page or button lifecycle'
    assert all(value==1 for _,value in e.curving)
    assert e.visible[e.panel]
  rows.append(dict(base=hex(b),format=fmt,two_visits=True,preview_only_lifecycle=True,no_match_reentry=True))
result=dict(passed=True,cases=rows,native_sha256=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest(),
 source_hashes={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['customization_v19.c','score_outline_v20.c']},
 scope='Integrated compiled game code with Unity API stubs; screenshots recorded by separate disposable Unity probe.')
(R/'analysis/v26-ui-native-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(passed=True,cases=len(rows))))
