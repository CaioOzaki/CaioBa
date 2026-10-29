"""v29 adapter around unchanged v28 native rules regression, never live Unity.

Only Unity/Photon/preferences boundary APIs added by v29 are stubbed. Native
GameRules, integrated hooks, serve coroutine, roster and Bomb fuse paths run.
"""
from pathlib import Path
import collections,hashlib,inspect,json,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import test_rules_bomb_v28 as old
from unicorn import UC_HOOK_MEM_INVALID
from unicorn.x86_const import *


class Rules29(old.Rules28):
    latest=None
    all_boundary_hits=collections.Counter()
    def __init__(self,*args,**kwargs):
        Rules29.latest=self;self.boundary_hits=collections.Counter();self.trace=collections.deque(maxlen=128);self.calltrace=collections.deque(maxlen=40)
        super().__init__(*args,**kwargs)
    def hook(self,u,addr,size,user):
        self.trace.append(addr-self.b)
        if '--trace' in sys.argv and u.mem_read(addr,1)==b'\xe8':
            import struct
            self.calltrace.append([hex(addr-self.b),hex(addr+5+struct.unpack('<i',u.mem_read(addr+1,4))[0]-self.b)])
        r=addr-self.b;a=u.reg_read(UC_X86_REG_RCX)
        # dump.cs: UnityEngine.Object.op_Implicit(Object exists), not a rule.
        if r==0xa0bfb0:self.mark('UnityEngine.Object.op_Implicit');self.ret(bool(a))
        elif r==0x94f3d0:
            self.mark('UnityEngine.GameObject.Find');self.ret(0) # no optional training target in rules-only fixture
        elif r in (0xb72b40,0xb72ae0,0xb72a20,0xb72960):
            # Verified UnityEngine.Time getters; a frozen deterministic clock.
            self.mark(hex(r));self.ret(f=1/60 if r==0xb72960 else 10.)
        elif r==0x14ba70:
            import struct
            self.box_value=struct.unpack('<i',u.mem_read(u.reg_read(UC_X86_REG_RDX),4))[0];self.mark('il2cpp_value_box');self.ret(self.alloc())
        else:super().hook(u,addr,size,user)
    def mark(self,name):
        self.boundary_hits[name]+=1;Rules29.all_boundary_hits[name]+=1
    def call(self,name,*args):
        self.last_entry=name
        return super().call(name,*args)


def trace_first():
    try:Rules29(0x180000000)
    except Exception as err:
        e=Rules29.latest
        import capstone
        dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64)
        rows=[]
        for rva in e.trace:
            code=bytes(e.u.mem_read(e.b+rva,15));i=next(dis.disasm(code,e.b+rva));rows.append(f'{rva:x}: {i.mnemonic} {i.op_str}')
        result=dict(error=str(err),rip=hex(e.u.reg_read(UC_X86_REG_RIP)-e.b),
                    registers={n:hex(e.u.reg_read(r)) for n,r in [('rax',UC_X86_REG_RAX),('rcx',UC_X86_REG_RCX),('rdx',UC_X86_REG_RDX)]},trace=rows)
        (R/'analysis/v29-rules-fixture-trace.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));return
    raise AssertionError('Expected original fixture to expose the first missing API boundary')


def run():
    native=R/'working/GameAssembly.dll';start=hashlib.sha256(native.read_bytes()).hexdigest()
    # Reuse the unchanged complete rule scenarios while adapting only versioned
    # expectations and the report output; never patch historical files/reports.
    source=inspect.getsource(old.run).replace('Rules28(', 'Rules29(')
    source=source.replace("fmt}-v28'", "fmt}-v29'")
    source=source.replace('v28-rules-bomb-tests.json','v29-rules-integrated-tests.json')
    source=source.replace('all four v28 room namespaces/prefabs','all four v29 room namespaces/prefabs')
    scope=dict(old.__dict__);scope.update(Rules29=Rules29)
    exec(compile(source,str(R/'test_rules_integrated_v29.py')+':inherited-scenarios','exec'),scope)
    try:scope['run']()
    except Exception as err:
        e=Rules29.latest
        import capstone
        dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64);rows=[]
        for r in e.trace:
            i=next(dis.disasm(bytes(e.u.mem_read(e.b+r,15)),e.b+r));rows.append(f'{r:x}: {i.mnemonic} {i.op_str}')
        report=dict(error=str(err),last_entry=e.last_entry,calltrace=list(e.calltrace),boundaries=dict(e.boundary_hits),registers={n:hex(e.u.reg_read(r)) for n,r in [('rip',UC_X86_REG_RIP),('rax',UC_X86_REG_RAX),('rcx',UC_X86_REG_RCX),('rdx',UC_X86_REG_RDX)]},trace=rows)
        (R/'analysis/v29-rules-fixture-next-trace.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));raise
    pool=[39,12,30,21,15,18,0,45,6];seen=set();rosters=0;selections=0
    for base in (0x180000000,0x190000000):
        e=Rules29(base)
        e.call('solo_awake_hook',e.page);assert e.visible[e.q(e.page+0x58)]
        for select,stage in [('solo_night_hook',2),('solo_day_hook',4),('solo_bomb_v28_hook',3)]:
            e.call(select,e.page);assert e.val('solo_stage')==stage and not e.visible[e.q(e.page+0x58)]
            e.call('solo_back_hook',e.page);assert e.val('solo_stage')==0 and e.visible[e.q(e.page+0x58)]
        for requested in list(range(9))+[47]:
            e.call('bots_roster_reset_v20',e.game);chosen=[]
            for team in (0,1):
                for slot in range(4):
                    e.call('bots_spawn_begin_v20',e.game,team,slot);raw=e.alloc();e.integer(raw,requested)
                    e.call('bot_character_box_hook',e.klass,raw);chosen.append(e.box_value);seen.add(e.box_value);selections+=1
                    e.call('bots_spawn_end_v20');e.integer(raw,0x1234567);e.call('bot_character_box_hook',e.klass,raw);assert e.box_value==0x1234567
            assert len(set(chosen))==8 and set(chosen)<=set(pool);rosters+=1
        for team,slot in [(-1,0),(2,0),(0,-1),(1,4)]:
            e.call('bots_spawn_begin_v20',e.game,team,slot);raw=e.alloc();e.integer(raw,-77);e.call('bot_character_box_hook',e.klass,raw);assert e.box_value==-77
    assert seen==set(pool) and hashlib.sha256(native.read_bytes()).hexdigest()==start,'DLL changed during regression'
    path=R/'analysis/v29-rules-integrated-tests.json';result=json.loads(path.read_text());assert result['sha256']==start
    result['identity_rosters']=rosters;result['identity_selections']=selections
    result['fixture_adapter']=dict(inherited='test_rules_bomb_v28.py (unchanged)',added_API_boundaries=dict(Rules29.all_boundary_hits),production_rules_hooks_stubbed=[],extras_visible_only_at_stage_zero=True)
    path.write_text(json.dumps(result,indent=2));print(json.dumps(dict(identity_rosters=rosters,identity_selections=selections,sha256=start,fixture_adapter=result['fixture_adapter']),indent=2))


if __name__=='__main__':trace_first() if '--trace' in sys.argv else run()
