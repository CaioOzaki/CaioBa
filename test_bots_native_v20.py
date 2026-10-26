"""Compile and execute the exact v20 bot identity module with engine stubs."""
from pathlib import Path
import json,os,struct,subprocess,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import pefile
from unicorn.x86_const import *
from test_map_v19 import Engine as BaseEngine
from fix_bot_v20 import patch_bot_identity_v20
HARNESS=r'''
typedef unsigned long long U64;
#define EXPORT __declspec(dllexport)
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
#define INT(o,n) (*(int*)((char*)(o)+(n)))
static U64 original_base;
static U64 base(void){return original_base;}
#define FN(r,t) ((t)(base()+(r)))
static void* rooted(unsigned h){return h?FN(0x14ac80,void*(*)(unsigned))(h):0;}
static void root_set(unsigned* h,void* obj){if(*h)FN(0x14ac70,void(*)(unsigned))(*h);*h=obj?FN(0x14ac90,unsigned(*)(void*,_Bool))(obj,0):0;}
#include "../bots_v20.c"
EXPORT void configure(U64 b){original_base=b;}
EXPORT int DllMain(void* m,unsigned why,void* reserved){return 1;}
'''
POOL=[39,12,30,21,15,18,0,45,6]


def compile_harness():
    source=R/'tools/b20.c';output=R/'tools/b20.dll';source.write_text(HARNESS,encoding='utf-8')
    zig=R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'
    env=dict(os.environ);env['ZIG_GLOBAL_CACHE_DIR']=env['ZIG_LOCAL_CACHE_DIR']=str(R/'tools/zig-cache-v13')
    command=[str(zig),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(source),'-o',str(output),'-Wl,--entry=DllMain']
    p=subprocess.run(command,capture_output=True,text=True,env=env)
    assert p.returncode==0,(p.stdout,p.stderr)
    return pefile.PE(str(output))


class BotEngine(BaseEngine):
    def __init__(self,b,q):
        self.roots={};self.boxes=[];self.values={};super().__init__(b,q)
    def mask(self):return struct.unpack('<I',self.u.mem_read(self.ex['bot_roster_mask_v20'],4))[0]
    def hook(self,u,addr,size,data):
        r=addr-self.b;a,b=[u.reg_read(x) for x in (UC_X86_REG_RCX,UC_X86_REG_RDX)]
        if r==0x14ac80:self.ret(self.roots[a])
        elif r==0x14ac70:self.roots.pop(a);self.ret()
        elif r==0x14ac90:
            h=max(self.roots,default=0)+1;self.roots[h]=a;self.ret(h)
        elif r==0x14ba70:
            value=struct.unpack('<i',u.mem_read(b,4))[0] if b else None
            result=self.alloc();self.values[result]=value;self.boxes.append((a,b,value));self.ret(result)
        else:super().hook(u,addr,size,data)
    def boxed(self,value):
        raw=self.alloc();self.u.mem_write(raw,struct.pack('<i',value));result=self.call('bot_character_box_hook',self.klass,raw)
        return self.values[result],raw


def run():
    q=compile_harness();cases=0;seen=set()
    slots=[(team,slot) for team in range(2) for slot in range(4)]
    formats={'solo_2v2':[(0,2),(1,0),(1,2)],'online_2v2':[(0,2),(1,2)],
             'solo_4v4':[(0,1),(0,2),(0,3)]+[(1,i) for i in range(4)],'online_4v4':[(0,2),(0,3),(1,2),(1,3)],'max_court':slots}
    for base in (0x180000000,0x190000000):
        e=BotEngine(base,q);e.call('configure',base);rules=e.alloc()
        for requested in range(48):
            for format,active in formats.items():
                e.call('bots_roster_reset_v20',rules);chosen=[]
                for team,slot in active:
                    e.call('bots_spawn_begin_v20',rules,team,slot)
                    selected,_=e.boxed(requested);assert selected in POOL
                    chosen.append(selected);seen.add(selected)
                    e.call('bots_spawn_end_v20')
                    mask=e.mask();v,pointer=e.boxed(0x1234567)
                    assert v==0x1234567 and e.boxes[-1][1]==pointer and e.mask()==mask
                assert len(chosen)==len(set(chosen)),(base,format,requested,chosen)
                assert e.mask().bit_count()==len(active)
                # No new choice occurs on a rally/rotation/human team swap.
                mask=e.mask();e.call('bots_spawn_end_v20');assert e.mask()==mask
                cases+=1
        for team,slot in [(-1,0),(2,0),(0,-1),(1,4)]:
            e.call('bots_spawn_begin_v20',rules,team,slot);mask=e.mask();v,p=e.boxed(-77)
            assert v==-77 and e.mask()==mask and e.boxes[-1][1]==p
        e.call('bots_spawn_begin_v20',0,0,0);v,_=e.boxed(47);assert v==47
        different=e.alloc();e.call('bots_spawn_begin_v20',different,0,0);assert e.mask()==0
        v,_=e.boxed(0);assert v==POOL[0] and e.mask()==1;e.call('bots_spawn_end_v20')
        e.call('bots_roster_reset_v20',different);assert e.mask()==0
    assert seen==set(POOL),'A profile is never selectable.'
    # Only characterIndex boxing changes; PhotonViewID/team/slot boxing is untouched.
    original=R/'backup/GameAssembly.dll';p=pefile.PE(str(original));result=bytearray(original.read_bytes())
    exports={e.name.decode():e.address for e in q.DIRECTORY_ENTRY_EXPORT.symbols if e.name};patches=[]
    patch_bot_identity_v20(result,p,patches,exports,0x194f000)
    assert len(patches)==1 and patches[0]['rva']==0x25513d
    for site in (0x255043,0x2550af,0x2550f9):
        off=p.get_offset_from_rva(site);assert result[off:off+5]==p.get_data(site,5)
    report=dict(passed=True,roster_cases=cases,ASLR_bases=['0x180000000','0x190000000'],database_indices=POOL,
                checks=['all 48 repeated RNG results without duplicate identities','solo/online 2v2/4v4 and full eight-slot court',
                        'all nine identities selectable','invalid slots preserve original boxing','context ends after spawn',
                        'same roster survives rally/rotation/team-swap boundaries','explicit match/clear reset and different rules reset',
                        'only characterIndex boxing call redirected; other three integer fields remain original'],
                scope='Compiled x64 helper with controlled allocation/boxing; original Photon RPC carries the chosen database index.')
    (R/'analysis/v20-bot-native-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':run()
