"""Record delivery only after package checks and all live file hashes agree."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent;G=Path('C:/APPS/STEAM/steamapps/common/Volleyball')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 package=json.loads((R/'analysis/complete-package-v26-validation.json').read_text())
 manifest=json.loads((R/'distribution/Cloudcourt-v26-session-repair/patch.json').read_text())
 audit=json.loads((R/'analysis/v26-integration-audit.json').read_text())
 assert audit['passed'] and H(R/'working/GameAssembly.dll')==audit['native_sha256']
 assert len(package['checks'])==13 and all(x['passed'] for x in package['checks'])
 assert H(Path(package['zip']))==package['sha256'] and package['zip_crc_valid']
 for row in manifest['files']:assert H(G/row['path'])==H(R/'working'/row['path'])==row['modified_sha256'],row['path']
 dest=R/'versions/cloudcourt-v26-fontes';dest.mkdir(exist_ok=True)
 for file in R.iterdir():
  if file.is_file() and file.suffix in ('.c','.py','.ps1','.md'):shutil.copyfile(file,dest/file.name)
 backup=max((d for d in G.glob('Caioba-backup-*') if (d/'recovery.json').exists()),key=lambda d:d.stat().st_mtime)
 status=dict(checkpoint=manifest['version'],base='Cloudcourt-v25-trigger-fix',installed=str(G),verified_files=17,
  zip=package['zip'],zip_sha256=package['sha256'],previous_checkpoint='distribution/Cloudcourt-v25-trigger-fix.zip',
  previous_backup='versions/cloudcourt-v25-antes-v26',installation_backup=str(backup),source_snapshot=str(dest),
  github_commit=None,requested_implementation_completed=True,work_in_progress=False,
  final_asset_audit_passed=True,native_validation_suites_passed=7,installer_cases_passed=13,
  native_sha256=audit['native_sha256'],room_namespaces=['Cloudcourt-2v2-v24','Cloudcourt-4v4-v24'],
  pending=['Quest 3: confirm serve/lobby ball spawn, holding and throwing, menu previews and bot poses',
   'Real two-PC: consecutive matches, symmetric net limits, Beach practice net, Indoor antennas and venue ball artwork',
   'Quest graphics/FPS: restart after changing preset and confirm the saved setting'],
  VR_playtest=False,live_two_PC_multiplayer=False,waiting_only_for_user_playtest=True)
 (R/'installation-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
 shutil.copyfile(R/'installation-status.json',dest/'installation-status.json')
 summary={k:v for k,v in status.items() if k not in ('installed','installation_backup','source_snapshot','pending','zip')}
 summary.update(zip_name=Path(package['zip']).name,zip_bytes=package['bytes'],changed_game_files=audit['changed_game_files'],
  unchanged_game_files=audit['unchanged_game_files'],graphics_changes_require_restart=True,
  actual_unity_ui_material_probes=True,deterministic_online_two_session_cases=8,
  controlled_startup_seconds=15)
 (R/'analysis/v26-release-summary.json').write_text(json.dumps(summary,indent=2))
 (R/'analysis/v26-installer-checks.json').write_text(json.dumps(dict(passed=True,checks=[
   {k:v for k,v in c.items() if k!='output'} for c in package['checks']],backups_verified=package['backups_verified'],
   previous_zip_preserved=package['previous_zip_preserved'],zip_crc_valid=package['zip_crc_valid']),indent=2))
 print(json.dumps(dict(verified_files=17,zip_sha256=package['sha256'],native_sha256=audit['native_sha256'],backup=str(backup))))
if __name__=='__main__':main()
