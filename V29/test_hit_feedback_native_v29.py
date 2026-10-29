"""Read-only original-byte/ABI audit + in-memory narrow call patch verification."""
from pathlib import Path
import sys,struct,json
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import pefile,capstone
from fix_hit_feedback_v29 import HIT_CALLS_V29,patch_hit_calls_v29
p=pefile.PE(str(R/'backup/GameAssembly.dll'))
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64)
def instructions(site,size):return list(md.disasm(p.get_data(site,size),site))
def calls(site,size):
 return [(i.address,int(i.op_str,16)) for i in instructions(site,size) if i.mnemonic=='call' and i.op_str.startswith('0x')]
body_calls=calls(0xeeb3b0,0x2330)
assert [(a,t) for a,t in body_calls if t==0xa3800]==[(0xeed321,0xa3800),(0xeed386,0xa3800)]
assert (0xeed250,0x77e5c0) in body_calls
assert not any(t==0xeefd80 for _,t in body_calls),'haptics are expected to be inlined'
assert (0x77e75f,0x26c610) in calls(0x77e5c0,0x280),'original accepted motion calls AudioSystem.PlayEffect'
# Verify native constructors/owning hosts and the exact coroutine overload.
for site,size,target in [(0x383c90,0xb5,0x383bf0),(0x383c90,0xb5,0xa0a0c0),(0x383c90,0xb5,0xa0a5e0),(0x385110,0xf3,0x384fd0),(0x385110,0xf3,0xa0a0c0),(0x385110,0xf3,0xa0a5e0)]:
 assert any(t==target for _,t in calls(site,size)),(hex(site),hex(target))
oc=[i.op_str for i in instructions(0x383c90,0xb5)];op=[i.op_str for i in instructions(0x385110,0xf3)]
assert 'rdi, qword ptr [rbx + 0x20]' in oc and 'qword ptr [rbx + 0x28], rax' in oc
assert 'rdi, qword ptr [rbx + 0x48]' in op and 'qword ptr [rbx + 0x58], rax' in op
# Oculus completion explicitly zeroes amplitude. OpenVR uses finite impulses.
assert (0x39e56e,0x453260) in calls(0x39e460,0x130)
assert any(i.address==0x39e568 and i.mnemonic=='xorps' and i.op_str=='xmm1, xmm1' for i in instructions(0x39e460,0x130))
assert (0x39e3c9,0xeb83a0) in calls(0x39e2f0,0x120)
# Apply helper to an in-memory copy. Exactly the two five-byte call instructions
# may change; build/installation files remain untouched.
original=p.__data__[:];result=bytearray(original);patches=[];exports={'hit_haptic_dispatch_v29':0x13000};delta=0x194f000
patch_hit_calls_v29(result,p,patches,exports,delta)
allowed=set()
for _,site,target,name in HIT_CALLS_V29:
 offset=p.get_offset_from_rva(site);allowed.update(range(offset,offset+5))
 assert result[offset:offset+5]==b'\xe8'+struct.pack('<i',exports[name]+delta-site-5)
assert len(patches)==2 and all(k in allowed for k,(a,b) in enumerate(zip(original,result)) if a!=b)
class Corrupt:
 def get_data(self,*args):return b'\x90'*5
try:patch_hit_calls_v29(bytearray(32),Corrupt(),[],exports,delta)
except AssertionError:pass
else:raise AssertionError('patch must refuse unknown original calls')
r=dict(passed=True,original_haptics_inlined=True,exact_accepted_hit_sites=[hex(s) for _,s,_,_ in HIT_CALLS_V29],original_motion_audio_call_verified=True,oculus_openvr_coroutine_abi_ownership_and_completion_verified=True,patch_changes_only_two_call_instructions=True,unknown_original_bytes_refused=True,no_game_files_modified=True)
(R/'analysis/v29-hit-feedback-native-audit.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))

