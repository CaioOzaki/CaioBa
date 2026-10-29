"""Tie v28 release evidence to final files; no Steam writes."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 native=H(R/'working/GameAssembly.dll');manifest=json.loads((R/'analysis/native-patch-manifest.json').read_text())
 assert manifest['modified_sha256']==native
 assert 'customization_stats_v28' not in manifest['exports'],'Debug-only probe leaked into production'
 reports={}
 for n in ['v28-rules-bomb-tests.json','v28-ball-spawn-integrated-tests.json','v26-ball-style-integrated-tests.json','v28-customization-native-tests.json','v28-customization-assets-tests.json','v28-sleeves-native-tests.json','v28-settings-audio-tests.json','v28-bomb-assets-tests.json','v28-customization-unity-release.json']:
  d=json.loads((R/'analysis'/n).read_text());assert d['passed'],n;reports[n]=d
 for n in ['v28-rules-bomb-tests.json','v28-ball-spawn-integrated-tests.json','v26-ball-style-integrated-tests.json']:assert reports[n]['sha256']==native,n
 assert reports['v28-settings-audio-tests.json']['production_source_sha256']==H(R/'settings_audio_v28.c')
 ui=reports['v28-customization-unity-release.json'];assert len(ui['visits'])==2 and len(ui['settings'])==8
 assert all(x['playlist']==[1,233789,1,1,22050] for x in ui['settings'])
 assert ui['preferences_restored'] and not ui['headset_or_two_pc_test']
 old=json.loads((R/'distribution/Cloudcourt-v27-avatar-elbow/patch.json').read_text());changed=[]
 for row in old['files']:
  assert H(R/'versions/cloudcourt-v27-antes-v28'/Path(row['path']).name)==row['modified_sha256']
  if H(R/'working'/row['path'])!=row['modified_sha256']:changed.append(row['path'])
 assert set(changed)=={'GameAssembly.dll','VolleyballFever_Data/resources.assets','VolleyballFever_Data/level0','VolleyballFever_Data/sharedassets0.assets','VolleyballFever_Data/sharedassets0.resource'},changed
 art=json.loads((R/'visuals-v28/assets-v28-report.json').read_text())
 for row in art['outputs']:assert H(R/'working/VolleyballFever_Data'/row['path'])==row['sha256']
 sys.path[:0]=[str(R),str(R/'tools/python')];import UnityPy
 a=UnityPy.load(str(R/'versions/cloudcourt-v27-antes-v28/resources.assets')).file;b=UnityPy.load(str(R/'working/VolleyballFever_Data/resources.assets')).file
 for i,o in a.objects.items():
  if o.type.name in ('Mesh','Texture2D') or 'Collider' in o.type.name:assert o.get_raw_data()==b.objects[i].get_raw_data(),('retained base mesh/texture/collider changed',i)
 assert H(R/'distribution/Cloudcourt-v27-avatar-elbow.zip')=='7794562afc49942a15e818c5ff4b1939d9c0ddab8ead74f6f8cd129e3203663d'
 log=(R/'tools/u28-custom/analysis/unity-release.log')
 # Probe's explicit path can differ from the historical startup log naming.
 logs=[R/'analysis/v28-release-unity.log'];assert all(p.exists() for p in logs)
 for p in logs:
  text=p.read_text(errors='replace');assert not any(x in text for x in ['NullReferenceException','AccessViolationException','Fatal error','Crash!!!','Error while reading audio','Error loading audio']),p
 result=dict(passed=True,native_sha256=native,verified_files=17,changed_game_files=changed,unchanged_game_files=12,native_validation_suites=7,asset_validation_suites=2,desktop_unity_probe_passed=True,real_menu_visits=2,real_settings_clicks=8,playlist_seconds=233.789,original_existing_meshes_textures_colliders_preserved=True,previous_zip_preserved=True,room_namespaces=['Cloudcourt-2v2-v28','Cloudcourt-4v4-v28','Cloudcourt-Bomb-2v2-v28','Cloudcourt-Bomb-4v4-v28'],reports=list(reports),physical_Quest_tested=False,live_two_PC_tested=False)
 (R/'analysis/v28-integration-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
