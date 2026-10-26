"""Verify installed v23 and preserve a recoverable delivery record."""
from pathlib import Path
import hashlib, json, shutil

R = Path(__file__).resolve().parent
G = Path('C:/APPS/STEAM/steamapps/common/Volleyball')
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    package = json.loads((R/'analysis/complete-package-v23-validation.json').read_text())
    manifest = json.loads((R/'distribution/Cloudcourt-v23-maos-audio/patch.json').read_text())
    regression = json.loads((R/'analysis/v23-regression.json').read_text())
    assert regression['passed'] and len(regression['suites']) == 6
    assert len(package['checks']) == 13 and all(c['passed'] for c in package['checks'])
    assert H(Path(package['zip'])) == package['sha256'] and package['zip_crc_valid']
    native = H(R/'working/GameAssembly.dll')
    assert native == regression['native_sha256']
    for name in ['v23-hands-assets-tests.json', 'v23-pause-audio-native-tests.json',
                 'v23-pause-audio-comparison.json']:
        assert json.loads((R/'analysis'/name).read_text())['passed'], name
    prior = R/'versions/cloudcourt-v22-antes-v23'
    changed = []
    for row in manifest['files']:
        rel = row['path']
        assert H(G/rel) == H(R/'working'/rel) == row['modified_sha256'], rel
        if H(prior/Path(rel).name) != row['modified_sha256']:
            changed.append(rel)
    assert sorted(changed) == ['GameAssembly.dll', 'VolleyballFever_Data/resources.assets'], changed
    assert H(R/'working/VolleyballFever_Data/resources.assets') == H(R/'visuals-v23-integrated/resources.assets')
    assert not (R/'analysis/level0-smoke-backup').exists()
    smoke = (R/'analysis/smoke-v23-menu.log').read_text(errors='replace')
    assert 'Loading environment IndoorArenaScene' in smoke
    for error in ['NullReferenceException', 'AccessViolationException', 'Fatal error', 'Crash!!!']:
        assert error not in smoke, error
    dest = R/'versions/cloudcourt-v23-fontes'
    dest.mkdir(exist_ok=True)
    for file in R.iterdir():
        if file.is_file() and file.suffix in ('.c', '.py', '.ps1', '.md'):
            shutil.copyfile(file, dest/file.name)
    backup = max((d for d in G.glob('Caioba-backup-*') if (d/'recovery.json').exists()),
                 key=lambda d: d.stat().st_mtime)
    status = dict(checkpoint=manifest['version'], base='Cloudcourt-v22-correcoes',
        installed=str(G), verified_files=len(manifest['files']), zip=package['zip'],
        zip_sha256=package['sha256'], previous_checkpoint='distribution/Cloudcourt-v22-correcoes.zip',
        previous_backup='versions/cloudcourt-v22-antes-v23', installation_backup=str(backup),
        source_snapshot=str(dest), github_commit=None, requested_implementation_completed=True,
        final_asset_audit_passed=True, native_regression_suites_passed=6, installer_cases_passed=13,
        native_sha256=native, room_namespaces=['Cloudcourt-2v2-v22', 'Cloudcourt-4v4-v22'],
        pending=['Quest 3: rounded default/setting/thumb hands and pause click with headset focus changes',
                 'Real two-PC online playtest and FPS measurement'], VR_playtest=False,
        live_two_PC_multiplayer=False, waiting_only_for_user_playtest=True)
    (R/'installation-status.json').write_text(json.dumps(status, indent=2), encoding='utf-8')
    summary = {k:v for k,v in status.items() if k not in
               ('installed', 'source_snapshot', 'installation_backup', 'pending', 'zip')}
    summary.update(zip_name=Path(package['zip']).name, zip_bytes=package['bytes'],
        changed_game_files=changed, default_hand_thickness_ratio=0.90,
        real_Unity_pause_audio_verified=True, global_listener_pause_preserved=True,
        source_reused_across_match_transition=True, startup_menu_indoor_seconds=15,
        startup_headset_present=False, physics_and_pose_protocol_unchanged=True)
    (R/'analysis/v23-release-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(dict(verified_files=17, zip_sha256=package['sha256'],
                          native_sha256=native, backup=str(backup))))

if __name__ == '__main__':
    main()
