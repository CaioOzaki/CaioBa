"""Compile exact new production module and verify isolated v29 asset safety."""
from pathlib import Path
import ctypes,json,os,subprocess,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_bots_refine_v29 import build_resources_v29

def run():
    out=R/'tools/bots-refine-v29';out.mkdir(exist_ok=True)
    env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(out/'global-cache');env['ZIG_LOCAL_CACHE_DIR']=str(out/'local-cache')
    dll=out/'test-bots-v29.dll'
    p=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(R/'test_bots_refine_v29_harness.c'),'-o',str(dll),'-Wl,--entry=DllMain'],capture_output=True,text=True,env=env)
    assert p.returncode==0,p.stdout+p.stderr
    lib=ctypes.CDLL(str(dll));decisions=lib.test_bot_decisions_v29();assert decisions>30,decisions
    visuals=lib.test_bot_visuals_v29();assert visuals>35,visuals
    audio=lib.test_bot_audio_v29();assert audio>=10,audio
    source=R/'versions/cloudcourt-v28-antes-v29/resources.assets'
    f=UnityPy.load(str(source)).file;assets=build_resources_v29(f,R/'visuals-v29-bots')
    assert len(assets['callouts'])==10
    raw=f.save();loaded=UnityPy.load(raw).file;again=build_resources_v29(loaded);assert again['idempotent']
    (R/'visuals-v29-bots/resources.assets').write_bytes(raw)
    result=dict(passed=True,native_decision_assertions=decisions,native_visual_assertions=visuals,native_audio_assertions=audio,assets=assets,
                scope='Native x64 controlled ownership/Unity API fixture and serialized asset roundtrip. No Quest or real two-PC validation.',
                checks=['ballistic anticipation and bounded malformed ball rejection','one receiver with stable id tie-break and hysteresis','reachable human keeps ball; unreachability fills gap','native ownership/master/serve/Bomb guards','quartet setter and attack receiver retained','support goals separated; no root writes','Mine!/Set! cooldown expiry and serve-hide','nine character identities and reversible small head signatures','thumbs-up/gaze priority','cache has no per-frame child search','reset removes roots and stale decisions','ten default-disabled visual children; existing artwork/physics untouched'])
    (R/'analysis/v29-bots-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
