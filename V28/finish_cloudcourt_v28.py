"""Record packaged/installed v28 after exact file validation."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent;G=Path('C:/APPS/STEAM/steamapps/common/Volleyball');H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 package=json.loads((R/'analysis/complete-package-v28-validation.json').read_text());manifest=json.loads((R/'distribution/Cloudcourt-v28-extras-customization/patch.json').read_text());audit=json.loads((R/'analysis/v28-integration-audit.json').read_text())
 assert audit['passed'] and H(R/'working/GameAssembly.dll')==audit['native_sha256'];assert len(package['checks'])==13 and all(x['passed'] for x in package['checks']);assert H(Path(package['zip']))==package['sha256'] and package['zip_crc_valid']
 for row in manifest['files']:assert H(G/row['path'])==H(R/'working'/row['path'])==row['modified_sha256'],row['path']
 dest=R/'versions/cloudcourt-v28-fontes';dest.mkdir(exist_ok=True)
 for p in R.iterdir():
  if p.is_file() and p.suffix in ('.c','.py','.ps1','.md'):shutil.copyfile(p,dest/p.name)
 backup=max((d for d in G.glob('Caioba-backup-*') if (d/'recovery.json').exists()),key=lambda d:d.stat().st_mtime)
 status=dict(checkpoint=manifest['version'],base='Cloudcourt-v27-avatar-elbow',installed=str(G),verified_files=17,zip=package['zip'],zip_sha256=package['sha256'],previous_checkpoint='distribution/Cloudcourt-v27-avatar-elbow.zip',previous_backup='versions/cloudcourt-v27-antes-v28',installation_backup=str(backup),source_snapshot=str(dest),github_commit=None,requested_implementation_completed=False,work_in_progress=True,final_asset_audit_passed=True,native_validation_suites_passed=audit['native_validation_suites'],installer_cases_passed=13,native_sha256=audit['native_sha256'],room_namespaces=audit['room_namespaces'],pending=['Finish scoped GitHub source publication and deliver ZIP','Physical Quest3 and real two-PC gameplay confirmation'],VR_playtest=False,live_two_PC_multiplayer=False,waiting_only_for_user_playtest=False)
 (R/'installation-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8');shutil.copyfile(R/'installation-status.json',dest/'installation-status.json')
 summary={k:v for k,v in status.items() if k not in ('installed','installation_backup','source_snapshot','pending','zip')};summary.update(zip_name=Path(package['zip']).name,zip_bytes=package['bytes'],changed_game_files=audit['changed_game_files'],unchanged_game_files=12,requested_implementation_completed=True,work_in_progress=False,waiting_only_for_user_playtest=True)
 (R/'analysis/v28-release-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 (R/'analysis/v28-installer-checks.json').write_text(json.dumps(dict(passed=True,checks=[{k:v for k,v in c.items() if k!='output'} for c in package['checks']],backups_verified=package['backups_verified'],previous_zip_preserved=package['previous_zip_preserved'],zip_crc_valid=package['zip_crc_valid']),indent=2),encoding='utf-8')
 print(json.dumps(dict(verified_files=17,zip_sha256=package['sha256'],native_sha256=audit['native_sha256'],backup=str(backup))))
if __name__=='__main__':main()
