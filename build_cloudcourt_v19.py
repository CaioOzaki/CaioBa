"""Apply v19 artwork/UI/audio-source edits to current v18, never reconstruct v16."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from build_customization_art_v19 import apply_customization_assets
from build_menu_v19 import build_menu,bind_v19_preview_assets
from silence_beach_v19 import silence,TARGETS
W=R/'working/VolleyballFever_Data'
resource=UnityPy.load(str(W/'resources.assets')).file
art=apply_customization_assets(resource);(W/'resources.assets').write_bytes(resource.save())
menu=UnityPy.load(str(W/'level0')).file
ui=build_menu(menu);preview=bind_v19_preview_assets(menu,art);(W/'level0').write_bytes(menu.save())
ambient=[]
for name,ids in TARGETS.items():
 scene=UnityPy.load(str(W/name)).file;ambient.append({'scene':name,'sources':silence(scene,ids)});(W/name).write_bytes(scene.save())
report={'avatar':art,'menu':ui,'previews':preview,'beach_audio':ambient,'live_game_modified':False}
(R/'analysis/v19-visual-build.json').write_text(json.dumps(report,indent=2));print(json.dumps({'art_applied':True,'menu_applied':True,'beach_ambience_disabled':True}))
