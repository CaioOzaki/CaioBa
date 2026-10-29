"""Bind v29 native, asset, desktop and preservation evidence to final files."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PREVIOUS_ZIP='b96b0baea6ff4e42977fb88cd4e789931aef1441f7a5c15d9f38af9e3d1323b0'
FOCUSED={
 'v29-training-tests.json':['training_v29.c','build_training_v29.py'],
 'v29-bots-tests.json':['bots_refine_v29.c','build_bots_refine_v29.py'],
 'v29-hit-feedback-tests.json':['hit_feedback_v29.c'],
 'v29-hit-feedback-native-audit.json':['hit_feedback_v29.c'],
 'v29-stats-tests.json':['stats_v29.c'],
 'v29-rewards-native-tests.json':['rewards_v29.c'],
 'v29-rewards-art-tests.json':['build_rewards_art_v29.py'],
 'v29-refinement-assets-tests.json':['build_refinement_ui_v29.py','build_assets_v29.py']}
ROOMS=['Cloudcourt-2v2-v29','Cloudcourt-4v4-v29','Cloudcourt-Bomb-2v2-v29','Cloudcourt-Bomb-4v4-v29']
def read_report(name):
 path=R/'analysis'/name
 d=json.loads(path.read_text(encoding='utf-8-sig'))
 assert d.get('passed') is True,('Failed or incomplete validation',name)
 return d
def verify():
 from package_cloudcourt_v29 import NAMES
 from build_assets_v29 import FILES,MODIFIED
 native=H(R/'working/GameAssembly.dll')
 manifest=json.loads((R/'analysis/native-patch-manifest.json').read_text(encoding='utf-8-sig'))
 assert manifest['modified_sha256']==native,'Native manifest is stale'
 exports=manifest.get('exports',{})
 assert 'customization_stats_v28' not in exports and 'probe_command' not in exports,'Debug probe exported in release'
 for name in ('stats_prepare_v29','stats_motion_v29','stats_point_v29','stats_tick_v29','training_begin_v29','rewards_progress_v29'):
  assert name in exports,('Missing integrated feature',name)
 integrated=read_report('v29-native-integration.json')
 assert integrated['sha256']==native,'Integrated native report is stale'
 assert integrated['patch_count']==len(manifest['patches'])
 assert integrated['hookcontracts'],'Hook contracts were not verified'
 reports={};source_hashes={}
 for name,dependencies in FOCUSED.items():
  report=read_report(name);reports[name]=report;path=R/'analysis'/name
  for source in dependencies:
   source_hashes[source]=H(R/source)
   assert path.stat().st_mtime_ns>=(R/source).stat().st_mtime_ns,('Fixture predates its production source; rerun it',name,source)
 # Where the focused fixture records a digest, compare bytes rather than dates.
 assert reports['v29-training-tests.json']['production_sha256']==H(R/'training_v29.c')
 assert reports['v29-rewards-art-tests.json']['production_sha256']==H(R/'build_rewards_art_v29.py')
 ui=read_report('v29-refinement-unity-release.json')
 assert len(ui['visits'])==2 and len(ui['settings'])==8,'Retained menu/settings probe incomplete'
 assert ui['preferences_restored'] is True and ui['headset_or_two_pc_test'] is False
 assert all(k in ui['v29'] and ui['v29'][k] for k in ('selector','newmenus','practice','feed','flight','target','wear','ordinary')),'v29 desktop checks incomplete'
 logs=[R/'analysis/v29-release-unity.log']
 for p in logs:
  assert p.is_file(),('Missing desktop Unity log',str(p))
  text=p.read_text(errors='replace')
  assert not any(x in text for x in ('NullReferenceException','AccessViolationException','Fatal error','Crash!!!','Error while reading audio','Error loading audio')),('Runtime error in desktop log',str(p))
 old=json.loads((R/'distribution/Cloudcourt-v28-extras-customization/patch.json').read_text(encoding='utf-8-sig'))
 assert len(old['files'])==17 and {r['path'] for r in old['files']}==set(NAMES)
 changed=[]
 for row in old['files']:
  assert H(R/'versions/cloudcourt-v28-antes-v29'/Path(row['path']).name)==row['modified_sha256'],('Immutable v28 baseline mismatch',row['path'])
  if H(R/'working'/row['path'])!=row['modified_sha256']:changed.append(row['path'])
 allowed={'GameAssembly.dll'}|{'VolleyballFever_Data/'+n for n in MODIFIED}
 assert set(changed)==allowed,('Unexpected final changed-file set',changed)
 art=json.loads((R/'analysis/v29-composed-assets.json').read_text(encoding='utf-8-sig'))
 candidate=Path(art['output']);assert candidate.resolve()==(R/'visuals-v29').resolve()
 assert art['file_count']==17 and {r['path'] for r in art['files']}==set(FILES)
 for row in art['files']:
  assert H(candidate/row['path'])==row['sha256'],('Candidate changed since asset composition',row['path'])
  if row['path']!='GameAssembly.dll':
   assert H(R/'working/VolleyballFever_Data'/row['path'])==row['sha256'],('Working assets differ from verified candidate',row['path'])
 # Retained geometry, collision and textures are byte-preserved, apart from
 # the explicit authored startup splash image at globalgamemanagers Texture2D3.
 sys.path[:0]=[str(R),str(R/'tools/python')];import UnityPy
 preserved=0
 for name in MODIFIED:
  a=UnityPy.load(str(R/'versions/cloudcourt-v28-antes-v29'/name)).file
  b=UnityPy.load(str(R/'working/VolleyballFever_Data'/name)).file
  for ident,obj in a.objects.items():
   protected=obj.type.name in ('Mesh','Texture2D','Rigidbody') or 'Collider' in obj.type.name
   splash=name=='globalgamemanagers.assets' and ident==3 and obj.type.name=='Texture2D'
   if protected and not splash:
    assert obj.get_raw_data()==b.objects[ident].get_raw_data(),('Retained geometry/physics/texture changed',name,ident,obj.type.name)
    preserved+=1
 previous=R/'distribution/Cloudcourt-v28-extras-customization.zip'
 assert H(previous)==PREVIOUS_ZIP,'Previous delivered v28 ZIP changed'
 working={name:H(R/'working'/name) for name in NAMES}
 result=dict(passed=True,native_sha256=native,verified_files=17,working_sha256=working,
  changed_game_files=changed,unchanged_game_files=17-len(changed),focused_reports=list(reports),
  focused_source_sha256=source_hashes,native_integration_report='v29-native-integration.json',
  desktop_unity_report='v29-refinement-unity-release.json',desktop_unity_probe_passed=True,
  real_menu_visits=len(ui['visits']),real_settings_clicks=len(ui['settings']),
  original_protected_objects_preserved=preserved,asset_report='v29-composed-assets.json',
  candidate_asset_sha256={r['path']:r['sha256'] for r in art['files'] if r['path']!='GameAssembly.dll'},
  previous_zip_preserved=True,previous_zip_sha256=H(previous),room_namespaces=ROOMS,
  physical_Quest_tested=False,live_two_PC_tested=False,private_report=True)
 return result
def main():
 result=verify()
 (R/'analysis/v29-integration-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()

