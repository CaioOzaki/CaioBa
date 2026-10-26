from pathlib import Path
import json,shutil,sys,re
R=Path(__file__).resolve().parent;sha=sys.argv[1];assert re.fullmatch('[0-9a-f]{40}',sha)
status=json.loads((R/'installation-status.json').read_text());assert status['checkpoint']=='Cloudcourt-v20-1-middle-part'
status['github_commit']=sha;(R/'installation-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
summary=json.loads((R/'analysis/v20-1-release-summary.json').read_text());summary['github_commit']=sha;(R/'analysis/v20-1-release-summary.json').write_text(json.dumps(summary,indent=2))
entries=json.loads((R/'analysis/v20-1-publish-text.json').read_text(encoding='utf-8'));binaries=json.loads((R/'analysis/v20-1-publish-binary.json').read_text())
record=dict(repository='https://github.com/CaioOzaki/CaioBa',branch='main',commit=sha,checkpoint=status['checkpoint'],
 published_files_in_last_commit=len(entries)+len(binaries),local_zip='distribution/Cloudcourt-v20-1-middle-part.zip',zip_sha256=status['zip_sha256'],
 note='Scoped source/own-art update through connector; reconcile before CLI push.')
(R/'analysis/github-publication.json').write_text(json.dumps(record,indent=2))
snapshot=R/'versions/cloudcourt-v20-1-fontes';snapshot.mkdir(exist_ok=True)
for entry in entries+binaries:
 name=entry['path'];dest=snapshot/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R.parent/'Caioba-github'/name,dest)
for src in [R/'installation-status.json',R/'analysis/github-publication.json',R/'analysis/complete-package-v20-1-validation.json',R/'analysis/v20-1-release-summary.json']:shutil.copyfile(src,snapshot/src.name)
print(json.dumps({'commit':sha,'zip':status['zip'],'verified_files':17},indent=2))
