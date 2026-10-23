"""Execute actual patched x64 code with deterministic engine stubs.
Menu navigation, ABI, exact spawn counts, area cycles, restoration and ASLR.
"""
import sys,pathlib,struct,json
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_64,UC_HOOK_CODE
from unicorn.x86_const import *
p=pefile.PE(str(R/'working/GameAssembly.dll'))
manifest=json.loads((R/'analysis/native-patch-manifest.json').read_text());ex=manifest['exports']
H=0x300000000;S=0x400000000;STOP=H+0xff000
class Engine:
 def __init__(self,base):
  self.b=base;self.u=u=Uc(UC_ARCH_X86,UC_MODE_64);u.mem_map(base,(p.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);u.mem_write(base,p.get_memory_mapped_image())
  if base!=p.OPTIONAL_HEADER.ImageBase:
   for block in p.DIRECTORY_ENTRY_BASERELOC:
    for e in block.entries:
     if e.type==10:self.ptr(base+e.rva,self.q(base+e.rva)+base-p.OPTIONAL_HEADER.ImageBase)
  u.mem_map(H,0x100000);u.mem_map(S,0x100000)
  self.next=H+0x1000;self.roots={};self.text={};self.labels={};self.buttons={};self.visible={};self.pos={};self.transforms={};self.calls=[];self.online=False
  self.klass=self.alloc(0x800);self.ptr(self.klass+0x5b0,H+0xfd000)
  self.page=self.alloc();self.ptr(self.page+0x38,self.newtext('Solo'))
  for offset,label in [(0x40,'Beach Day'),(0x48,'Beach Night'),(0x50,'Indoor'),(0x58,'Bomb'),(0x60,'Back')]:
   button=self.alloc();self.buttons[button]=self.newtext(label);self.ptr(self.page+offset,button)
  self.target=self.alloc();self.bot=self.alloc();self.flt(self.bot+0x3c,2);self.flt(self.bot+0x44,2)
  self.game=self.alloc();teams=self.alloc();self.ptr(self.game+0x60,teams);self.ptr(teams+0x18,2);self.teams=[];self.areas=[]
  for t in range(2):
   team=self.alloc();self.teams.append(team);self.ptr(teams+0x20+t*8,team);lst=self.alloc();arr=self.alloc();self.ptr(team+0x18,lst);self.integer(lst+0x18,4);self.ptr(lst+0x10,arr)
   members=self.alloc();self.ptr(team+0x28,members);self.integer(members+0x18,0)
   areas=[self.alloc() for _ in range(4)];self.areas.append(areas)
   for i,a in enumerate(areas):
    self.ptr(arr+0x20+i*8,a);self.ptr(a+0x28,areas[(i+1)%4]);self.vec(a+0x18,(4.5,2,4.5));self.u.mem_write(a+0x38,bytes([int(i==2),int(i>=2)]))
    transform=self.alloc();default=self.alloc();self.transforms[a]=transform;self.ptr(a+0x30,default)
    self.pos[transform]=((-2.25 if i in (0,3) else 2.25),0,(2.25 if i<2 else 6.75)*(1 if t else -1));self.pos[default]=self.pos[transform]
  self.original_pos=self.pos.copy();u.hook_add(UC_HOOK_CODE,self.hook)
 def alloc(self,n=0x100):v=self.next;self.next+=(n+15)&~15;return v
 def ptr(self,a,v):self.u.mem_write(a,struct.pack('<Q',v))
 def q(self,a):return struct.unpack('<Q',self.u.mem_read(a,8))[0]
 def integer(self,a,v):self.u.mem_write(a,struct.pack('<i',v))
 def val(self,name):return struct.unpack('<i',self.u.mem_read(self.b+ex[name],4))[0]
 def flag(self,name,v):self.integer(self.b+ex[name],v)
 def flt(self,a,v=None):
  if v is None:return struct.unpack('<f',self.u.mem_read(a,4))[0]
  self.u.mem_write(a,struct.pack('<f',v))
 def vec(self,a,v=None):
  if v is None:return struct.unpack('<fff',self.u.mem_read(a,12))
  self.u.mem_write(a,struct.pack('<fff',*v))
 def string(self,s):v=self.alloc();self.text[v]=s;return v
 def newtext(self,s):v=self.alloc();self.ptr(v,self.klass);self.labels[v]=self.string(s);return v
 def ret(self,v=None,f=None):
  if v is not None:self.u.reg_write(UC_X86_REG_RAX,v)
  if f is not None:self.u.reg_write(UC_X86_REG_XMM0,struct.unpack('<I',struct.pack('<f',f))[0])
  sp=self.u.reg_read(UC_X86_REG_RSP);self.u.reg_write(UC_X86_REG_RIP,self.q(sp));self.u.reg_write(UC_X86_REG_RSP,sp+8)
 def hook(self,u,addr,size,_):
  r=addr-self.b;a,b,c,d=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9)]
  if addr==H+0xfd000:self.ret(self.labels[a])
  elif r==0x14ac80:self.ret(self.roots[a])
  elif r==0x14ac70:self.roots.pop(a);self.ret()
  elif r==0x14ac90:h=max(self.roots.keys(),default=0)+1;self.roots[h]=a;self.ret(h)
  elif r==0x14ac30:self.ptr(b,c);self.ret()
  elif r==0x14b790:
   data=bytes(u.mem_read(a,100)).split(b'\0')[0].decode();self.ret(self.string(data))
  elif r==0xe84d60:self.labels[a]=b;self.ret()
  elif r==0xef46a0:self.ret(self.buttons[self.q(a+0x50)])
  elif r==0x94b570:self.ret(a)
  elif r==0x94f700:self.visible[a]=bool(b);self.ret()
  elif r==0xee3400:self.ret()
  elif r==0x402600:self.ret(H+0xfc000)
  elif r==0x61fbf0:self.ret(not self.online)
  elif r==0x94b620:self.ret(self.transforms[a])
  elif r==0xb74de0:self.vec(a,self.pos[b]);self.ret(a)
  elif r==0xb756b0:self.pos[a]=self.vec(b);self.ret()
  elif r==0xef32b0:self.ret(1)
  elif r==0xef33b0:self.ret(f=1.5)
  elif r==ex['pass_target_trampoline']:self.ret(self.target)
  elif r==ex['bot_body_trampoline']:self.calls.append(('speed',self.flt(a+0x3c)));self.ret()
  elif r==ex['add_player_trampoline']:self.calls.append(('member',a,c));self.ret()
  elif r==ex['spawn_bot_trampoline']:self.calls.append(('spawn',c,d));self.ret()
  elif r==ex['game_go_trampoline']:self.calls.append(('go',));self.ret()
  elif r in [ex[n+'_trampoline'] for n in ('online_entry','solo_awake','solo_entry','solo_day','solo_night','solo_back','solo_start','main_menu')]:self.calls.append(('original',r));self.ret(H+0xfc000)
 def call(self,name,*args):
  u=self.u;sp=S+0x80008;u.reg_write(UC_X86_REG_RSP,sp);self.ptr(sp,STOP)
  for reg,value in zip((UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9),list(args)+[0]*4):u.reg_write(reg,value)
  self.ptr(sp+0x28,0);self.ptr(sp+0x30,0);u.emu_start(self.b+ex[name],STOP,count=100000)
  assert u.reg_read(UC_X86_REG_RIP)==STOP,name
  return u.reg_read(UC_X86_REG_RAX)
 def label(self,offset):return self.text[self.labels[self.buttons[self.q(self.page+offset)]]]

def run(base):
 e=Engine(base);e.call('solo_awake_hook',e.page)
 assert e.label(0x40)=='4v4' and e.label(0x48)=='2v2';assert not e.visible[e.q(e.page+0x50)]
 e.call('solo_night_hook',e.page);assert e.val('solo_stage')==2 and e.label(0x40)=='Beach Day'
 assert e.visible[e.q(e.page+0x50)] and not e.visible[e.q(e.page+0x48)] and not e.visible[e.q(e.page+0x58)]
 e.call('solo_start_hook',e.page,123,0);assert e.val('doubles_requested')==1
 e.call('game_go_hook',e.game);assert e.val('doubles_enabled')==1
 for t,areas in enumerate(e.areas):
  assert e.q(areas[2]+0x28)==areas[0] and e.q(areas[0]+0x28)==areas[2]
  for i in (0,2):assert e.vec(areas[i]+0x18)==(4.5,2,9) and abs(e.pos[e.transforms[areas[i]]][2])==4.5
 e.calls=[]
 for slot in (0,2,3):e.call('spawn_bot_hook',e.game,123,0,slot)
 for slot in range(4):e.call('spawn_bot_hook',e.game,123,1,slot)
 assert e.calls==[('spawn',0,2),('spawn',1,2),('spawn',1,0)] and e.val('doubles_spawned')==3
 for t in range(2):
  e.call('add_player_hook',e.teams[t],e.bot,1)
  assert e.calls[-1]==('member',e.teams[t],0)
 assert e.call('front_row_hook')==0
 e.call('player_speed_hook');assert abs(struct.unpack('<f',struct.pack('<I',e.u.reg_read(UC_X86_REG_XMM0)&0xffffffff))[0]-2.4)<1e-5
 for _ in range(3):e.call('bot_body_hook',e.bot);assert abs(e.calls[-1][1]-3.2)<1e-5 and e.flt(e.bot+0x3c)==2
 e.integer(e.bot+0x28,1);e.call('bot_body_hook',e.bot);assert abs(e.calls[-1][1]-2.8)<1e-5
 e.integer(e.bot+0x28,0)
 for t in (0,1):
  serve_transform=e.transforms[e.areas[t][2]];before=e.pos[serve_transform];result=e.alloc()
  for _ in range(3):
   e.call('bot_serve_position_hook',result,serve_transform,0)
   assert e.vec(result)==(before[0],before[1]+2,before[2]) and e.pos[serve_transform]==before
 e.u.mem_write(e.target+0x24,b'\1');e.flt(e.target+0x20,0);e.call('pass_target_hook',e.bot);assert e.flt(e.target+0x20)==3.25
 e.u.mem_write(e.target+0x24,b'\0');e.flt(e.target+0x20,2);e.call('pass_target_hook',e.bot);assert e.flt(e.target+0x20)==2
 e.call('solo_back_hook',e.page);assert e.val('solo_stage')==0
 e.call('solo_day_hook',e.page);assert e.val('solo_stage')==4 and all(e.visible[e.q(e.page+o)] for o in (0x40,0x48,0x50,0x58))
 e.call('solo_start_hook',e.page,123,0);e.call('game_go_hook',e.game);assert e.val('doubles_enabled')==0 and e.val('quartet_enabled')==1
 for areas in e.areas:
  for i,a in enumerate(areas):assert e.q(a+0x28)==areas[(i+1)%4]
 assert e.call('front_row_hook')==0
 e.call('bot_serve_position_hook',result,serve_transform,0);assert e.vec(result)==e.pos[serve_transform]
 e.call('bot_body_hook',e.bot);assert abs(e.calls[-1][1]-3.2)<1e-5
 e.u.mem_write(e.target+0x24,b'\1');e.call('pass_target_hook',e.bot);assert e.flt(e.target+0x20)==2
 e.flag('doubles_requested',1);e.online=True;e.call('game_go_hook',e.game);assert e.val('doubles_enabled')==0 and e.pos==e.original_pos
 e.online=False;e.u.mem_write(e.game+0x68,b'\1');e.call('game_go_hook',e.game);assert e.val('doubles_enabled')==0
 e.flag('doubles_requested',1);e.flag('doubles_enabled',1);e.call('main_menu_hook',e.page);assert e.val('doubles_requested')==0 and e.val('doubles_enabled')==1
 e.call('solo_entry_hook',e.page);assert e.val('solo_stage')==0
 return True
assert run(0x180000000) and run(0x190000000)
report={'passed':18,'ASLR_bases':2,'checks':['format selector','2v2 courts','4v4 courts','back navigation','reopen Solo resets','three bots only','two member slots per team','two-position rotation','whole depth coverage','4v4 cross and online geometry restoration','all four positions participate in 4v4 rotation','player speed multiplier','bot speed without accumulation','higher set to player','bot-to-bot unchanged','inactive rally does not modify set','online excluded','bomb excluded'],'scope':'Patched machine code with deterministic engine stubs; does not replace Unity or VR testing.'}
(R/'analysis/2v2-test-results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

