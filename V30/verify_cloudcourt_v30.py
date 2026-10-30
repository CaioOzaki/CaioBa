"""Bind V30 release files to current native, asset and actual desktop evidence."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PREVIOUS='0729fb7ea75047e48c44a76c1f0c27ad60c4e2151355d40b61c259cb1b1ccf64'
def report(name):
 d=json.loads((R/'analysis'/name).read_text(encoding='utf-8-sig'));assert d.get('passed') is True,('Incomplete evidence',name);return d
def hashes(rows):
 for name,digest in rows.items():assert H(R/name)==digest,('Source changed after test',name)
def verify():
 from package_cloudcourt_v30 import NAMES
 from build_assets_v30 import FILES,MODIFIED
 native=H(R/'working/GameAssembly.dll');m=json.loads((R/'analysis/native-patch-manifest.json').read_text())
 assert m['modified_sha256']==native
 ni=report('v30-native-integration.json');assert ni['sha256']==native and ni['patch_count']==len(m['patches']);hashes(ni['source_sha256'])
 for name in ['v30-rules-integrated-tests.json','v30-ball-spawn-integrated-tests.json']:
  d=report(name);assert d['sha256']==native
 rt=report('v30-haptics-settings-tests.json');hashes(rt['sources']);assert rt['native_haptic_argument_cases']==12 and rt['custom_haptic_coroutines']==0
 visual=report('v30-visual-tests.json');hashes(visual['source_sha256'])
 bomb=report('v30-bomb-launch-tests.json');hashes(bomb['source_sha256'])
 music=json.loads((R/'analysis/v30-music-tests.json').read_text());assert music['source_sha256']==H(R/'build_music_v30.py')
 assert music['original_audio_inputs'] is False and music['non_target_audio_payloads_exact']==14 and music['target_path_id']==171
 desktop=report('v30-desktop-checks.json');hashes(desktop['source_sha256'])
 for flag in ['six_modes_native_launch_without_stuck_black','native_leave_reentry','first_solo_extras','in_match_settings_game_audio_back_resume','new_music_playing','mirror_base_and_reward_fresh_and_return','bot_bubbles_outside_all_nine_heads','preferences_restored']:
  assert desktop.get(flag) is True,('Desktop check missing',flag)
 assert desktop['physical_quest_tested'] is False and desktop['real_two_pc_tested'] is False
 for row in desktop['evidence']:
  p=R/row['path'];assert H(p)==row['sha256'],('Evidence changed',row['path'])
 previous=R/'distribution/Cloudcourt-v29-refinement.zip';assert H(previous)==PREVIOUS
 old=json.loads((R/'distribution/Cloudcourt-v29-refinement/patch.json').read_text())
 for row in old['files']:assert H(R/'versions/cloudcourt-v29-antes-v30'/Path(row['path']).name)==row['modified_sha256']
 art=json.loads((R/'analysis/v30-composed-assets.json').read_text());assert art['file_count']==17 and {x['path'] for x in art['files']}==set(FILES)
 for row in art['files']:
  name=row['path'];assert H(R/'visuals-v30'/name)==row['sha256']
  if name!='GameAssembly.dll':assert H(R/'working/VolleyballFever_Data'/name)==row['sha256']
 changed=[n for n in NAMES if H(R/'working'/n)!=H(R/'versions/cloudcourt-v29-antes-v30'/Path(n).name)]
 assert set(changed)=={'GameAssembly.dll'}|{'VolleyballFever_Data/'+n for n in MODIFIED},changed
 import UnityPy
 protected=0
 for name in ['level0','resources.assets','sharedassets0.assets']:
  before=UnityPy.load(str(R/'versions/cloudcourt-v29-antes-v30'/name)).file;after=UnityPy.load(str(R/'visuals-v30'/name)).file
  for ident,obj in before.objects.items():
   if obj.type.name in ['Mesh','Texture2D','Rigidbody'] or 'Collider' in obj.type.name:
    assert obj.get_raw_data()==after.objects[ident].get_raw_data(),('Protected object changed',name,ident);protected+=1
  if name=='resources.assets':
   from build_bomb_launch_v30 import bomb_placement_audit_v30
   actual=[i for i,o in before.objects.items() if o.get_raw_data()!=after.objects[i].get_raw_data()]
   assert set(actual)==set(art['bomb_launch']['changed_existing_ids'])=={512,1431,1436,1441,1446,1451,1456}
   assert len(set(after.objects)-set(before.objects))==21
   assert sum(not x['placements'] for x in bomb_placement_audit_v30(before))==7
   assert all(x['default_valid'] and len(x['placements'])==1 for x in bomb_placement_audit_v30(after))
  if name=='sharedassets0.assets':
   a=(R/'versions/cloudcourt-v29-antes-v30/sharedassets0.resource').read_bytes();b=(R/'visuals-v30/sharedassets0.resource').read_bytes()
   for ident,obj in before.objects.items():
    if obj.type.name!='AudioClip':assert obj.get_raw_data()==after.objects[ident].get_raw_data(),('Non-audio changed',ident);continue
    if ident==171:continue
    ar=obj.read_typetree()['m_Resource'];br=after.objects[ident].read_typetree()['m_Resource']
    assert a[ar['m_Offset']:ar['m_Offset']+ar['m_Size']]==b[br['m_Offset']:br['m_Offset']+br['m_Size']]
 result=dict(passed=True,native_sha256=native,verified_files=17,working_sha256={n:H(R/'working'/n) for n in NAMES},changed_game_files=changed,unchanged_game_files=17-len(changed),protected_objects_preserved=protected,previous_zip_preserved=True,previous_zip_sha256=PREVIOUS,desktop_unity_report='v30-desktop-checks.json',room_namespaces=['Cloudcourt-2v2-v30','Cloudcourt-4v4-v30','Cloudcourt-Bomb-2v2-v30','Cloudcourt-Bomb-4v4-v30'],physical_Quest_tested=False,live_two_PC_tested=False,private_report=True)
 return result
if __name__=='__main__':
 d=verify();(R/'analysis/v30-integration-audit.json').write_text(json.dumps(d,indent=2),encoding='utf8');print(json.dumps(d))
