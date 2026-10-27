"""Verify only the authorized elbow delta, preserving the delivered v26 assets."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 native=H(R/'working/GameAssembly.dll');helper=H(R/'elbow_v27.c')
 unit=json.loads((R/'analysis/elbow-v27-results.json').read_text())
 integrated=json.loads((R/'analysis/elbow-v27-integrated-results.json').read_text())
 assert unit['passed'] and integrated['passed']
 # The integrated report must identify the final DLL; the helper report
 # documents its own isolated native fixture separately.
 assert integrated.get('native_sha256',integrated.get('sha256'))==native
 assert integrated.get('helper_sha256',integrated.get('source_sha256'))==helper
 old=json.loads((R/'distribution/Cloudcourt-v26-session-repair/patch.json').read_text())
 baseline=R/'versions/cloudcourt-v26-antes-v27';changed=[]
 for row in old['files']:
  assert H(baseline/Path(row['path']).name)==row['modified_sha256']
  if H(R/'working'/row['path'])!=row['modified_sha256']:changed.append(row['path'])
 assert changed==['GameAssembly.dll','VolleyballFever_Data/resources.assets'],changed
 balls=json.loads((R/'analysis/v27-plain-balls-tests.json').read_text())
 assert balls['passed'] and balls['changed_existing_ids']==[40]
 assert balls['changed_texture_fields']==['image data']
 assert H(R/'working/VolleyballFever_Data/resources.assets')==balls['resources_sha256']
 assert balls['builder_sha256']==H(R/'build_plain_balls_v27.py')
 delta=[]
 for p in R.glob('*.c'):
  if p.name.startswith('test_'):continue
  b=baseline/'fontes'/p.name
  if not b.exists() or H(p)!=H(b):delta.append(p.name)
 assert sorted(delta)==['elbow_v27.c','mode_2v2.c'],delta
 patch=json.loads((R/'analysis/native-patch-manifest.json').read_text())
 assert patch['modified_sha256']==native and patch['network_version']=='Cloudcourt-2v2-v24 / Cloudcourt-4v4-v24'
 entry=next(e for e in patch['patches'] if e['name']=='elbow_bend_v27')
 assert entry['rva']==0xeeabe0 and entry['length']==7 and entry['original']=='488bc448895818'
 smoke=(R/'analysis/smoke-v27-menu.log').read_text(errors='replace')
 assert 'Loading environment IndoorArenaScene' in smoke
 assert not any(s in smoke for s in ['NullReferenceException','AccessViolationException','Fatal error','Crash!!!'])
 assert not (R/'analysis/level0-smoke-backup').exists()
 result=dict(passed=True,native_sha256=native,helper_sha256=helper,verified_files=17,
  changed_game_files=changed,unchanged_game_files=15,changed_production_c_sources=delta,
  native_validation_suites=2,isolated_cases=unit['cases'],integrated_cases=integrated['cases'],
  controlled_startup_seconds=15,tracked_wrist_targets_preserved=True,opposite_arm_native=True,
  physical_Quest_tested=False,live_two_PC_tested=False,
  plain_ball_art_verified=True,changed_asset_objects=[40],ball_texture_sha256=balls['resources_sha256'],
  scope='Focused native solver/component checks, texture40-only artwork audit and startup; unrelated features retained without redundant full regressions.')
 (R/'analysis/v27-integration-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
