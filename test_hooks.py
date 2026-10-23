"""Emulate patched x64 hooks against engine stubs, without running the game.
Checks Windows ABI, relocated code/data, accepted local hit and offline gate.
"""
import sys,pathlib,struct,json,math
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_64,UC_HOOK_CODE
from unicorn.x86_const import *
p=pefile.PE(str(R/'working/GameAssembly.dll'))
manifest=json.loads((R/'analysis/native-patch-manifest.json').read_text())
patches={x['name']:x for x in manifest['patches']}
B=0x180000000; HEAP=0x300000000; STACK=0x400000000; STOP=HEAP+0xf000; RETURN=HEAP+0xe000
def run(offline=True,hand=(3,0,0),accepted=True,base=B,frames=90,fps=90,mod_online=False,format=2,received=None):
    u=Uc(UC_ARCH_X86,UC_MODE_64);u.mem_map(base,(p.OPTIONAL_HEADER.SizeOfImage+4095)//4096*4096)
    u.mem_write(base,p.get_memory_mapped_image())
    # Simulate Windows ASLR, including the new helper pointer relocation.
    if base!=B:
        for block in p.DIRECTORY_ENTRY_BASERELOC:
            for entry in block.entries:
                if entry.type==10:
                    val=struct.unpack('<Q',u.mem_read(base+entry.rva,8))[0]
                    u.mem_write(base+entry.rva,struct.pack('<Q',val+base-B))
    u.mem_write(base+manifest['exports']['online_version_ready'],struct.pack('<i',int(mod_online)))
    u.mem_write(base+manifest['exports']['online_format'],struct.pack('<i',format))
    u.mem_map(HEAP,0x10000);u.mem_map(STACK,0x100000)
    body=HEAP+0x100;part=HEAP+0x500;ball=HEAP+0x1000;collision=HEAP+0x2000;contacts=HEAP+0x2500;rb=HEAP+0x3000;local=HEAP+0x3500
    def ptr(a,v):u.mem_write(a,struct.pack('<Q',v))
    def vec(a,v):u.mem_write(a,struct.pack('<fff',*v))
    def rv(a):return struct.unpack('<fff',u.mem_read(a,12))
    u.mem_write(part+0x18,struct.pack('<i',3));u.mem_write(ball+0x88,b'\1')
    ptr(ball+0x98,rb);ptr(ball+0x30,local);vec(ball+0x8c,(0,0,0))
    ptr(collision+0x40,contacts);u.mem_write(collision+0x38,struct.pack('<i',1));ptr(contacts+0x18,1);vec(contacts+0x20,(0,-.105,0))
    state={'vel':{rb:(0,0,0)},'omega':{rb:(0,0,0),local:(0,0,0)},'motion':0,'original':0,'late':0,'max':{},'engine_calls':0,'velocity_writes':0,'angular_writes':0}
    # Stub continuation returns from the simulated original collision routine.
    u.mem_write(RETURN,b'\x48\x81\xc4\x88\x00\x00\x00\xc3')
    def ret():
        sp=u.reg_read(UC_X86_REG_RSP);target=struct.unpack('<Q',u.mem_read(sp,8))[0]
        u.reg_write(UC_X86_REG_RSP,sp+8);u.reg_write(UC_X86_REG_RIP,target)
    def floatret(f):u.reg_write(UC_X86_REG_XMM0,struct.unpack('<I',struct.pack('<f',f))[0]);ret()
    def hook(uc,address,size,user):
        rva=address-base;rcx=u.reg_read(UC_X86_REG_RCX);rdx=u.reg_read(UC_X86_REG_RDX)
        if rva in [0x61fbf0,0x77fe10,0xb72960,0xec5a10,0xec5870,0xec5b90,0xeea0e0,0xec5940,0xec5cd0,0xec60d0,0xec5ea0]:state['engine_calls']+=1
        if rva==0x61fbf0:u.reg_write(UC_X86_REG_RAX,int(offline));ret()
        elif rva==0x77fe10:floatret(.105)
        elif rva==0xb72960:floatret(1/fps)
        elif rva in (0xec5a10,0xec5870,0xec5b90):
            values=(0,0,0) if rva==0xec5a10 else state['omega' if rva==0xec5870 else 'vel'].get(rdx,(0,0,0))
            vec(rcx,values);u.reg_write(UC_X86_REG_RAX,rcx);ret()
        elif rva==0xeea0e0:vec(rcx,hand);u.reg_write(UC_X86_REG_RAX,rcx);ret()
        elif rva==0xec5940:u.reg_write(UC_X86_REG_RAX,0);ret()
        elif rva==0xec5cd0:state['omega'][rcx]=rv(rdx);state['angular_writes']+=1;ret()
        elif rva==0xec60d0:state['vel'][rcx]=rv(rdx);state['velocity_writes']+=1;ret()
        elif rva==0xec5ea0:state['max'][rcx]=u.reg_read(UC_X86_REG_XMM1)&0xffffffff;ret()
        elif rva==0x77e5c0:
            state['motion']+=1;state['wire_context']=struct.unpack('<I',u.mem_read(u.reg_read(UC_X86_REG_RSP)+0x40,4))[0];ret()
        elif rva==patches['client_motion']['trampoline']:
            state['decoded_context']=struct.unpack('<I',u.mem_read(u.reg_read(UC_X86_REG_RSP)+0x38,4))[0];ret()
        elif rva==patches['collision']['trampoline']:
            state['original']+=1
            if not accepted:ret();return
            sp=u.reg_read(UC_X86_REG_RSP)-0x90;u.reg_write(UC_X86_REG_RSP,sp);ptr(sp,RETURN)
            u.reg_write(UC_X86_REG_RCX,ball);u.reg_write(UC_X86_REG_RDX,HEAP+0x4000);u.reg_write(UC_X86_REG_R8,HEAP+0x4100);u.reg_write(UC_X86_REG_R9,1)
            vec(HEAP+0x4000,(0,0,0));vec(HEAP+0x4100,(10,0,0));u.mem_write(sp+0x28,b'\0'*0x28)
            u.reg_write(UC_X86_REG_RIP,base+patches['accepted_local_hit']['hook'])
        elif rva==patches['late']['trampoline']:state['late']+=1;ret()
    u.hook_add(UC_HOOK_CODE,hook)
    def call(rva,args):
        sp=STACK+0x80008;u.reg_write(UC_X86_REG_RSP,sp);ptr(sp,STOP)
        for reg,value in zip([UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9],args):u.reg_write(reg,value)
        for i,value in enumerate(list(args)[4:]+[0]*6):ptr(sp+0x28+i*8,value)
        u.emu_start(base+rva,STOP,count=100000)
        assert u.reg_read(UC_X86_REG_RIP)==STOP,'Hook did not return normally'
    if received is None:call(0xeeb3b0,[body,part,ball,collision])
    else:
        v=HEAP+0x4000;vec(v,(10,0,0));call(0x77de30,[ball,v,v,1,0,0,received,0])
    spin=state['omega'][rb]
    count=state['engine_calls'];angular=state['angular_writes']
    state['vel'][rb]=(10,0,0);state['vel'][local]=(10,0,0)
    for frame in range(frames):call(0x77ec30,[ball,0])
    state['frame_engine_calls']=state['engine_calls']-count
    assert state['angular_writes']==angular,'Must not write angular velocity per frame'
    return spin,state
spin,s=run();assert spin[2]>17 and s['motion']==1 and s['original']==1 and s['late']==90 and s['vel'][HEAP+0x3000][1]>0
assert s['velocity_writes']==30 and s['frame_engine_calls']<=240
at90=s['vel'][HEAP+0x3000];calls90=s['frame_engine_calls']
opposite,s=run(hand=(-3,0,0));assert opposite[2]<-17
straight,s=run(hand=(0,3,0));assert max(map(abs,straight))<1e-5
online,s=run(offline=False);assert online==(0,0,0) and s['motion']==1 and not s['max']
rejected,s=run(accepted=False);assert rejected==(0,0,0) and s['motion']==0
relocated,s=run(base=0x190000000);assert abs(relocated[2]-spin[2])<1e-5
for rate in [30,10]:
    _,s=run(frames=rate,fps=rate)
    assert max(abs(a-b) for a,b in zip(at90,s['vel'][HEAP+0x3000]))<0.001,'Trajectory should be consistent across frame rates'
report={'passed':9,'cases':['accepted local brush','opposite brush','normal hit','online original behavior','rejected hit unchanged','ASLR relocated image','30 Hz cadence','trajectory at 30 FPS','trajectory at 10 FPS'],'spin_rad_s':spin,'engine_calls_per_second_at_90_fps':calls90,'v1_engine_calls_same_case':630,'reduction_percent':100*(1-calls90/630),'scope':'Real patched machine code in CPU emulator with engine stubs. Does not replace VR playtesting.'}
(R/'analysis/hook-test-results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

for fmt in (2,4):
 for addr in (B,0x190000000):
  hit,a=run(offline=False,mod_online=True,format=fmt,base=addr)
  remote,b=run(offline=False,mod_online=True,format=fmt,base=addr,received=a['wire_context'])
  assert hit==remote and hit[2]>16
  assert b['decoded_context']==0
  for rb in (HEAP+0x3000,HEAP+0x3500):
   assert a['vel'][rb]==b['vel'][rb] and a['vel'][rb][1]>0
  assert a['velocity_writes']==60 and b['velocity_writes']==60
  _,rejected=run(offline=False,mod_online=True,format=fmt,base=addr,accepted=False)
  assert not rejected['angular_writes'] and not rejected['velocity_writes']
print('PASS: v13 spin encoded/decoded between peers, both bodies, 2v2/4v4, ASLR and rejected hits')
