"""Capture the delivered v19 working files and editable mod sources before v20."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent
D=R/'versions/cloudcourt-v19-antes-v20'
manifest=json.loads((R/'distribution/Cloudcourt-v19-customizacao/patch.json').read_text())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
D.mkdir(exist_ok=True,parents=True)
rows=[]
for row in manifest['files']:
 source=R/'working'/row['path'];assert H(source)==row['modified_sha256'],row['path']
 dest=D/Path(row['path']).name
 if dest.exists():assert H(dest)==row['modified_sha256'],'Never overwrite a different backup.'
 else:shutil.copyfile(source,dest)
 assert H(dest)==row['modified_sha256']
 rows.append({'path':row['path'],'sha256':H(dest)})
sources=[]
for source in R.iterdir():
 if source.is_file() and source.suffix.lower() in ('.py','.c','.ps1','.cmd','.md','.json'):
  dest=D/'fontes'/source.name;dest.parent.mkdir(exist_ok=True)
  if not dest.exists():shutil.copyfile(source,dest)
  sources.append({'path':source.name,'sha256':H(dest)})
for source in [R/'installation-status.json',R/'analysis/github-publication.json']:
 dest=D/source.name
 if not dest.exists():shutil.copyfile(source,dest)
report={'base':'Cloudcourt-v19-customizacao','game_files':rows,'source_files':sources,
 'live_game_modified':False,'sources_reference_modified':False}
(D/'backup-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'backup':str(D),'verified_game_files':len(rows),'source_files':len(sources)}))
