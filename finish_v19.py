"""Verify live hashes and save release metadata. Does not install or publish."""
from pathlib import Path
import json, hashlib
R=Path(__file__).resolve().parent
G=Path('C:/APPS/STEAM/steamapps/common/Volleyball')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
package=json.loads((R/'analysis/complete-package-v19-validation.json').read_text())
manifest=json.loads((R/'distribution/Cloudcourt-v19-customizacao/patch.json').read_text())
tests=json.loads((R/'analysis/v19-regressions.json').read_text())
assets=json.loads((R/'analysis/v19-final-assets-tests.json').read_text())
native=json.loads((R/'analysis/native-patch-manifest.json').read_text())
assert tests['passed'] and tests['completed']==tests['total']==23
assert assets['passed'] and not assets['problems']
assert H(Path(package['zip']))==package['sha256']
for entry in manifest['files']:
 assert H(G/entry['path'])==entry['modified_sha256'],entry['path']
latest=max((p for p in G.glob('Caioba-backup-*') if (p/'recovery.json').exists()),key=lambda p:p.stat().st_mtime)
status={'checkpoint':'Cloudcourt-v19-customizacao','base':'Cloudcourt-v18-praia-lobby',
 'installed':str(G),'verified_files':len(manifest['files']),'zip':package['zip'],
 'zip_sha256':package['sha256'],'previous_checkpoint':'distribution/Cloudcourt-v18-praia-lobby.zip',
 'previous_backup':'versions/cloudcourt-v18-antes-v19','installation_backup':str(latest),
 'github_commit':None,'test_suites_passed':23,'asset_suites_passed':3,
 'requested_implementation_completed':True,
 'pending':['Quest 3: A e trigger nas duas maos em todos os menus; clique e painel de customizacao',
 'Quest 3: bots atacando levantamento inalterado, 2v2/4v4 e Indoor/Beach',
 'Dois PCs v19: selecao de mapa pelo host, sincronizacao das 81 combinacoes e troca de times',
 'Quest 3: Beach sem mar/passaros; regras Indoor25/Beach21 melhor de tres',
 'Playtests anteriores: pausa/bots, maos, placares, high five e bolas do lobby']}
(R/'installation-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
summary={'checkpoint':status['checkpoint'],'implementation_complete':True,
 'installed_verified_files':len(manifest['files']),'native_test_suites_passed':23,
 'asset_test_suites_passed':3,'native_sha256':native['modified_sha256'],
 'zip_name':Path(package['zip']).name,'zip_bytes':package['bytes'],
 'zip_sha256':package['sha256'],'avatar_faces':9,'avatar_outfits':9,'avatar_combinations':81,
 'avatar_texture_bytes':6291488,'bot_real_jump_apex_m':2.0,
 'unchanged_player_setting_arc':True,'best_of_sets':3,'indoor_points':25,'beach_points':21,
 'room_namespaces':['Cloudcourt-2v2-v19','Cloudcourt-4v4-v19'],
 'startup_checks':{'menu_indoor_seconds':15,'beach_day_seconds':15,'controlled_without_VR':True},
 'VR_playtest':False,'live_two_PC_multiplayer':False,'waiting_only_for_user_playtest':True}
(R/'analysis/v19-release-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({'verified_files':len(manifest['files']),'backup':str(latest),
 'zip_sha256':package['sha256'],'native_sha256':native['modified_sha256']},indent=2))
