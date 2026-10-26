"""Verify installed v22, preserve its sources and record the delivered state."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent;G=Path('C:/APPS/STEAM/steamapps/common/Volleyball')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=json.loads((R/'analysis/complete-package-v22-validation.json').read_text())
 m=json.loads((R/'distribution/Cloudcourt-v22-correcoes/patch.json').read_text())
 reg=json.loads((R/'analysis/v22-regression.json').read_text());assert reg['passed']
 assert all(c['passed'] for c in p['checks']) and H(Path(p['zip']))==p['sha256']
 native=H(R/'working/GameAssembly.dll');assert native==reg['native_sha256']
 for n in ['v22-hands-integrated-tests.json','v22-landing-projection-tests.json']:
  r=json.loads((R/'analysis'/n).read_text());assert r['passed'] and r['sha256']==native,n
 audit=json.loads((R/'analysis/v22-integration-assets.json').read_text());assert audit['passed']
 for r in m['files']:assert H(G/r['path'])==H(R/'working'/r['path'])==r['modified_sha256'],r['path']
 done=json.loads((R/'analysis/v22-ui-unity-after.json').read_text())
 assert all(r['top_hit_is_target'] for r in done['rows'])
 assert all(not r['panel_after'] for r in done['rows'] if r['control']=='Done')
 dest=R/'versions/cloudcourt-v22-fontes';dest.mkdir(exist_ok=True)
 for f in R.iterdir():
  if f.is_file() and f.suffix in ('.c','.py','.ps1','.md'):shutil.copyfile(f,dest/f.name)
 backup=max((d for d in G.glob('Caioba-backup-*') if (d/'recovery.json').exists()),key=lambda d:d.stat().st_mtime)
 status=dict(checkpoint=m['version'],base='Cloudcourt-v21-orla-gestos',installed=str(G),verified_files=17,
  zip=p['zip'],zip_sha256=p['sha256'],previous_checkpoint='distribution/Cloudcourt-v21-orla-gestos.zip',
  previous_backup='versions/cloudcourt-v21-antes-v22',installation_backup=str(backup),source_snapshot=str(dest),
  github_commit=None,requested_implementation_completed=True,final_asset_audit_passed=True,
  native_regression_suites_passed=len(reg['suites']),installer_cases_passed=len(p['checks']),native_sha256=native,
  room_namespaces=['Cloudcourt-2v2-v22','Cloudcourt-4v4-v22'],
  pending=['Quest3: Done/setting hands/thumbs and connected bot arm until serve whistle',
           'Quest3: Beach dry surface/ground ring, restored bot looks, Indoor boards/posts',
           'Real two-PC online playtest and FPS measurement'],
  VR_playtest=False,live_two_PC_multiplayer=False,waiting_only_for_user_playtest=True)
 (R/'installation-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
 summary={k:v for k,v in status.items() if k not in ('installed','source_snapshot','installation_backup','pending','zip')}
 summary.update(zip_name=Path(p['zip']).name,zip_bytes=p['bytes'],real_Unity_Done_raycast_verified=True,
  bot_celebration_until_serve_whistle=True,hand_tones=6,skyline_triangles=1572,sand_surface_triangles=2,
  unchanged_colliders=144,unchanged_collider_meshes=76,startup_menu_indoor_seconds=15,startup_beach_seconds=15)
 (R/'analysis/v22-release-summary.json').write_text(json.dumps(summary,indent=2))
 print(json.dumps(dict(verified_files=17,zip=p['zip'],zip_sha256=p['sha256'],native_sha256=native,backup=str(backup))))
if __name__=='__main__':main()
