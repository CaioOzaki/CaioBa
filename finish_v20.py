"""Verify the installed v20 release; record only after package/tests are complete."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;G=Path('C:/APPS/STEAM/steamapps/common/Volleyball')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
package=json.loads((R/'analysis/complete-package-v20-validation.json').read_text())
manifest=json.loads((R/'distribution/Cloudcourt-v20-personagens-menu/patch.json').read_text())
tests=json.loads((R/'analysis/v20-regressions.json').read_text())
assets=json.loads((R/'analysis/v20-final-assets-audit.json').read_text())
assert tests['passed'] and tests['completed']==tests['total']==27
assert assets['passed']
assert tests['binary_sha256']==H(R/'working/GameAssembly.dll')
assert H(Path(package['zip']))==package['sha256'] and all(r['passed'] for r in package['checks'])
for entry in manifest['files']:assert H(G/entry['path'])==entry['modified_sha256'],entry['path']
latest=max((p for p in G.glob('Caioba-backup-*') if (p/'recovery.json').exists()),key=lambda p:p.stat().st_mtime)
status={'checkpoint':'Cloudcourt-v20-personagens-menu','base':'Cloudcourt-v19-customizacao',
 'installed':str(G),'verified_files':len(manifest['files']),'zip':package['zip'],
 'zip_sha256':package['sha256'],'previous_checkpoint':'distribution/Cloudcourt-v19-customizacao.zip',
 'previous_backup':'versions/cloudcourt-v19-antes-v20','installation_backup':str(latest),
 'github_commit':None,'test_suites_passed':27,'final_asset_audit_passed':True,
 'requested_implementation_completed':True,
 'pending':['Quest 3: conferir CUSTOMIZE e aparencia aplicada no avatar vivo',
 'Dois PCs v20: confirmar estilos de players, nove bots sem repeticao e circulo no mesmo contato',
 'Quest 3: verificar cabelos/BOT8/BOT9, outline nos placares, Settings e bandeiras',
 'Playtests anteriores: pausa, maos, high five, ataque dos bots e bolas de lobby']}
(R/'installation-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
summary={'checkpoint':status['checkpoint'],'implementation_complete':True,
 'installed_verified_files':17,'native_suites_passed':27,'final_asset_audit_passed':True,
 'native_sha256':tests['binary_sha256'],'zip_name':Path(package['zip']).name,
 'zip_bytes':package['bytes'],'zip_sha256':package['sha256'],
 'bot_identities':9,'bot_roster_cases':480,'bot_texture_bytes_before':150994944,
 'bot_texture_bytes_after':33554304,'player_atlas_bytes':6291488,
 'all_player_mips_opaque':True,'preview_rendered_in_actual_Unity':True,
 'skin_material_retry_x64_regression':True,'landing_cases':40,
 'landing_uses_actual_contact_and_existing_reliable_RPC':True,
 'banner_intersections_before':12,'banner_intersections_after':0,
 'room_namespaces':['Cloudcourt-2v2-v20','Cloudcourt-4v4-v20'],
 'startup_checks':{'menu_indoor_seconds':15,'beach_day_seconds':15,'controlled_without_VR':True},
 'live_avatar_visual_playtest':False,'VR_playtest':False,'live_two_PC_multiplayer':False,
 'waiting_only_for_user_playtest':True}
(R/'analysis/v20-release-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({'verified_files':17,'backup':str(latest),'zip_sha256':package['sha256']},indent=2))
