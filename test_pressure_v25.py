"""Independent production trigger predicate test with actual native interface dispatch.

Uses an isolated tools/t25pressure build. Does not read or change working DLL.
The original grab result is a fixture; full Hand.Update belongs to integration tests.
"""
from pathlib import Path
import hashlib,json,os,struct,subprocess,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_64,UC_HOOK_CODE
from unicorn.x86_const import *
H,S,STOP,DELTA=0x300000000,0x400000000,0x3000ff000,0x194f000
T=R/'tools/t25pressure';T.mkdir(exist_ok=True)
source=T/'p.c'
source.write_text((R/'test_pressure_v25_harness.c').read_text().replace('#include "spawn_input_v24.c"','#include "../../spawn_input_v24.c"'))
env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str(T/'g'),ZIG_LOCAL_CACHE_DIR=str(T/'l'))
subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc',
 '-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(source),'-o',str(T/'p.dll'),'-Wl,--entry=DllMain'],
 check=True,env=env,capture_output=True)
P=pefile.PE(str(T/'p.dll'));EX={x.name.decode():x.address+DELTA for x in P.DIRECTORY_ENTRY_EXPORT.symbols}
ORIGINAL=pefile.PE(str(R/'backup/GameAssembly.dll'),fast_load=True)
# Independently decode the original RIP operands; do not infer RVAs from helper.
cmp=ORIGINAL.get_data(0x3130b6,7);load=ORIGINAL.get_data(0x3130c2,6)
assert cmp[:2]==b'\x80\x3d' and cmp[-1]==0 and load[:2]==b'\x8b\x0d'
metadata_flag=0x3130bd+struct.unpack('<i',cmp[2:6])[0]
metadata_token=0x3130c8+struct.unpack('<i',load[2:6])[0]
assert (metadata_flag,metadata_token)==(0x150060e,0x12a144c)
native_init_call=ORIGINAL.get_data(0x3130c8,5)
assert native_init_call[0]==0xe8 and 0x3130cd+struct.unpack('<i',native_init_call[1:])[0]==0x1c21b0
# Reuse only the fixture class; its compiler and run() are never evaluated.
text=(R/'test_input_v19.py').read_text()
exec(text[text.index('class InputEngine:'):text.index('\ndef run():')])

class PressureEngine(InputEngine):
 def __init__(self,base,cold=False):
  super().__init__(base);self.queries=[];self.local=True
  self.metadata_calls=0;self.metadata_pending={}
  self.integer(base+metadata_token,0x5125)
  self.u.mem_write(base+metadata_flag,b'\0' if cold else b'\1')
  if cold:
   for rva in (0x1542b48,0x1541dc0,0x1541d98):
    self.metadata_pending[rva]=self.q(base+rva);self.ptr(base+rva,0)
  self.hands=[self.alloc(),self.alloc()]
  self.u.mem_write(self.hands[1]+0x24,b'\1')
  self.player=self.alloc();self.body=self.alloc();self.ptr(self.player+0x80,self.body)
 def hook(self,u,addr,size,user):
  if addr==self.b+0x1c21b0:
   assert u.reg_read(UC_X86_REG_RCX)==0x5125
   self.metadata_calls+=1
   for rva,value in self.metadata_pending.items():self.ptr(self.b+rva,value)
   self.metadata_pending.clear();self.ret();return
  if addr==self.b+12008720:self.ret(int(self.local));return
  if addr in (H+0x81000,H+0x82000):self.queries.append((self.controllers.index(u.reg_read(UC_X86_REG_RCX)),addr==H+0x82000))
  super().hook(u,addr,size,user)
 def probe(self,side):return self.call('pressure_probe',self.hands[side])&255
 def mode(self,off,net,orig):self.call('fixture_mode',off,net,orig,self.player)
 def grabbed(self,side):return self.call('hand_input_v25_hook',self.hands[side])&255

checks=[]
for base in (0x180000000,0x190000000):
 cold=PressureEngine(base,cold=True)
 assert not cold.call('pressure_probe',0) and cold.metadata_calls==0
 cold.analog=[.9,0.]
 assert cold.probe(0)==1 and cold.metadata_calls==1 and not cold.metadata_pending
 # Own once flag prevents duplicate initialization while native flag stays cold.
 assert cold.probe(0)==1 and cold.probe(1)==0 and cold.metadata_calls==1
 assert cold.u.mem_read(base+metadata_flag,1)==b'\0'
 e=PressureEngine(base)
 assert not e.call('pressure_probe',0)
 for side in (0,1):
  for pressure,expected in ((.59,0),(.60,1),(.45,1),(.35,0),(.45,0),(.9,1),(float('nan'),0),(.9,1),(float('inf'),0)):
   e.analog[side]=pressure;assert e.probe(side)==expected,(side,pressure,expected)
  e.digital[side]=True;e.analog[side]=float('nan');assert e.probe(side)==1
  e.digital[side]=False;assert e.probe(side)==0
 # Independent left/right latch and repeated read do not consume held state.
 e.analog=[.9,.1];assert e.probe(0)==1 and e.probe(1)==0
 e.analog[0]=.45;assert e.probe(0)==e.probe(0)==1
 e.analog[1]=.9;assert e.probe(1)==1
 e.analog[0]=.2;assert not e.probe(0) and e.probe(1)==1
 # UI A fallbacks and original grip result cannot create trigger intent.
 e.analog=[0.,0.];e.a=e.steam_a=True;e.mode(1,0,1)
 assert not e.probe(0) and not e.probe(1)
 assert e.grabbed(0)==1  # Preserves original grip while trigger is released.
 e.mode(1,0,0);e.analog[0]=.9;assert e.grabbed(0)==1
 e.analog[0]=.2;assert e.grabbed(0)==0
 # Disconnection releases latch and bypasses original null-throwing reader.
 e.analog[0]=.9;assert e.probe(0)==1
 old=e.q(e.input+0x40);e.ptr(e.input+0x40,0)
 count=e.call('original_calls');e.mode(1,0,1)
 assert e.grabbed(0)==0 and e.call('original_calls')==count
 e.ptr(e.input+0x40,old);e.analog[0]=.45;assert not e.probe(0)
 # New controller identity must not inherit a previous .45 held latch.
 e.analog[0]=.9;assert e.probe(0)==1
 old_controller=e.controllers[0];new=e.alloc();e.controllers[0]=new
 e.interface(new,e.controller_type,{4:H+0x81000,5:H+0x82000})
 e.analog[0]=.45;assert not e.probe(0)
 # Missing interface type or controller clears safely.
 typeptr=e.q(base+0x1541d98);e.ptr(base+0x1541d98,0);assert not e.probe(0)
 e.ptr(base+0x1541d98,typeptr)
 e.controllers[0]=0;assert not e.probe(0);e.controllers[0]=new
 # Remote native predicate cannot sample/reset/consume local analog state.
 e.mode(0,1,0);e.local=True;e.analog[0]=.9;assert e.grabbed(0)==1
 before=list(e.queries);e.local=False;e.analog[0]=.1;assert e.grabbed(0)==0
 assert e.queries==before
 e.local=True;e.analog[0]=.45;assert e.grabbed(0)==1
 # Unsupported session returns native value without polling local trigger.
 e.mode(0,0,1);before=list(e.queries);assert e.grabbed(0)==1 and before==e.queries
 assert e.metadata_calls==0,'warm native metadata flag should skip initializer'
 checks.append(dict(base=hex(base),passed=True,cold_initializer_calls=cold.metadata_calls,warm_initializer_calls=e.metadata_calls))
report=dict(passed=True,cases=checks,source_sha256=hashlib.sha256((R/'spawn_input_v24.c').read_bytes()).hexdigest(),
 metadata_rvas=dict(flag=hex(metadata_flag),token=hex(metadata_token),initializer='0x1c21b0'),
 scope='Compiled production predicate and actual original InterfaceFuncInvoker0; original grab result fixture; no hardware or full Hand.Update claim.')
(R/'analysis/v25-pressure-tests.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
