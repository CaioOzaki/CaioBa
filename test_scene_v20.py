"""Strict object/field whitelist for Settings and indoor banner repair."""
from pathlib import Path
import json, struct, sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy, numpy as np
from build_scene_v20 import build_scene_assets, hierarchy, SETTINGS_ROWS, relocate_banners

BASE=R/'versions/cloudcourt-v19-antes-v20';OUT=R/'visuals-v20-scene'
before={n:UnityPy.load(str(BASE/n)).file for n in ('level0','level3')}
after={n:UnityPy.load(str(OUT/n)).file for n in ('level0','level3')}
report=json.loads((OUT/'scene-report.json').read_text())
checks={}
for name in before:
 old,new=before[name],after[name];allowed=set(report[name]['changed_object_ids'])
 assert set(old.objects)==set(new.objects) and len(old.types)==len(new.types)
 assert old.externals==new.externals
 actual={i for i in old.objects if old.objects[i].get_raw_data()!=new.objects[i].get_raw_data()}
 assert actual==allowed,(name,actual,allowed)
 for i in set(old.objects)-allowed:assert old.objects[i].get_raw_data()==new.objects[i].get_raw_data()
 for i in actual:
  a,b=old.objects[i],new.objects[i];assert a.type.name==b.type.name
  if name=='level3':
   assert a.type.name=='Mesh' and i==report['level3']['mesh_id']
   da,db=a.read_typetree(),b.read_typetree()
   assert da['m_IndexBuffer']==db['m_IndexBuffer'] and da['m_VertexData']['m_Channels']==db['m_VertexData']['m_Channels']
   va,vb=bytes(da['m_VertexData']['m_DataSize']),bytes(db['m_VertexData']['m_DataSize']);stride=len(va)//da['m_VertexData']['m_VertexCount']
   for offset in range(0,len(va),stride):assert va[offset+4:offset+stride]==vb[offset+4:offset+stride],'Only X positions may move'
  elif a.type.name=='RectTransform':
   da,db=a.read_typetree(),b.read_typetree();delta={k for k in da if da[k]!=db[k]}
   assert delta<=set(['m_AnchorMin','m_AnchorMax','m_Pivot','m_AnchoredPosition','m_LocalPosition','m_SizeDelta','m_LocalScale','m_RootOrder','m_Children'])
   assert da['m_GameObject']==db['m_GameObject'] and da['m_Father']==db['m_Father']
  else:
   assert a.type.name=='MonoBehaviour'
   ra,rb=a.get_raw_data(),b.get_raw_data();script=struct.unpack_from('<q',ra,20)[0];assert len(ra)==len(rb)
   changed={j for j,(x,y) in enumerate(zip(ra,rb)) if x!=y}
   if script==572:
    assert changed<=set([60,*range(84,88),*range(100,104)])
    assert ra[72:84]==rb[72:84] and not rb[60],'Font/raycast contract changed'
   else:assert script==465 and changed<=set(range(60,68))
 checks[name]={'changed_ids':sorted(actual),'unchanged_objects':len(old.objects)-len(actual)}

gs,ts,paths=hierarchy(after['level0']);centers=[]
for row,names in enumerate(SETTINGS_ROWS):
 for col,name in enumerate(names):
  t=ts[paths['Menu/Pages/Settings/'+name]];p=t['m_AnchoredPosition'];assert p=={'x':-124. if col==0 else 124.,'y':132.-row*44}
  assert t['m_SizeDelta']=={'x':216.,'y':36.};centers.append((p['x'],p['y']))
assert len(set(centers))==12
for name in ('Sets Button','Points Button'):
 assert not gs[ts[paths['Menu/Pages/Settings/'+name]]['m_GameObject']['m_PathID']]['m_IsActive']
assert report['level3']['old_intersections']==12 and report['level3']['new_intersections']==0
assert min(r['minimum_structure_clearance_m'] for r in report['level3']['components'])>.27
for obj in before['level3'].objects.values():
 if 'Collider' in obj.type.name:assert obj.get_raw_data()==after['level3'].objects[obj.path_id].get_raw_data()

# Apply the in-memory transforms again: no duplicate components or drift.
oldraw={n:{i:o.get_raw_data() for i,o in f.objects.items()} for n,f in after.items()}
again=build_scene_assets(after)
assert all(oldraw[n]=={i:o.get_raw_data() for i,o in f.objects.items()} for n,f in after.items())
result={'passed':True,'files':checks,'checks':['strict object and byte-field whitelist','font references and button events unchanged','sets/points remain hidden','12 controls arranged without overlap','12 old banner/frame intersections removed','at least 27cm structural clearance','all colliders unchanged','idempotent in-memory transforms'],
        'native_outline_helper':'score_outline_v20.c must be integrated after runtime font assignment; no copied MonoBehaviour schema',
        'VR_render_tested':False}
(R/'analysis/v20-scene-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
