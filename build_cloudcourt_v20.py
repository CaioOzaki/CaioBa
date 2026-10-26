"""Apply narrow v20 upgrades to the current v19 assets; never rebuild an old base."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from build_bots_v20 import apply_bots_assets_v20
from build_customization_fix_v20 import apply_customization_fix
from build_scene_v20 import build_scene_assets
from build_landing_v20 import add_landing_marks
W=R/'working/VolleyballFever_Data'
names=['resources.assets','sharedassets0.assets','level0','level1','level2','level3']
before={name:hashlib.sha256((W/name).read_bytes()).hexdigest() for name in names}
files={name:UnityPy.load(str(W/name)).file for name in names}
report={'bots':apply_bots_assets_v20(files['sharedassets0.assets']),
 'customization':apply_customization_fix(files['resources.assets']),
 'scenes':build_scene_assets(files),'landing':{}}
for name in ['level1','level2','level3']:
 report['landing'][name]=add_landing_marks(files[name],files['resources.assets'])
# All transforms succeed in memory before replacing any working file. Steam is
# touched only later by the separately tested, reversible distribution installer.
for name,file in files.items():(W/name).write_bytes(file.save())
report['files']=[{'name':name,'sha256_before':before[name],
 'sha256_after':hashlib.sha256((W/name).read_bytes()).hexdigest()} for name in names]
report['live_game_modified']=False
(R/'analysis/v20-assets-integration.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'upgraded_files':len(names),'live_game_modified':False,'atlas_formats':'BC3 players / BC1 bots','bot_identities':9}))
