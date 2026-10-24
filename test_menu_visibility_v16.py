"""Inspect the saved menu assets, not a separate mockup of their colors."""
import hashlib,json
from pathlib import Path
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
from menu_visibility_v16 import contrast
R=Path(__file__).resolve().parent;new=R/'visuals-v16/VolleyballFever_Data';old=R/'versions/v16-before-menu-fix/VolleyballFever_Data'
g=TypeTreeGenerator(UnityPy.load(str(new/'level0')).file.unity_version);g.load_local_dll_folder(str(R/'tools/dump/DummyDll'))
def load(path):e=UnityPy.load(str(path));e.typetree_generator=g;return e.file
file=load(new/'level0');prior=load(old/'level0');trees={}
for o in file.objects.values():
 if o.type.name in ['MonoBehaviour','GameObject','RectTransform','Transform']:
  try:trees[o.path_id]=o.read_typetree()
  except Exception:pass
parents={d['m_GameObject']['m_PathID']:trees.get(d.get('m_Father',{}).get('m_PathID'),{}).get('m_GameObject',{}).get('m_PathID') for d in trees.values() if 'm_LocalPosition' in d}
buttons={d['m_GameObject']['m_PathID']:d for d in trees.values() if 'm_Colors' in d and 'm_TargetGraphic' in d}
ratios=[];labels=0
for pid,d in trees.items():
 if 'm_Text' not in d:continue
 go=d['m_GameObject']['m_PathID'];visited=set()
 while go and go not in buttons and go not in visited:visited.add(go);go=parents.get(go)
 if go not in buttons:continue
 button=buttons[go];image=trees[button['m_TargetGraphic']['m_PathID']];assert image['m_Enabled'] and image['m_Color']['a']==1
 assert d['m_Color']['a']==1
 for state in ['m_NormalColor','m_HighlightedColor','m_SelectedColor','m_PressedColor','m_DisabledColor']:
  tint=button['m_Colors'][state];assert tint['a']==1
  effective={k:image['m_Color'][k]*tint[k] for k in 'rgb'}
  ratio=contrast(d['m_Color'],effective);assert ratio>=7,(pid,state,ratio);ratios.append(ratio)
 labels+=1
for pid,d in trees.items():
 if 'm_OnClick' in d:
  before=prior.objects[pid].read_typetree(nodes=file.objects[pid]._get_typetree_node(None));assert d['m_OnClick']==before['m_OnClick'] and d['m_Navigation']==before['m_Navigation']
 if 'savedColor' in d:
  go=d['m_GameObject']['m_PathID'];graphics=[x for x in trees.values() if x.get('m_GameObject',{}).get('m_PathID')==go and 'm_Color' in x]
  if graphics:assert d['savedColor']==graphics[0]['m_Color'],('stale CurvedUI color',pid)
font_file=load(new/'sharedassets0.assets');old_font_file=load(old/'sharedassets0.assets')
baseline=load(R/'tools/v16-fixture-v15/VolleyballFever_Data/sharedassets0.assets')
assert font_file.objects[188].get_raw_data()==baseline.objects[188].get_raw_data()
for pid,obj in font_file.objects.items():
 if pid!=188:assert obj.get_raw_data()==old_font_file.objects[pid].get_raw_data(),('unexpected shared asset change',pid)
report={'passed':True,'selectables':len(buttons),'button_labels':labels,'checked_color_states':len(ratios),'minimum_contrast':min(ratios),'native_menu_font':'byte-identical to working v15 font','callbacks':'unchanged','shared_assets':'only legacy font object changed','scope':'serialized asset and contrast verification; headset visual confirmation pending'}
(R/'analysis/v16-menu-visibility-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
