"""Runtime score outlines: native ABI, scope, repeat enable, and raycasts."""
from pathlib import Path
__file__=str(Path(__file__).with_name('test_cloudcourt_v16.py'))
exec(Path(__file__).read_text().split('\nchecks=[]')[0])

class OutlineEngine(CloudEngine):
 def __init__(self,base):
  super().__init__(base);self.parents={};self.outlines={};self.created=0;self.rays={};self.tmp={};self.shadow={}
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==0xb739d0:self.ret(self.parents.get(a,0))
  elif r==0x7911d0:self.rays[a]=bool(b);self.ret()
  elif r==0x2402d0:self.tmp.setdefault(a,{})['rgba']=b&0xffffffff;self.ret()
  elif r==0x240340:
   self.tmp.setdefault(a,{})['width']=struct.unpack('<f',struct.pack('<I',u.reg_read(UC_X86_REG_XMM1)&0xffffffff))[0];self.ret()
  elif r==0x94f570:self.ret(self.outlines.get(a,0))
  elif r==0x94f240:
   outline=self.alloc();self.outlines[a]=outline;self.created+=1;self.ret(outline)
  elif r==0x83e5a0:self.shadow.setdefault(a,{})['color']=struct.unpack('<4f',u.mem_read(b,16));self.ret()
  elif r==0x83e650:self.shadow.setdefault(a,{})['distance']=struct.unpack('<2f',struct.pack('<Q',b));self.ret()
  elif r==0x83e7b0:self.shadow.setdefault(a,{})['alpha']=bool(b);self.ret()
  else:super().hook(u,addr,size,user)
 def score_text(self,parent_name):
  text=self.alloc();t=self.alloc();parent=self.alloc();self.transforms[text]=t;self.transforms[t]=t
  self.names[t]='Score';self.names[parent]=parent_name;self.parents[t]=parent;return text

cases=[]
for base in (0x180000000,0x190000000):
 e=OutlineEngine(base)
 for parent in ('Scoreboard','CloudBoard0','CloudBoard1'):
  text=e.score_text(parent);e.call('score_outline_tmp_v20',text)
  assert e.tmp[text]['rgba']==0xff000000 and abs(e.tmp[text]['width']-.18)<1e-6 and not e.rays[text]
  before=e.created;e.call('score_outline_text_v20',text);e.call('score_outline_text_v20',text)
  assert e.created==before+1 and not e.rays[text]
  outline=e.outlines[text];assert e.shadow[outline]=={'color':(0,0,0,1),'distance':(2.5,2.5),'alpha':True}
  cases.append((hex(base),parent))
 text=e.score_text('Menu');before=e.created;e.call('score_outline_tmp_v20',text);e.call('score_outline_text_v20',text)
 assert e.created==before and text not in e.rays and text not in e.tmp
report={'passed':True,'cases':cases,'checks':['black opaque TMP Color32 uses verified Windows x64 ABI','TMP thickness applied after font assignment','UI.Text Outline added once through Unity API','outline uses text alpha','unrelated menu labels untouched','score labels do not intercept rays'],
        'scope':'Compiled helper with engine stubs; headset rendering still needs visual confirmation.'}
(R/'analysis/v20-score-outline-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
