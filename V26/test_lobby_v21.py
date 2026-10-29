"""Production lobby C plus original x64 Hand.Update/StartInteraction; isolated."""
from pathlib import Path
import json,os,struct,subprocess,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_64,UC_HOOK_CODE
from unicorn.x86_const import *
from fix_lobby_v21 import LOBBY_CALLS_V21
HARNESS=r'''
typedef unsigned long long U64;
typedef struct {float x,y,z;} V3;
typedef struct {float x,y,z,w;} Q4;
typedef void (*SetVec)(void*,V3,void*);
#define EXPORT __declspec(dllexport)
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
#define INT(o,n) (*(int*)((char*)(o)+(n)))
#define BYTE(o,n) (*(unsigned char*)((char*)(o)+(n)))
#define TRAMP(t,n,args) EXPORT __attribute__((naked)) t n##_trampoline args {__asm__(".rept 32; int3; .endr");}
static U64 original_base;
static U64 base(void){return original_base;}
#define FN(r,t) ((t)(base()+(r)))
static float physics_interval=1.f/30;
static void* player; static int online=1,pointer_over;
static int network_physics(void){return online;}
static void* online_local_player(void){return player;}
static int ui_pointer_over_button_v19(void){return pointer_over;}
static int finitev(V3 p){return __builtin_isfinite(p.x)&&__builtin_isfinite(p.y)&&__builtin_isfinite(p.z);}
static void* rooted(unsigned h){return h?FN(0x14ac80,void*(*)(unsigned))(h):0;}
static void root_set(unsigned* h,void* o){if(*h)FN(0x14ac70,void(*)(unsigned))(*h);*h=o?FN(0x14ac90,unsigned(*)(void*,_Bool))(o,0):0;}
static void managed_field(void* o,int n,void* v){FN(0x14ac30,void(*)(void*,void**,void*))(o,(void**)((char*)o+n),v);}
static int alive(void* o){return o&&FN(0xa0bfb0,_Bool(*)(void*,void*))(o,0);}
static void* transform(void* o){return FN(0x94b620,void*(*)(void*,void*))(o,0);}
static void* gameobject(void* o){return o;}
static V3 position(void* t){return FN(0xb74de0,V3(*)(void*,void*))(t,0);}
static void position_set(void* t,V3 p){FN(0xb756b0,SetVec)(t,p,0);}
static void* str(const char* s){return FN(0x14b790,void*(*)(const char*))(s);}
#include "../lobby_v18.c"
EXPORT void configure(U64 b,void* p,int net,int ui){original_base=b;player=p;online=net;pointer_over=ui;}
EXPORT void* hand_find_hook(void* h,void* m){return lobby_active()&&lobby_local_hand(h)&&!pointer_over?lobby_hand_ball(h):0;}
EXPORT int DllMain(void* m,unsigned why,void* reserved){return 1;}
'''
def compile_harness():
 c=R/'tools/l21.c';dll=R/'tools/l21.dll';c.write_text(HARNESS)
 env=dict(os.environ);cache=str(R/'tools/zl21');env.update(ZIG_LOCAL_CACHE_DIR=cache,ZIG_GLOBAL_CACHE_DIR=cache)
 result=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(c),'-o',str(dll),'-Wl,--entry=DllMain'],env=env,capture_output=True,text=True)
 assert not result.returncode,result.stdout+result.stderr
 return pefile.PE(str(dll))
H,S,STOP=0x300000000,0x400000000,0x3000ff000
class Engine:
 def __init__(self,b,q):
  self.b=b;self.code=b+0x2000000;self.u=u=Uc(UC_ARCH_X86,UC_MODE_64)
  p=pefile.PE(str(R/'backup/GameAssembly.dll'));u.mem_map(b,0x1950000);u.mem_write(b,p.get_memory_mapped_image())
  u.mem_map(self.code,0x100000);image=bytearray(q.get_memory_mapped_image())
  for block in getattr(q,'DIRECTORY_ENTRY_BASERELOC',[]):
   for e in block.entries:
    if e.type==10:struct.pack_into('<Q',image,e.rva,struct.unpack_from('<Q',image,e.rva)[0]+self.code-q.OPTIONAL_HEADER.ImageBase)
  u.mem_write(self.code,bytes(image));u.mem_map(H,0x100000);u.mem_map(S,0x100000)
  self.ex={e.name.decode():self.code+e.address for e in q.DIRECTORY_ENTRY_EXPORT.symbols}
  at=self.ex['lobby_hand_update_trampoline'];u.mem_write(at,b'\xe9'+struct.pack('<i',b+0x312f60-at-5))
  at=b+0x312c50;u.mem_write(at,b'\xe9'+struct.pack('<i',self.ex['hand_find_hook']-at-5))
  at=b+0x31c2cf;u.mem_write(at,b'\xe8'+struct.pack('<i',self.ex['lobby_jump_area_hook']-at-5))
  self.ex['player_update_native']=b+0x31c250
  self.next=H+0x1000;self.roots={};self.owned=set();self.transforms={};self.pos={};self.parents={};self.grab=set();self.locals=set();self.dead=set();self.spawned=[];self.destroyed=[];self.vel={};self.angular={};self.active=True;self.room=True;self.time=10;self.menu_down=False;self.menu_shown=True;self.menu_calls=[];self.releases=0
  self.klass=self.alloc(0x400);self.ptr(b+0x1519208,self.klass);self.ptr(self.klass+0x190,b+0x77f660);self.ptr(self.klass+0x1a0,STOP-0x100)
  self.ballklass=self.alloc();self.statics=self.alloc();self.ptr(b+0x15426f0,self.ballklass);self.ptr(self.ballklass+0xb8,self.statics)
  self.page=self.alloc();self.menu=self.alloc();self.ptr(self.page+0x68,self.menu);self.player=self.alloc();self.body=self.alloc();self.bodyt=self.alloc();self.ptr(self.player+0x80,self.body);self.transforms[self.body]=self.bodyt
  self.player_view=self.alloc();self.owned.add(self.player_view);self.jumps=[];self.jump_mode=2
  u.hook_add(UC_HOOK_CODE,self.hook);self.call('configure',b,self.player,1,0);self.call('lobby_enter_hook',self.page,0,0)
 def alloc(self,n=0x100):v=self.next;self.next+=(n+15)&~15;return v
 def ptr(self,a,v):self.u.mem_write(a,struct.pack('<Q',v))
 def q(self,a):return struct.unpack('<Q',self.u.mem_read(a,8))[0]
 def vec(self,a,v=None):
  if v is None:return struct.unpack('<fff',self.u.mem_read(a,12))
  self.u.mem_write(a,struct.pack('<fff',*v))
 def ret(self,v=0,f=None):
  if f is not None:self.u.reg_write(UC_X86_REG_XMM0,struct.unpack('<I',struct.pack('<f',f))[0])
  self.u.reg_write(UC_X86_REG_RAX,int(v));sp=self.u.reg_read(UC_X86_REG_RSP);self.u.reg_write(UC_X86_REG_RIP,self.q(sp));self.u.reg_write(UC_X86_REG_RSP,sp+8)
 def call(self,name,*args):
  for reg,val in zip((UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9),list(args)+[0]*4):self.u.reg_write(reg,val)
  sp=S+0xf008;self.ptr(sp,STOP);self.u.reg_write(UC_X86_REG_RSP,sp)
  try:self.u.emu_start(self.ex[name],STOP,count=300000)
  except Exception as err:raise AssertionError((name,hex(self.u.reg_read(UC_X86_REG_RIP)),err))
  assert self.u.reg_read(UC_X86_REG_RIP)==STOP,(name,hex(self.u.reg_read(UC_X86_REG_RIP)))
  return self.u.reg_read(UC_X86_REG_RAX)
 def hook(self,u,at,size,user):
  r=at-self.b;a,b,c=[u.reg_read(x) for x in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if at in [self.ex[n+'_trampoline'] for n in ('lobby_enter','lobby_start','lobby_update')]:self.ret()
  elif at==self.ex['lobby_ball_awake_trampoline']:self.ptr(self.statics,a);self.ret()
  elif r==0x9478e0:self.ret(self.active)
  elif r==0x61efc0:self.ret(self.room)
  elif r==0xa0bfb0:self.ret(a not in self.dead)
  elif r==0x14ac80:self.ret(self.roots[a])
  elif r==0x14ac70:self.roots.pop(a);self.ret()
  elif r==0x14ac90:
   handle=max(self.roots,default=0)+1;self.roots[handle]=a;self.ret(handle)
  elif r==0x14ac30:self.ptr(b,c);self.ret()
  elif r==0x94b620:self.ret(self.transforms.get(a,0))
  elif r==0xb74de0:self.vec(a,self.pos[b]);self.ret(a)
  elif r==0xb756b0:self.pos[a]=self.vec(b);self.ret()
  elif r==0xb755b0:self.parents[a]=b;self.ret()
  elif r==12008720:self.ret(a in self.locals and b==self.bodyt)
  elif r==0xe6e000:self.ret(a in self.owned)
  elif r==0x6054c0:self.ret(self.player_view)
  elif r==0xef3330:self.ret(self.jump_mode)
  elif r==0xef3570:self.ret(0)
  elif r==0x31b390:self.ret(1)
  elif r==0x1c22e0:self.ret(self.alloc())
  elif r==0x1fd2b0:self.ret()
  elif r==0xa0a0c0:self.jumps.append((a,self.q(b+0x20),struct.unpack('<i',u.mem_read(b+0x10,4))[0]));self.ret(self.alloc())
  elif r==0xb72b40:self.ret(f=self.time)
  elif r==0x3130b0:self.ret(a in self.grab)
  elif r==0x314470:self.ret(self.menu_down)
  elif r in (0x318350,0x3183d0):assert a==self.menu;self.menu_shown=r==0x3183d0;self.menu_calls.append(r);self.ret()
  elif r==0xef3370:self.ret(False)
  elif r==0x14b790:self.ret(self.alloc())
  elif r==0x60fb50:
   ball=self.alloc(0x200);view=self.alloc();t=self.alloc();rb=self.alloc();self.ptr(ball,self.klass);self.ptr(ball+0xc8,view);self.ptr(ball+0x98,rb);self.ptr(ball+0x30,rb);self.transforms[ball]=t;self.pos[t]=self.vec(b);self.owned.add(view);self.spawned.append(ball)
   self.spawn_sp=u.reg_read(UC_X86_REG_RSP);self.ptr(self.spawn_sp-0x60,STOP-0x200);u.reg_write(UC_X86_REG_RSP,self.spawn_sp-0x60);u.reg_write(UC_X86_REG_RCX,ball);u.reg_write(UC_X86_REG_RIP,self.ex['lobby_ball_awake_hook'])
  elif at==STOP-0x200:u.reg_write(UC_X86_REG_RSP,self.spawn_sp);self.ret(self.spawned[-1])
  elif r==0x94f410:self.ret(a)
  elif r==0x60cb40:self.destroyed.append(a);self.ret()
  elif r==0x94f700:self.ret()
  elif r==0xec60d0:self.vel[a]=self.vec(b);self.ret()
  elif r==0xec5cd0:self.angular[a]=self.vec(b);self.ret()
  elif r in (0x1c21b0,0x14b040):self.ret()
  elif r==0xa0c080:self.ret(a!=b)
  elif r==0xa0be40:self.ret(a==b)
  elif at==STOP-0x100:self.releases+=1;u.mem_write(a+0xd0,b'\0');self.ptr(a+0xd8,0);self.ret()
 def hand(self,right,local=True):
  h=self.alloc();t=self.alloc();self.transforms[h]=t;self.ptr(h+0x18,t);self.pos[t]=((-1 if not right else 1),1.4,-4);self.u.mem_write(h+0x24,bytes([right]))
  if local:self.locals.add(t)
  return h
 def update(self,h,down):
  (self.grab.add if down else self.grab.discard)(h);self.call('lobby_hand_update_hook',h)
def run():
 q=compile_harness();cases=[];p=pefile.PE(str(R/'backup/GameAssembly.dll'))
 for _,site,target,_ in LOBBY_CALLS_V21:assert p.get_data(site,5)==b'\xe8'+struct.pack('<i',target-site-5)
 for base in [0x180000000,0x190000000]:
  e=Engine(base,q);left=e.hand(0);right=e.hand(1);remote=e.hand(0,False)
  e.update(remote,True);assert not e.spawned
  e.update(left,True);ball=e.q(left+0x30);assert ball and e.spawned==[ball] and e.q(ball+0xd8)==left and e.q(e.statics)==0
  e.update(right,True);assert e.q(right+0x30)==ball and e.q(left+0x30)==0 and e.q(ball+0xd8)==right
  for _ in range(8):e.update(left,True);e.update(right,True)
  assert e.q(right+0x30)==ball and e.q(left+0x30)==0 and e.spawned==[ball]
  for i in range(30):
   h=left if i%2 else right;e.update(h,False);e.update(h,True);assert e.q(h+0x30)==ball and e.q(ball+0xd8)==h
  rb=e.q(ball+0x98);assert e.vel[rb]==e.angular[rb]==(0.,0.,0.) and e.spawned==[ball]
  e.call('configure',base,e.player,1,1);e.update(right,False);before=e.q(ball+0xd8);e.update(right,True);assert e.q(ball+0xd8)==before
  e.call('configure',base,e.player,1,0)
  peer=e.alloc(0x200);pv=e.alloc();pt=e.alloc();e.ptr(peer+0xc8,pv);e.transforms[peer]=pt;e.pos[pt]=(2,1,0);e.call('lobby_ball_awake_hook',peer)
  e.update(right,False);e.update(right,True);assert e.q(right+0x30)==ball and len(e.spawned)==1
  e.call('lobby_selector_hide_v21');assert not e.menu_shown and e.call('lobby_move_enabled_hook')==1 and e.call('lobby_jump_area_hook',0,0)==1
  # Execute the actual NetworkPlayer.Update null-area branch, with only the
  # engine scheduler mocked. A normal jump coroutine is created for the local
  # player despite the absent pre-match team/playArea assignment.
  e.call('player_update_native',e.player);assert e.jumps==[(e.player,e.player,0)]
  e.call('lobby_selector_show_v21');assert e.menu_shown
  e.call('lobby_selector_hide_v21');e.menu_down=True;e.call('lobby_update_hook',e.page);assert e.menu_shown
  e.call('lobby_start_hook',e.page);assert e.destroyed==[ball] and e.call('lobby_move_enabled_hook')==0 and e.call('lobby_jump_area_hook',0,0)==0
  e.call('player_update_native',e.player);assert len(e.jumps)==1
  e.ptr(e.player+0x20,e.alloc());e.call('player_update_native',e.player);assert len(e.jumps)==2
  e.update(right,False);e.update(right,True);assert len(e.spawned)==1
  cases.append(hex(base))
 report=dict(passed=True,ASLR_bases=cases,checks=['native held-object gate','native vtable attachment','one local ball after 30 alternating recalls','transfer while both triggers remain held','no old-hand reacquisition','zero velocities on recall','remote hands rejected','peer ownership preserved','UI ray clicks excluded','selector hidden practice active','menu input reopens selector','native NetworkPlayer.Update starts normal jump without team area only in lobby','cleanup destroys only owned balls'],scope='Compiled x64/native Hand.Update and NetworkPlayer.Update with engine stubs; no real Unity physics, Quest or two-PC session claimed.')
 (R/'analysis/v21-lobby-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':run()
