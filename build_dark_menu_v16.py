"""Apply the requested dark-button/light-letter palette to the current menu."""
import argparse,hashlib,json
from pathlib import Path
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
from menu_visibility_v16 import apply_menu_visibility
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);a=p.parse_args()
rel='VolleyballFever_Data/level0';source=a.game/rel;raw=source.read_bytes()
expected='bcc66abbcdebf4e33fe74a29d9026f331033bf72bc98190dd76bd25d61233445'
assert hashlib.sha256(raw).hexdigest()==expected,'Installed version changed'
prior=R/'versions/v16.1-before-dark-menu'/rel;prior.parent.mkdir(parents=True,exist_ok=True)
if prior.exists():assert prior.read_bytes()==raw
else:prior.write_bytes(raw)
env=UnityPy.load(str(source));gen=TypeTreeGenerator(env.file.unity_version);gen.load_local_dll_folder(str(R/'tools/dump/DummyDll'));env.typetree_generator=gen
report=apply_menu_visibility(env.file);data=env.file.save();(R/'visuals-v16'/rel).write_bytes(data)
manifest=R/'visuals-v16/manifest.json';m=json.loads(manifest.read_text());next(f for f in m if f['path']==rel)['after']=hashlib.sha256(data).hexdigest();manifest.write_text(json.dumps(m,indent=2))
print(json.dumps(report))
