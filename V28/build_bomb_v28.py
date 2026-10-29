"""Compose v28 Bomb areas into any compatible resources.assets in memory.
Only Bomb team/area nodes change. New nodes have no colliders/renderers.
No working assets or installation are mutated by default.
"""
from pathlib import Path
import argparse,copy,hashlib,json,struct,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from build_menu_v19 import set_raw,save_tree,ptr

def apply_bomb_v28(file):
 before={i:o.get_raw_data() for i,o in file.objects.items()};created=[]
 def clone(source):
  obj=copy.copy(source);obj.path_id=max(file.objects)+1;obj.assets_file=file
  set_raw(obj,source.get_raw_data());file.objects[obj.path_id]=obj;created.append(obj.path_id);return obj.path_id
 def get_transform(go):
  d=file.objects[go].read_typetree()
  return next(c['component']['m_PathID'] for c in d['m_Component'] if file.objects[c['component']['m_PathID']].type.name=='Transform')
 # Exact serialized GameRules references in the recorded compatible build.
 rules=file.objects[1247];raw=rules.get_raw_data();assert len(raw)==168 and raw[152]==1
 teams=[struct.unpack_from('<q',raw,132+12*i)[0] for i in range(2)]
 report=[]
 for team_index,teamid in enumerate(teams):
  team=file.objects[teamid];traw=bytearray(team.get_raw_data());assert len(traw)==88 and struct.unpack_from('<i',traw,32)[0]==4
  area0=struct.unpack_from('<q',traw,40)[0];area_source=file.objects[area0];araw=area_source.get_raw_data();assert len(araw)==76
  ago=struct.unpack_from('<q',araw,4)[0];at=get_transform(ago);ad=file.objects[at].read_typetree();parent=ad['m_Father']['m_PathID']
  default=struct.unpack_from('<q',araw,60)[0];dd=file.objects[default].read_typetree();dgo=dd['m_GameObject']['m_PathID']
  # Idempotence: keep an existing v28 roster intact on a second composition.
  remaining=[struct.unpack_from('<q',traw,40+12*i)[0] for i in range(1,4)]
  if all(remaining):
   report.append(dict(team=team_index,areas=[area0]+remaining,reused=True));continue
  areas=[area0];transforms=[at];defaults=[default]
  for slot in range(1,4):
   ng=clone(file.objects[ago]);nt=clone(file.objects[at]);na=clone(area_source)
   ndg=clone(file.objects[dgo]);ndt=clone(file.objects[default])
   gd=file.objects[ng].read_typetree();gd['m_Name']='CC_BombArea_v28_'+str(slot);gd['m_Component']=[{'component':ptr(nt)},{'component':ptr(na)}];save_tree(file.objects[ng],gd)
   ndgd=file.objects[ndg].read_typetree();ndgd['m_Name']='DefaultPoint';ndgd['m_Component']=[{'component':ptr(ndt)}];save_tree(file.objects[ndg],ndgd)
   td=copy.deepcopy(ad);td['m_GameObject']=ptr(ng);td['m_Children']=[ptr(ndt)];save_tree(file.objects[nt],td)
   dtd=copy.deepcopy(dd);dtd['m_GameObject']=ptr(ndg);dtd['m_Father']=ptr(nt);save_tree(file.objects[ndt],dtd)
   nr=bytearray(araw);struct.pack_into('<q',nr,4,ng);struct.pack_into('<q',nr,60,ndt);set_raw(file.objects[na],nr)
   pd=file.objects[parent].read_typetree();pd['m_Children'].append(ptr(nt));save_tree(file.objects[parent],pd)
   areas.append(na);transforms.append(nt);defaults.append(ndt)
  sign=-1 if team_index==0 else 1
  # Parent team is at its own baseline (+/-4.5), with identity rotation.
  base_z=file.objects[parent].read_typetree()['m_LocalPosition']['z']
  assert abs(base_z-sign*4.5)<.001
  for slot,(aid,tid,did) in enumerate(zip(areas,transforms,defaults)):
   x=-1. if slot<2 else 1.;z=sign*(3.375 if slot in (0,3) else 1.125)
   td=file.objects[tid].read_typetree();td['m_LocalPosition']=dict(x=x,y=1.,z=z-base_z);save_tree(file.objects[tid],td)
   dtd=file.objects[did].read_typetree();dtd['m_LocalPosition']=dict(x=0.,y=-1.,z=0.);save_tree(file.objects[did],dtd)
   ar=bytearray(file.objects[aid].get_raw_data());struct.pack_into('<3f',ar,32,2.,2.,2.25);struct.pack_into('<q',ar,48,areas[(slot+1)%4]);ar[68]=int(slot==0);ar[72]=int(slot in (0,3));set_raw(file.objects[aid],ar)
   struct.pack_into('<q',traw,40+12*slot,aid)
  set_raw(team,traw);report.append(dict(team=team_index,areas=areas,positions=[[-1,3.375*sign],[-1,1.125*sign],[1,1.125*sign],[1,3.375*sign]]))
 changed=[i for i,b in before.items() if file.objects[i].get_raw_data()!=b]
 return dict(changed_existing_ids=changed,added_ids=created,teams=report,new_colliders=0,new_renderers=0,bounds=dict(half_width=2.,half_length=4.5),original_rules_visuals_and_serve_points_identical=all(file.objects[i].get_raw_data()==before[i] for i in (1247,496,537,549,531)))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 f=UnityPy.load(str(args.source)).file;report=apply_bomb_v28(f);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(f.save());print(json.dumps(report,indent=2))
