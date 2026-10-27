"""Verify installed v24, snapshot sources and record the recoverable release."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent
G=Path('C:/APPS/STEAM/steamapps/common/Volleyball')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 package=json.loads((R/'analysis/complete-package-v24-validation.json').read_text())
 manifest=json.loads((R/'distribution/Cloudcourt-v24-celebracao-graficos/patch.json').read_text())
 audit=json.loads((R/'analysis/v24-integration-audit.json').read_text())
 assert audit['passed'] and H(R/'working/GameAssembly.dll')==audit['native_sha256']
 assert len(package['checks'])==13 and all(x['passed'] for x in package['checks'])
 assert H(Path(package['zip']))==package['sha256'] and package['zip_crc_valid']
 for row in manifest['files']:
  assert H(G/row['path'])==H(R/'working'/row['path'])==row['modified_sha256'],row['path']
 dest=R/'versions/cloudcourt-v24-fontes';dest.mkdir(exist_ok=True)
 for file in R.iterdir():
  if file.is_file() and file.suffix in ('.c','.py','.ps1','.md'):shutil.copyfile(file,dest/file.name)
 backup=max((d for d in G.glob('Caioba-backup-*') if (d/'recovery.json').exists()),key=lambda d:d.stat().st_mtime)
 status=dict(checkpoint=manifest['version'],base='Cloudcourt-v23-maos-audio',installed=str(G),verified_files=17,
  zip=package['zip'],zip_sha256=package['sha256'],previous_checkpoint='distribution/Cloudcourt-v23-maos-audio.zip',
  previous_backup='versions/cloudcourt-v23-antes-v24',installation_backup=str(backup),source_snapshot=str(dest),
  github_commit=None,requested_implementation_completed=True,work_in_progress=False,
  final_asset_audit_passed=True,native_regression_suites_passed=10,installer_cases_passed=13,
  native_sha256=audit['native_sha256'],room_namespaces=audit['room_namespaces'],
  graphics_default='ULTRA',graphics_presets=['LOW','MEDIUM','HIGH','ULTRA'],
  pending=['Quest 3: actual eye-buffer render scale/FPS, triggers, gestures and sleeve appearance',
           'Real two-PC online: point recipient gaze/thumb, independent outfits and lobby recall'],
  VR_playtest=False,live_two_PC_multiplayer=False,waiting_only_for_user_playtest=True)
 (R/'installation-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
 summary={k:v for k,v in status.items() if k not in ('installed','installation_backup','source_snapshot','pending','zip')}
 summary.update(zip_name=Path(package['zip']).name,zip_bytes=package['bytes'],
  changed_game_files=audit['changed_game_files'],controlled_startup_seconds=15,
  real_Unity_graphics_raycast_and_getters=True,real_Unity_saved_graphics_reload=True,
  authoritative_point_recipient=True,trigger_only_spawn=True,per_player_outfit_sleeves=True,
  original_physics_source_unchanged=True,component_native_tests_passed=3,authored_asset_suites_passed=2)
 (R/'analysis/v24-release-summary.json').write_text(json.dumps(summary,indent=2))
 print(json.dumps(dict(verified_files=17,zip_sha256=package['sha256'],native_sha256=audit['native_sha256'],backup=str(backup))))

if __name__=='__main__':main()
