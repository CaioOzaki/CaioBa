"""Record a verified GitHub publication and snapshot only the release allowlist."""
from pathlib import Path
import json,hashlib,shutil,sys,re
R=Path(__file__).resolve().parent;sha=sys.argv[1];assert re.fullmatch('[0-9a-f]{40}',sha)
status=json.loads((R/'installation-status.json').read_text())
assert status['checkpoint']=='Cloudcourt-v19-customizacao' and status['verified_files']==17
status['github_commit']=sha;(R/'installation-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
summary=json.loads((R/'analysis/v19-release-summary.json').read_text());summary['github_commit']=sha
(R/'analysis/v19-release-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
entries=json.loads((R/'analysis/v19-publish-text.json').read_text(encoding='utf-8'))
binaries=json.loads((R/'analysis/v19-publish-binary.json').read_text(encoding='utf-8'))
record={'repository':'https://github.com/CaioOzaki/CaioBa','branch':'main','commit':sha,
 'checkpoint':status['checkpoint'],'published_files_in_last_commit':len(entries)+len(binaries),
 'update_mode':'Scoped sources, tests and own avatar PNGs; cleaned remote base tree preserved',
 'local_zip':'distribution/Cloudcourt-v19-customizacao.zip','zip_sha256':status['zip_sha256'],
 'note':'Published through GitHub connector. Local staging history differs; fetch and reconcile before CLI push.'}
(R/'analysis/github-publication.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
snapshot=R/'versions/cloudcourt-v19-fontes';snapshot.mkdir(exist_ok=True)
for entry in entries+binaries:
 name=entry['path'];src=R.parent/'Caioba-github'/name;dest=snapshot/name
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
for src in [R/'installation-status.json',R/'analysis/native-patch-manifest.json',
 R/'analysis/github-publication.json',R/'analysis/complete-package-v19-validation.json',R/'analysis/v19-release-summary.json']:
 shutil.copyfile(src,snapshot/src.name)
assert hashlib.sha256(Path(status['zip']).read_bytes()).hexdigest()==status['zip_sha256']
print(json.dumps({'checkpoint':status['checkpoint'],'commit':sha,'zip':status['zip'],
 'source_snapshot':str(snapshot),'installed_verified_files':17},indent=2))
