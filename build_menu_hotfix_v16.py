"""Repair only the two menu-related files of an installed v16 candidate."""
import argparse,copy,hashlib,json,os,shutil
from pathlib import Path
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
from menu_visibility_v16 import apply_menu_visibility,contrast,LIGHT,STATES
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--font-baseline',type=Path,required=True);a=p.parse_args()
manifest=json.loads((R/'distribution/Volley-Riot-v16/patch.json').read_text());rows={f['path']:f for f in manifest['files']}
out=R/'visuals-v16';prior=R/'versions/v16-before-menu-fix';gen=TypeTreeGenerator(UnityPy.load(str(a.game/'VolleyballFever_Data/level0')).file.unity_version);gen.load_local_dll_folder(str(R/'tools/dump/DummyDll'))
changes=[]
for name in ['level0','sharedassets0.assets']:
 rel='VolleyballFever_Data/'+name;src=a.game/rel;raw=src.read_bytes()
 allowed=[rows[rel]['modified_sha256']]+[x['sha256'] for x in rows[rel].get('additional_versions',[])]
 assert hashlib.sha256(raw).hexdigest() in allowed,('unexpected installed input',rel)
 backup=prior/rel;backup.parent.mkdir(parents=True,exist_ok=True)
 if backup.exists():assert backup.read_bytes()==raw
 else:backup.write_bytes(raw)
 env=UnityPy.load(str(src));env.typetree_generator=gen
 if name=='level0':changes.append(apply_menu_visibility(env.file))
 else:
  baseline=UnityPy.load(str(a.font_baseline));original=baseline.file.objects[188].read_typetree()
  assert original['m_FontData'] and 'norwester' in original['m_Name'].lower()
  env.file.objects[188].save_typetree(original)
  changes.append({'font':'restored native menu font from verified v15 baseline'})
 data=env.file.save();dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 check=UnityPy.load(str(dest));check.typetree_generator=gen
 assert len(check.file.objects)==len(env.file.objects)
 for obj in check.file.objects.values():
  if obj.type.name in ['Font','RectTransform']:obj.read_typetree()
 m=json.loads((out/'manifest.json').read_text());next(f for f in m if f['path']==rel)['after']=hashlib.sha256(data).hexdigest();(out/'manifest.json').write_text(json.dumps(m,indent=2))
report={'changes':changes,'minimum_button_contrast':min(contrast(LIGHT,c) for c in STATES.values()),'scope':'menu colors, cached vertex colors and native menu font only; gameplay and online protocol unchanged'}
(R/'analysis/v16-menu-visibility.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
