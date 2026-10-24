"""Add a verified production native build to the v16 asset candidate."""
import hashlib,json,os,shutil
from pathlib import Path
R=Path(__file__).resolve().parent;out=R/'visuals-v16';game=Path(os.environ.get('VOLLEY_RIOT_GAME_DIRECTORY',r'C:\Program Files (x86)\Steam\steamapps\common\Volleyball'))
m=json.loads((out/'manifest.json').read_text());native=json.loads((R/'analysis/native-patch-manifest.json').read_text())
assert 'probe_command' not in native['exports'],'Diagnostic build must never be distributed'
data=(R/'working/GameAssembly.dll').read_bytes();assert hashlib.sha256(data).hexdigest()==native['modified_sha256']
shutil.copy2(R/'working/GameAssembly.dll',out/'GameAssembly.dll')
m=[x for x in m if x['path']!='GameAssembly.dll'];m.append({'path':'GameAssembly.dll','before':hashlib.sha256((game/'GameAssembly.dll').read_bytes()).hexdigest(),'after':native['modified_sha256']})
(out/'manifest.json').write_text(json.dumps(m,indent=2));print('production native build staged; diagnostic commands absent')
