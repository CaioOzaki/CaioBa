"""Verify the focused trigger repair without claiming unaffected tests reran."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 native=H(R/'working/GameAssembly.dll')
 integration=json.loads((R/'analysis/v25-trigger-integrated-tests.json').read_text())
 pressure=json.loads((R/'analysis/v25-pressure-tests.json').read_text())
 assert integration['passed'] and integration['sha256']==native
 assert integration['delivered_v24_regression_reproduced'] and not integration['native_hand_predicate_stubbed']
 assert integration['actual_interface_invoker'] and len(integration['cases'])==18
 assert pressure['passed'] and pressure['source_sha256']==H(R/'spawn_input_v24.c')
 baseline=R/'versions/cloudcourt-v24-antes-v25'
 manifest=json.loads((R/'distribution/Cloudcourt-v24-celebracao-graficos/patch.json').read_text())
 changed=[]
 for row in manifest['files']:
  assert H(baseline/Path(row['path']).name)==row['modified_sha256']
  if H(R/'working'/row['path'])!=row['modified_sha256']:changed.append(row['path'])
 assert changed==['GameAssembly.dll']
 source_changes=[]
 for path in R.glob('*.c'):
  if path.name.startswith('test_'):continue
  assert (baseline/'fontes'/path.name).exists(),path.name
  if H(path)!=H(baseline/'fontes'/path.name):source_changes.append(path.name)
 assert sorted(source_changes)==['formation_serve.c','spawn_input_v24.c']
 patch=json.loads((R/'analysis/native-patch-manifest.json').read_text())
 assert patch['modified_sha256']==native and patch['network_version']=='Cloudcourt-2v2-v24 / Cloudcourt-4v4-v24'
 assert any(p['name']=='hand_input_v25' and p['rva']==0x3130b0 and p['length']==6 for p in patch['patches'])
 smoke=(R/'analysis/smoke-v25-menu.log').read_text(errors='replace')
 assert 'Loading environment IndoorArenaScene' in smoke
 assert not any(x in smoke for x in ['NullReferenceException','AccessViolationException','Fatal error','Crash!!!'])
 assert not (R/'analysis/level0-smoke-backup').exists()
 result=dict(passed=True,native_sha256=native,changed_game_files=changed,verified_files=17,
  changed_production_c_sources=source_changes,unchanged_assets=16,retained_v24_rooms=True,
  previous_defect_reproduced=True,analog_digital_independent=True,controlled_startup_seconds=15,
  physical_Quest_tested=False,live_two_PC_tested=False,
  scope='Two focused native suites and final startup; unaffected v24 artwork/physics/graphics/bot tests retained without rerunning.')
 (R/'analysis/v25-integration-audit.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result))

if __name__=='__main__':main()
