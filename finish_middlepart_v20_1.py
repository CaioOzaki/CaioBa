"""Verify the exact cosmetic install and record its release state."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;G=Path('C:/APPS/STEAM/steamapps/common/Volleyball')
package=json.loads((R/'analysis/complete-package-v20-1-validation.json').read_text());tests=json.loads((R/'analysis/v20-1-middlepart-tests.json').read_text())
manifest=json.loads((R/'distribution/Cloudcourt-v20-1-middle-part/patch.json').read_text())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert tests['passed'] and tests['other_release_files_unchanged']==16
assert all(row['passed'] for row in package['checks']) and H(Path(package['zip']))==package['sha256']
for row in manifest['files']:assert H(G/row['path'])==row['modified_sha256'],row['path']
backup=max((p for p in G.glob('Caioba-backup-*') if (p/'recovery.json').exists()),key=lambda p:p.stat().st_mtime)
status=json.loads((R/'installation-status.json').read_text());assert status['checkpoint']=='Cloudcourt-v20-personagens-menu'
status['base_v20_asset_audit_passed']=status.pop('final_asset_audit_passed',False)
status.update(checkpoint='Cloudcourt-v20-1-middle-part',base='Cloudcourt-v20-personagens-menu',verified_files=17,
 zip=package['zip'],zip_sha256=package['sha256'],previous_checkpoint='distribution/Cloudcourt-v20-personagens-menu.zip',
 previous_backup='versions/cloudcourt-v20-antes-middlepart',installation_backup=str(backup),github_commit=None,
 cosmetic_patch_tests_passed=True,requested_implementation_completed=True,
 validation_note='Only BOT1 mesh and three renderer AABBs changed. Native DLL and other16files identical to tested v20; previous27suites were not repeated.')
(R/'installation-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
summary=dict(checkpoint=status['checkpoint'],implementation_complete=True,installed_verified_files=17,
 zip=package['zip'],zip_bytes=package['bytes'],zip_sha256=package['sha256'],changed_assets=1,changed_objects=4,
 pre_v20_bot1_mesh_verified=True,other16files_unchanged=True,native_DLL_unchanged=True,
 previous27suites_retained_without_rerun=True,VR_playtest=False,room_namespace_unchanged=True)
(R/'analysis/v20-1-release-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({'verified_files':17,'backup':str(backup),'zip_sha256':package['sha256']},indent=2))
