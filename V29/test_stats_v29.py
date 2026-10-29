"""Compile and exercise the exact standalone session-only match stats module."""
from pathlib import Path
import ctypes,json,os,subprocess
R=Path(__file__).resolve().parent
def run():
    out=R/'tools/stats-v29';out.mkdir(exist_ok=True)
    env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(out/'global-cache');env['ZIG_LOCAL_CACHE_DIR']=str(out/'local-cache')
    dll=out/'test-stats-v29.dll'
    p=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(R/'test_stats_v29_harness.c'),'-o',str(dll),'-Wl,--entry=DllMain'],capture_output=True,text=True,env=env)
    assert p.returncode==0,p.stdout+p.stderr
    lib=ctypes.CDLL(str(dll));n=lib.test_stats_v29();assert n>=65,n
    result=dict(passed=True,native_assertions=n,scope='Exact production C with controlled Unity/network identity and UI stubs. No Quest or real two-PC test claim.',
        checks=['ace, direct attack and conservative soft-contact exclusion','controlled local reception and confirmed assisted-set goals','loser-only error attribution','motion and point duplicate suppression','finite/bounded event validation','training/pending/lobby exclusion','best-of-three finalization','retained completed summary after reset','reused rules and online team identity','empty/current/completed UI and one menu notification','root cache cleanup and no per-frame hierarchy searches'])
    (R/'analysis/v29-stats-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()

