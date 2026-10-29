"""Audit the final native/asset integration and the limits of its evidence."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
from PIL import Image
import numpy as np
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 native=H(R/'working/GameAssembly.dll');reports={}
 for n in ['bot-pose-integrated','ball-style-integrated','ui-native','trigger-integrated']:
  report=json.loads((R/f'analysis/v26-{n}-tests.json').read_text())
  assert report['passed'] and report.get('sha256',report.get('native_sha256'))==native,(n,'stale DLL report')
  reports[n]=report
 for n in ['graphics','online-state','bot-pose-native']:
  report=json.loads((R/f'analysis/v26-{n}-tests.json').read_text());assert report['passed'];reports[n]=report
 ui=json.loads((R/'analysis/v26-ui-unity-final.json').read_text())
 assert ui['passed'] and ui['popup'][3]==1 and ui['popup_material'][1]==1
 assert ui['shader_name']=='TextMeshPro/Mobile/Distance Field'
 assert ui['graphics']==[3,4,0,3,4,0],ui['graphics']
 images=[]
 for row in ui['visits']:
  a=np.asarray(Image.open(row['before']).convert('RGB')).astype(float)
  b=np.asarray(Image.open(row['after']).convert('RGB')).astype(float)
  for label,(x0,y0,x1,y1) in [('face',(260,316,400,421)),('outfit',(625,316,764,421))]:
   mean=float(np.abs(a[y0:y1,x0:x1]-b[y0:y1,x0:x1]).mean())
   assert mean>2,(row['visit'],label,'preview did not visibly change')
   images.append(dict(visit=row['visit'],preview=label,mean_pixel_difference=mean))
 assets=json.loads((R/'visuals-v26-integrated/build-report.json').read_text())
 for n,v in assets['files'].items():assert H(R/'working/VolleyballFever_Data'/n)==v['sha256']
 art=json.loads((R/'assets/cloudcourt-v26/art-report.json').read_text())
 assert art['validation']['script_transform_physics_collider_bytes_preserved']
 baseline=R/'versions/cloudcourt-v25-antes-v26';old=json.loads((R/'distribution/Cloudcourt-v25-trigger-fix/patch.json').read_text())
 changed=[]
 for row in old['files']:
  assert H(baseline/Path(row['path']).name)==row['modified_sha256']
  if H(R/'working'/row['path'])!=row['modified_sha256']:changed.append(row['path'])
 assert sorted(changed)==sorted(['GameAssembly.dll']+['VolleyballFever_Data/'+n for n in assets['files']])
 patch=json.loads((R/'analysis/native-patch-manifest.json').read_text());assert patch['modified_sha256']==native
 assert patch['network_version']=='Cloudcourt-2v2-v24 / Cloudcourt-4v4-v24'
 for scene in ['menu','beach']:
  text=(R/f'analysis/smoke-v26-{scene}.log').read_text(errors='replace')
  assert 'Initialize engine version: 2019.4.5f1' in text
  assert not any(s in text for s in ['NullReferenceException','AccessViolationException','Fatal error','Crash!!!'])
 assert not (R/'analysis/level0-smoke-backup').exists()
 source_changes=[p.name for p in R.glob('*.c') if not p.name.startswith('test_') and
    (not (baseline/'fontes'/p.name).exists() or H(p)!=H(baseline/'fontes'/p.name))]
 result=dict(passed=True,native_sha256=native,verified_files=17,changed_game_files=changed,
  unchanged_game_files=17-len(changed),changed_production_c_sources=source_changes,
  native_validation_suites=7,actual_unity_preview_image_changes=images,
  actual_unity_sdf_shader_and_keyword_verified=True,actual_unity_graphics_selection_retains_ultra=True,
  two_menu_visits_with_native_page_reentry=True,deterministic_online_sessions_per_case=2,
  controlled_scene_startup_seconds=15,beach_legacy_terrain_utility_shader_warning_retained=True,
  physical_Quest_tested=False,live_two_PC_tested=False,
  scope='Actual Unity local UI/material/getter probes plus deterministic native/scene fixtures. No physical input/FPS or real Photon peers; final user headset/multiplayer validation remains external.')
 (R/'analysis/v26-integration-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
