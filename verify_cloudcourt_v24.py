"""Audit final native evidence, composed assets and unchanged v23 game files."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
from package_cloudcourt_v24 import NAMES
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 native=H(R/'working/GameAssembly.dll')
 regression=json.loads((R/'analysis/v24-regression.json').read_text())
 assert regression['passed'] and len(regression['suites'])==9 and regression['native_sha256']==native
 for name in ['v24-bot-target-integrated-tests.json','v24-spawn-input-tests.json']:
  report=json.loads((R/'analysis'/name).read_text())
  assert report['passed'] and report['sha256']==native,name
 for name in ['v24-bot-target-native-tests.json','v24-sleeves-assets-tests.json',
              'v24-sleeves-native-tests.json','v24-graphics-tests.json','v24-graphics-rendering-unity.json']:
  assert json.loads((R/'analysis'/name).read_text())['passed'],name
 assert H(R/'graphics_v24.c')==H(R/'tools/u24-graphics/graphics_v24.c')
 bot=json.loads((R/'analysis/v24-bot-target-native-tests.json').read_text())
 assert bot['production_sha256']==H(R/'hand_visuals_v21.c')
 composed=json.loads((R/'visuals-v24-integrated/build-report.json').read_text())
 for name in ['resources.assets','level0']:
  assert H(R/'working/VolleyballFever_Data'/name)==composed[name]['sha256']
 changed=[name for name in NAMES if H(R/'working'/name)!=H(R/'versions/cloudcourt-v23-antes-v24'/Path(name).name)]
 assert sorted(changed)==['GameAssembly.dll','VolleyballFever_Data/level0','VolleyballFever_Data/resources.assets']
 assert H(R/'spin_mod.c')==H(R/'versions/cloudcourt-v23-antes-v24/fontes/spin_mod.c')
 rays=json.loads((R/'analysis/v24-graphics-unity.json').read_text())['rows']
 assert len(rays)==6 and all(x['top_hit_is_target'] and x['unity_pointer_click_invoked'] for x in rays)
 assert rays[-1]['control']=='Done' and not rays[-1]['panel_after']
 (R/'analysis/v24-ui-raycast-tests.json').write_text(json.dumps(dict(passed=True,
  rows=rays,actual_Unity_CurvedUI_rays_and_pointer_clicks=True,headset_tested=False),indent=2))
 smoke=(R/'analysis/smoke-v24-menu.log').read_text(errors='replace')
 assert 'Loading environment IndoorArenaScene' in smoke
 for bad in ['NullReferenceException','AccessViolationException','Fatal error','Crash!!!']:assert bad not in smoke,bad
 assert not (R/'analysis/level0-smoke-backup').exists()
 assert not (R/'analysis/terrain-smoke-backup').exists()
 result=dict(passed=True,native_sha256=native,verified_game_files=len(NAMES),
  changed_game_files=changed,unchanged_game_files=len(NAMES)-len(changed),
  composed_assets={k:v['sha256'] for k,v in composed.items()},
  source_sha256={p.name:H(p) for p in R.glob('*.c') if not p.name.startswith('test_')},
  original_physics_source_unchanged=True,controlled_startup_seconds=15,
  graphics_probe_source_matches_final=True,room_namespaces=['Cloudcourt-2v2-v24','Cloudcourt-4v4-v24'],
  physical_Quest_tested=False,live_two_PC_tested=False)
 (R/'analysis/v24-integration-audit.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(dict(passed=True,native_sha256=native,verified_game_files=17,changed_game_files=changed)))

if __name__=='__main__':main()
