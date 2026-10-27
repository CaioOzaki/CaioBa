"""Analog-only acquisition through real Hand.Update/WantsToGrab/interface code."""
from pathlib import Path
import hashlib,json,math
__file__=str(Path(__file__).with_name('test_spawn_input_v24.py'))
exec(Path(__file__).read_text().split('\ncases=[]')[0])
NATIVE=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest()
ex['native_hand_release_v25']=0x313160

class RealTriggerEngineV25(SpawnInputEngine):
 def __init__(self,base):
  super().__init__(base);self.digital=[False,False];self.analog=[0.,0.];self.grips=[False,False]
  self.released=0;self.analog_calls=[0,0];self.ui_block=False;self.ui_go=self.alloc();self.ui_button=self.alloc()
  klass=self.alloc(0x200);stat=self.alloc();module=self.alloc(0x200)
  self.ptr(self.b+0x1542440,klass);self.ptr(klass+0xb8,stat);self.ptr(stat+8,module);self.ui_module=module
  self.interface(self.vr,self.q(self.b+0x1541dc0),{5:H+0x80000,6:H+0x80010})
  for controller in self.controllers:self.configure(controller)
 def interface(self,obj,kind,methods):
  klass=self.alloc(0x400);offsets=self.alloc();self.ptr(obj,klass)
  self.u.mem_write(klass+0x126,struct.pack('<H',1));self.ptr(klass+0xb0,offsets);self.ptr(offsets,kind);self.integer(offsets+8,0)
  for index,fn in methods.items():self.ptr(klass+(0x13+index)*16,fn)
 def configure(self,controller):
  self.interface(controller,self.q(self.b+0x1541d98),{1:H+0x83000,4:H+0x81000,5:H+0x82000})
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX)]
  # Do not inherit the old tests' WantsToGrab/Invoker stubs. Execute the actual
  # patched predicate, original trampoline and interface table tail-dispatch.
  if r in (0x3130b0,0xa2710):return
  if addr in (H+0x80000,H+0x80010):self.ret(self.controllers[addr==H+0x80010]);return
  if addr==H+0x81000:self.ret(self.digital[self.controllers.index(a)]);return
  if addr==H+0x82000:
   side=self.controllers.index(a);self.analog_calls[side]+=1;self.ret(0xdeadbeef,f=self.analog[side]);return
  if addr==H+0x83000:self.ret(self.grips[self.controllers.index(a)]);return
  if addr==H+0xfb000:self.released+=1
  if r==0x94f410 and a==self.ui_go and self.text[b]=='Button':self.ret(self.ui_button);return
  super().hook(u,addr,size,user)
 def frame(self,hand,analog=0.,digital=False,grip=False):
  side=self.u.mem_read(hand+0x24,1)[0];self.analog[side]=analog;self.digital[side]=digital;self.grips[side]=grip
  self.ptr(self.ui_module+0xf8,self.ui_go if self.ui_block else 0)
  self.call('lobby_hand_update_hook',hand)
 def release_query(self,hand):return bool(self.call('native_hand_release_v25',hand))

patch=json.loads((R/'analysis/native-patch-manifest.json').read_text())
entry=next(x for x in patch['patches'] if x['name']=='hand_input_v25')
assert entry['rva']==0x3130b0 and entry['length']==6 and entry['original']=='40534883ec20'
raw=p.get_data(0x3130b0,6);assert raw[0]==0xe9 and raw[-1]==0x90
assert 0x3130b5+struct.unpack('<i',raw[1:5])[0]==ex['hand_input_v25_hook']
# Reproduce the reported failure using the actual immutable delivered v24 DLL
# and its preserved address manifest, with exactly the same analog-only input.
current_pe,current_exports=p,ex
baseline_path=R/'versions/cloudcourt-v24-antes-v25/GameAssembly.dll'
baseline_manifest=json.loads((R/'analysis/v24-build.log').read_text())
p=pefile.PE(str(baseline_path));ex=baseline_manifest['exports']
baseline=RealTriggerEngineV25(0x180000000);baseline.room=False;baseline.online=False
baseline_hand=baseline.hand(0);baseline_ball,baseline_renderer=baseline.waiting()
baseline.frame(baseline_hand,.90)
assert not baseline.q(baseline_hand+0x30) and not baseline.render[baseline_renderer]
assert baseline.analog_calls==[0,0],'v24 native predicate never reaches analog acquisition'
BASELINE_SHA=hashlib.sha256(baseline_path.read_bytes()).hexdigest()
assert BASELINE_SHA==baseline_manifest['modified_sha256']
p,ex=current_pe,current_exports
cases=[]
for base in (0x180000000,0x190000000):
 e=RealTriggerEngineV25(base);hands=[e.hand(0),e.hand(1)]
 for fmt in (2,4):
  for online in (False,True):
   e.room=False;e.online=online;e.flag('online_version_ready',int(online));e.flag('online_format',fmt)
   e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4)
   for side,hand in enumerate(hands):
    e.frame(hand);ball,renderer=e.waiting();e.a_button=True;e.frame(hand)
    assert not e.q(hand+0x30) and not e.render[renderer],'A must not spawn'
    e.a_button=False;e.frame(hand,0.,grip=True)
    assert not e.q(hand+0x30) and not e.render[renderer],'GRAB-only must not spawn'
    e.frame(hand,.59);assert not e.q(hand+0x30) and not e.render[renderer]
    e.frame(hand,.90)
    assert e.q(hand+0x30)==ball and e.q(ball+0xd8)==hand and e.render[renderer]
    assert not e.release_query(hand),'analog-only hold must reach WantsToRelease'
    for pressure in (.45,.40,.36):e.frame(hand,pressure);assert e.q(hand+0x30)==ball
    before=e.released;e.frame(hand,.35);assert not e.q(hand+0x30) and e.release_query(hand) and e.released==before+1
    # Digital-only hardware is retained, independently of analog pressure.
    ball,renderer=e.waiting();e.frame(hand,0.,digital=True);assert e.q(hand+0x30)==ball
    e.frame(hand,0.,grip=True);assert e.q(hand+0x30)==ball,'ordinary native grip holding preserved'
    e.frame(hand);assert not e.q(hand+0x30)
    cases.append(dict(base=hex(base),format=fmt,online=online,hand=side,serve=True))
 # UI exclusion on waiting serve uses the same pointer guard as the lobby.
 e.online=True;e.flag('online_version_ready',1);e.room=False
 ball,renderer=e.waiting();e.ui_block=True;e.frame(hands[0],.9)
 assert not e.q(hands[0]+0x30) and not e.render[renderer]
 e.ui_block=False;e.frame(hands[0]);e.frame(hands[0],.9);assert e.q(hands[0]+0x30)==ball;e.frame(hands[0])
 # Fresh analog-only lobby recalls/transfer still use exactly one owned ball.
 e.room=True;e.flag('online_format',2);left,right=hands
 e.frame(left,0.,grip=True);e.frame(right,0.,grip=True);assert not e.spawned
 e.frame(left,.9);ball=e.q(left+0x30);assert e.spawned==[ball]
 e.frame(right,.9);assert e.q(right+0x30)==ball and not e.q(left+0x30)
 e.frame(left,.9);assert not e.q(left+0x30),'held old hand cannot steal transferred ball'
 for side,hand in enumerate(hands*3):
  e.frame(hand);e.frame(hand,.9);assert e.q(hand+0x30)==ball and e.spawned==[ball]
 e.frame(left);e.frame(right)
 e.ui_block=True;e.frame(left,.9);assert not e.q(left+0x30)
 e.ui_block=False;e.frame(left);e.frame(left,.9);assert e.q(left+0x30)==ball
 # Replacement must reset the latch: .45 on a new controller is not a press.
 old=e.controllers[0];new=e.alloc();e.controllers[0]=new;e.configure(new);e.frame(left,.45)
 assert not e.q(left+0x30);e.frame(left,.6);assert e.q(left+0x30)==ball
 e.frame(left,float('nan'));assert not e.q(left+0x30)
 # Remote hands cannot poll analog or recall the local player's practice ball.
 remote=e.alloc();rt=e.alloc();e.transforms[remote]=rt;e.ptr(remote+0x18,rt)
 e.analog[0]=.9;e.digital[0]=False;e.grips[0]=False;before=tuple(e.analog_calls)
 e.call('lobby_hand_update_hook',remote)
 assert tuple(e.analog_calls)==before and not e.q(remote+0x30) and e.spawned==[ball]
 cases.append(dict(base=hex(base),analog_lobby=True,actual_native_interface_dispatch=True))
assert hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest()==NATIVE
report=dict(passed=True,sha256=NATIVE,cases=cases,native_hand_predicate_stubbed=False,
 delivered_v24_regression_reproduced=True,baseline_sha256=BASELINE_SHA,
 actual_interface_invoker=True,float_analog_independent_of_digital=True,dll_unchanged_during_test=True,
 checks=['analog-only .9 native acquisition','original WantsToRelease/hysteresis','GRAB-only and A cannot spawn',
 'digital-only path','two hands/formats/solo/online','UI excludes serve and lobby acquisition',
 'one owned lobby ball/fresh transfer','native grip hold preserved','hotplug latch reset','NaN releases safely',
 'remote hands never sample analog or recall'],hardware_Quest_tested=False)
(R/'analysis/v25-trigger-integrated-tests.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(passed=True,cases=len(cases),sha256=NATIVE)))
