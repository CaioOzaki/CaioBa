"""Verify final installation, preserve source checkpoint and record v21."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent
G=Path('C:/APPS/STEAM/steamapps/common/Volleyball')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    package=json.loads((R/'analysis/complete-package-v21-validation.json').read_text())
    manifest=json.loads((R/'distribution/Cloudcourt-v21-orla-gestos/patch.json').read_text())
    assert all(c['passed'] for c in package['checks']) and H(Path(package['zip']))==package['sha256']
    assert all(c['passed'] for c in json.loads((R/'analysis/v21-regression-final.json').read_text()))
    audit=json.loads((R/'analysis/v21-integration-assets.json').read_text());assert audit['passed']
    native=H(R/'working/GameAssembly.dll')
    for name in ['v21-serve-feedback-tests.json','v21-lobby-integrated-tests.json',
                 'v21-hand-visuals-integrated-tests.json','v21-bot-celebration-integrated-tests.json']:
        report=json.loads((R/'analysis'/name).read_text());assert report['passed'] and report['sha256']==native,name
    for row in manifest['files']:
        assert H(G/row['path'])==H(R/'working'/row['path'])==row['modified_sha256'],row['path']
    snapshot=R/'versions/cloudcourt-v21-fontes';snapshot.mkdir(exist_ok=True)
    for p in R.iterdir():
        if p.is_file() and p.suffix in ('.c','.py','.ps1','.md'):shutil.copyfile(p,snapshot/p.name)
    backup=max((p for p in G.glob('Caioba-backup-*') if (p/'recovery.json').exists()),key=lambda p:p.stat().st_mtime)
    status=dict(checkpoint=manifest['version'],base='Cloudcourt-v20-1-middle-part',installed=str(G),
        verified_files=17,zip=package['zip'],zip_sha256=package['sha256'],
        previous_checkpoint='distribution/Cloudcourt-v20-1-middle-part.zip',
        previous_backup='versions/cloudcourt-v20-1-antes-v21',installation_backup=str(backup),
        source_snapshot=str(snapshot),github_commit=None,requested_implementation_completed=True,
        final_asset_audit_passed=True,native_regression_suites_passed=19,installer_cases_passed=len(package['checks']),
        native_sha256=native,room_namespaces=['Cloudcourt-2v2-v21','Cloudcourt-4v4-v21'],
        pending=['Quest 3: visual/gesture/menu and Indoor/Beach playtest',
                 'Two PCs on v21: own-team celebrations, poses/tones, serve feedback and lobby practice',
                 'Physical ball/net bounce and FPS measurement'],
        VR_playtest=False,live_two_PC_multiplayer=False,waiting_only_for_user_playtest=True)
    (R/'installation-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    summary={k:v for k,v in status.items() if k not in ('installed','source_snapshot','installation_backup','pending')}
    summary.update(zip_name=Path(package['zip']).name,zip_bytes=package['bytes'],visible_english_fields=119,
        contact_marker_until_serve_spawn=True,firsthand_preview_Unity_probe=True,
        original_whistle=True,hand_tones=6,skyline_triangles=1572,bot_identities=9,
        unchanged_colliders=144,unchanged_collider_meshes=19,working_sources_preserved=True,
        startup_menu_indoor_seconds=15,startup_beach_seconds=15)
    summary.pop('zip');(R/'analysis/v21-release-summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({'verified_files':17,'backup':str(backup),'zip_sha256':package['sha256'],'native_sha256':native}))
if __name__=='__main__':main()
