"""Reload isolated lobby assets, check stable controllers and aligned net hitboxes."""
from pathlib import Path
import hashlib,json,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from build_lobby_v21 import build_lobby_assets_v21
from build_menu_v19 import MenuEditor,BUTTON,button_layout
from fix_gloves_v16 import hierarchy
W=R/'working/VolleyballFever_Data';F=R/'tools/u21-lobby-assets';F.mkdir(exist_ok=True)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
names=['level0','level1','level2','level3'];before={n:digest(W/n) for n in names}
files={n:UnityPy.load(str(W/n)).file for n in names}
old={n:{i:o.get_raw_data() for i,o in f.objects.items()} for n,f in files.items()}
report=build_lobby_assets_v21(files)
for n,f in files.items():
 (F/n).write_bytes(f.save());files[n]=UnityPy.load(str(F/n)).file
e=MenuEditor(files['level0']);paths=e.paths()[2]
for path in ['Menu/Pages/InRoom/Buttons/CC_LobbyClose','Menu/Pages/InRoom/CC_LobbyChangeTeam']:
 button=e.component(paths[path],BUTTON);raw=button.get_raw_data();_,event=button_layout(raw)
 assert struct.unpack_from('<I',raw,event)[0]==0,'cloned callbacks must not ready/leave the room'
 assert e.component(paths[path+'/Text'],572)
 # Text children are decoration, parent remains a clickable ray target.
 assert e.component(paths[path],1430).get_raw_data()[60]==1
controllers=[]
for i,o in files['level0'].objects.items():
 if o.type.name=='MonoBehaviour' and i in old['level0']:
  raw=old['level0'][i]
  # Every original MonoBehaviour must remain byte-identical except any source
  # UI templates explicitly shared with the cloned label (none expected).
  assert o.get_raw_data()==raw,('original menu component modified',i)
for name,net in report['nets'].items():
 assert net['solid'] and 8.9<net['world_size'][0]<9.1 and .8<net['world_size'][1]<1.1 and .04<net['world_size'][2]<.06
 assert files[name].objects[net['collider_id']].read_typetree()['m_Enabled']
 for i,o in files[name].objects.items():assert o.get_raw_data()==old[name][i],('unexpected scene mutation',name,i)
# Second application reuses named controls without extra objects/listeners.
counts={n:len(f.objects) for n,f in files.items()};build_lobby_assets_v21(files)
assert {n:len(f.objects) for n,f in files.items()}==counts
assert {n:digest(W/n) for n in names}==before,'working files modified'
report.update(passed=True,original_controller_bytes_preserved=True,scene_bytes_unchanged=True,idempotent=True,working_files_unchanged=True)
(R/'analysis/v21-lobby-assets-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
