"""Preserve v28's native ball lifecycle suite against the full integrated v30 DLL.

Added v30 menu-reset calls reach Unity's optional target lookup and clocks.
This adapter supplies those API boundaries; no ball/lobby/reset hook is skipped.
"""
from pathlib import Path
import collections,inspect,json,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import test_ball_spawn_v28 as old
from unicorn.x86_const import *


class Spawn30(old.SpawnEngine):
    latest=None
    boundary_hits=collections.Counter()
    def __init__(self,*args,**kwargs):
        Spawn30.latest=self;self.trace=collections.deque(maxlen=24);self.entry='construct'
        super().__init__(*args,**kwargs)
    def hook(self,u,addr,size,user):
        r=addr-self.b;self.trace.append(hex(r));a=u.reg_read(UC_X86_REG_RCX)
        if r==0x94f3d0:
            Spawn30.boundary_hits['UnityEngine.GameObject.Find']+=1;self.ret(0)
        elif r in (0xb72b40,0xb72ae0,0xb72a20,0xb72960):
            Spawn30.boundary_hits[hex(r)]+=1;self.ret(f=1/60 if r==0xb72960 else 10.)
        else:super().hook(u,addr,size,user) # retains original material and Object.alive/dead assertions
    def call(self,name,*args):
        self.entry=name;return super().call(name,*args)


def run():
    source=inspect.getsource(old.run).replace('SpawnEngine(', 'Spawn30(')
    source=source.replace('v28-ball-spawn-integrated-tests.json','v30-ball-spawn-integrated-tests.json')
    scope=dict(old.__dict__);scope['Spawn30']=Spawn30
    exec(compile(source,str(R/'test_ball_spawn_integrated_v30.py')+':inherited-scenarios','exec'),scope)
    try:scope['run']()
    except Exception as err:
        e=Spawn30.latest
        report=dict(error=str(err),entry=e.entry,rip=hex(e.u.reg_read(UC_X86_REG_RIP)),trace=list(e.trace),boundary_hits=dict(Spawn30.boundary_hits))
        (R/'analysis/v30-ball-spawn-fixture-trace.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));raise
    path=R/'analysis/v30-ball-spawn-integrated-tests.json';result=json.loads(path.read_text())
    result['fixture_adapter']=dict(inherited='test_ball_spawn_v28.py (unchanged)',added_Unity_boundaries=dict(Spawn30.boundary_hits),production_hooks_stubbed=[])
    path.write_text(json.dumps(result,indent=2));print(json.dumps(result['fixture_adapter'],indent=2))


if __name__=='__main__':run()
