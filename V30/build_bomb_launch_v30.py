"""Restore native human placement markers omitted from the V28 Bomb areas.
BotArea.PlayAreaPlacement is found with GetComponentInChildren by native human
placement. DefaultPoint alone is sufficient for bots, but not NetworkPlayer.
Add only missing invisible native marker nodes; preserve rules, rally/fuse code,
serve points, court geometry, colliders and the complete 2v2/4v4 area cycles.
"""
import copy,struct
from fix_gloves_v16 import hierarchy
from build_menu_v19 import ptr,save_tree,set_raw

def bomb_placement_audit_v30(file):
 gs,ts,paths=hierarchy(file);rows=[]
 def descendants(t):
  yield t
  for child in ts[t]['m_Children']:
   if child['m_FileID']==0:yield from descendants(child['m_PathID'])
 for aid in (1209,1432,1437,1442,1212,1447,1452,1457):
  raw=file.objects[aid].get_raw_data();assert len(raw)==76
  go=struct.unpack_from('<q',raw,4)[0];default=struct.unpack_from('<q',raw,60)[0]
  area=next(x['component']['m_PathID'] for x in gs[go]['m_Component'] if file.objects[x['component']['m_PathID']].type.name=='Transform')
  markers=[]
  for t in descendants(area):
   for c in gs[ts[t]['m_GameObject']['m_PathID']]['m_Component']:
    o=file.objects[c['component']['m_PathID']]
    if o.type.name=='MonoBehaviour':
     b=o.get_raw_data()
     if len(b)==32 and struct.unpack_from('<iq',b,16)==(1,1064):markers.append(o.path_id)
  rows.append(dict(area=aid,transform=area,default=default,default_valid=default in ts and ts[default]['m_Father']['m_PathID']==area,placements=markers))
 return rows

def apply_bomb_launch_v30(file):
 before={i:o.get_raw_data() for i,o in file.objects.items()};rows=bomb_placement_audit_v30(file)
 missing=[x for x in rows if not x['placements']];added=[]
 source_transform=file.objects[534].read_typetree();source_go=source_transform['m_GameObject']['m_PathID']
 assert len(file.objects[1234].get_raw_data())==32
 def clone(oid):
  o=copy.copy(file.objects[oid]);o.path_id=max(file.objects)+1;o.assets_file=file
  set_raw(o,file.objects[oid].get_raw_data());file.objects[o.path_id]=o;added.append(o.path_id);return o.path_id
 for row in missing:
  go=clone(source_go);transform=clone(534);marker=clone(1234)
  g=file.objects[go].read_typetree();g['m_Name']='PlayAreaPlacement';g['m_Component']=[{'component':ptr(transform)},{'component':ptr(marker)}];save_tree(file.objects[go],g)
  t=file.objects[transform].read_typetree();t['m_GameObject']=ptr(go);t['m_Father']=ptr(row['transform']);t['m_Children']=[]
  t['m_LocalPosition']=file.objects[row['default']].read_typetree()['m_LocalPosition'];save_tree(file.objects[transform],t)
  b=bytearray(file.objects[marker].get_raw_data());struct.pack_into('<q',b,4,go);set_raw(file.objects[marker],b)
  parent=file.objects[row['transform']];p=parent.read_typetree();p['m_Children'].append(ptr(transform));save_tree(parent,p)
 after=bomb_placement_audit_v30(file)
 assert all(x['default_valid'] and len(x['placements'])==1 for x in after),after
 protected=(1247,1242,1221,496,537,549,531,1209,1432,1437,1442,1212,1447,1452,1457,534,1234)
 assert all(file.objects[i].get_raw_data()==before[i] for i in protected)
 changed=[i for i,b in before.items() if file.objects[i].get_raw_data()!=b]
 assert set(changed)=={x['transform'] for x in missing},changed
 return dict(missing_before=len(missing),missing_after=0,changed_existing_ids=changed,added_ids=added,areas=after,new_colliders=0,new_renderers=0,native_rules_and_bomb_flag_preserved=True)
