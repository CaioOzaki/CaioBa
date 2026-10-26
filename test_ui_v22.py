"""Strict modal layout and raycast scope; no working/live writes."""
from pathlib import Path
import json,sys,struct
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_ui_v22 import build_menu
from build_menu_v19 import MenuEditor,script,IMAGE,TEXT,RAW_IMAGE,BUTTON,button_layout
src=R/'versions/cloudcourt-v21-antes-v22/level0'
f=UnityPy.load(str(src)).file;before={i:o.get_raw_data() for i,o in f.objects.items()}
e=MenuEditor(f);_,_,paths=e.paths();modal='Menu/CC_Customization'
allowed={tid for p,tid in paths.items() if p.startswith(modal)}
for t in list(allowed):
 go=f.objects[f.objects[t].read_typetree()['m_GameObject']['m_PathID']].read_typetree()
 allowed.update(x['component']['m_PathID'] for x in go['m_Component'])
report=build_menu(f);changed=set(report['changed_existing_ids']);assert changed<=allowed
assert not report['created_ids'] and report['canvas_unchanged']
assert all(f.objects[i].get_raw_data()==raw for i,raw in before.items() if i not in allowed)
assert not build_menu(f)['changed_existing_ids'],'must be idempotent'
controls=[]
for path,t in paths.items():
 if not path.startswith(modal+'/'):continue
 d=f.objects[t].read_typetree();button=e.component(t,BUTTON)
 if button:
  x,y=d['m_AnchoredPosition'].values();w,h=d['m_SizeDelta'].values()
  assert abs(x)+w/2<=400 and abs(y)+h/2<200,(path,x,y,w,h)
  graphic=e.component(t,IMAGE);assert graphic.get_raw_data()[60]==1
  raw=button.get_raw_data();target,event=button_layout(raw)
  assert struct.unpack_from('<I',raw,event)[0]==0,'modal button must not navigate pages'
  controls.append(path.rsplit('/',1)[-1])
 for kind in (TEXT,RAW_IMAGE):
  g=e.component(t,kind)
  if g:assert g.get_raw_data()[60]==0,'decorative preview/label intercepts click'
report.update(passed=True,controls=controls,unchanged_outside_modal=True,idempotent=True,all_buttons_inside_original_canvas=True,modal_buttons_have_no_navigation_callbacks=True)
(R/'analysis/v22-ui-asset-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
