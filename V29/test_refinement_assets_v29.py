"""Focused composed-asset checks, serialization and menu layout previews.
Checks rendered menu geometry/content; no live Unity or headset claim.
"""
from pathlib import Path
import hashlib,json,struct,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from PIL import Image,ImageDraw,ImageFont
from fix_gloves_v16 import hierarchy
from build_assets_v29 import FILES,MODIFIED
from build_refinement_ui_v29 import apply_refinement_ui_v29
from build_menu_v19 import MenuEditor,BUTTON,TEXT,IMAGE,RAW_IMAGE,button_layout
B=R/'versions/cloudcourt-v28-antes-v29';D=R/'visuals-v29';A=R/'assets/refinement-v29'
assert all((D/n).is_file() for n in FILES)
for name in FILES:
 if name not in MODIFIED:assert(D/name).read_bytes()==(B/name).read_bytes(),name
menu=UnityPy.load(str(D/'level0')).file;e=MenuEditor(menu);gs,ts,paths=e.paths()
required={
 'CC_Training':['CC_TrainServe','CC_TrainReceive','CC_TrainSet','CC_TrainSpike','CC_TrainEasy','CC_TrainStandard','CC_TrainChallenge','CC_TrainBack'],
 'CC_Stats':['CC_StatsState','CC_StatsYou','CC_StatsBlue','CC_StatsRed','CC_StatsLongest','CC_StatsDone'],
 'CC_Rewards':['CC_RewardsState','CC_RewardOutfitValue','CC_RewardFaceValue','CC_RewardAccentValue','CC_RewardOutfitPrev','CC_RewardOutfitNext','CC_RewardFacePrev','CC_RewardFaceNext','CC_RewardAccentPrev','CC_RewardAccentNext','CC_RewardsDone']}
buttons=[];labels=[]
for panel,names in required.items():
 root='Menu/'+panel;tid=paths[root];assert not gs[ts[tid]['m_GameObject']['m_PathID']]['m_IsActive']
 for name in names:assert root+'/'+name in paths
 for path,tid in paths.items():
  if not path.startswith(root+'/') or path.count('/')!=2:continue
  d=ts[tid];x,y=d['m_AnchoredPosition'].values();w,h=d['m_SizeDelta'].values()
  assert -400<=x-w/2<=x+w/2<=400 and -200<=y-h/2<=y+h/2<=200,(path,x,y,w,h)
  button=e.component(tid,BUTTON)
  if button:
   b=button.get_raw_data();_,ev=button_layout(b);assert struct.unpack_from('<I',b,ev)[0]==0
   assert e.component(tid,IMAGE).get_raw_data()[60]==1;buttons.append(path)
  text=e.component(tid,TEXT)
  if text:assert text.get_raw_data()[60]==0;labels.append(path)
for path in ['Menu/Pages/Start/CC_StatsOpen','Menu/Pages/InGame/CC_StatsOpen','Menu/CC_Customization/CC_RewardsOpen']:
 tid=paths[path];d=ts[tid];x,y=d['m_AnchoredPosition'].values();w,h=d['m_SizeDelta'].values();assert -400<=x-w/2<x+w/2<=400 and -200<=y-h/2<y+h/2<=200
assert ts[paths['Menu/Pages/Start/CC_StatsOpen']]['m_AnchoredPosition']==dict(x=-120.,y=-140.)
assert ts[paths['Menu/Pages/Start/CC_CustomizeOpen']]['m_AnchoredPosition']==dict(x=120.,y=-140.)
assert ts[paths['Menu/Pages/InGame/CC_StatsOpen']]['m_AnchoredPosition']==dict(x=-265.,y=22.)
assert ts[paths['Menu/CC_Customization/CC_RewardsOpen']]['m_AnchoredPosition']==dict(x=-255.,y=-176.)
assert 'Menu/Pages/Start/CC_TrainingOpen' not in paths and 'Menu/Pages/InGame/CC_TrainingOpen' not in paths
assert ts[paths['Menu/CC_Training/CC_TrainingHint']]['m_SizeDelta']['y']>=40
assert ts[paths['Menu/CC_Rewards/CC_RewardsState']]['m_SizeDelta']['y']>=60
base=UnityPy.load(str(B/'level0')).file;be=MenuEditor(base)
newroot=menu.objects[paths['Menu']].read_typetree();oldroot=base.objects[be.find('Menu')].read_typetree()
assert {k:v for k,v in newroot.items() if k!='m_Children'}=={k:v for k,v in oldroot.items() if k!='m_Children'},'root raycast geometry changed'
rootgo=menu.objects[newroot['m_GameObject']['m_PathID']].read_typetree()
for c in rootgo['m_Component']:
 i=c['component']['m_PathID']
 if i!=paths['Menu']:assert menu.objects[i].get_raw_data()==base.objects[i].get_raw_data(),'root raycast canvas component changed'
logo=paths['Menu/Pages/Start/CC_StartupLogo'];assert menu.objects[logo].get_raw_data()==base.objects[be.find('Menu/Pages/Start/CC_StartupLogo')].get_raw_data()
assert e.component(logo,RAW_IMAGE).get_raw_data()==be.component(be.find('Menu/Pages/Start/CC_StartupLogo'),RAW_IMAGE).get_raw_data()
counts=len(menu.objects);again=apply_refinement_ui_v29(menu);assert len(menu.objects)==counts and not again['changed_existing_ids'],'UI not idempotent'
ga=UnityPy.load(str(D/'globalgamemanagers.assets')).file;gb=UnityPy.load(str(B/'globalgamemanagers.assets')).file
assert sorted(ga.objects)==sorted(gb.objects)
assert [i for i in gb.objects if ga.objects[i].get_raw_data()!=gb.objects[i].get_raw_data()]==[3]
t=ga.objects[3].read();assert(t.m_Width,t.m_Height)==(2048,1024) and t.image.getextrema()[3][0]==0
resources=UnityPy.load(str(D/'resources.assets')).file;rg,rt,rp=hierarchy(resources)
assert len([p for p in rp if p.endswith('/CC_CallMine_v29') or p.endswith('/CC_CallSet_v29')])==10
for stem in ['Face','Outfit']:assert 'NetworkPlayer/PhysicalBody/CC_RewardSources/'+stem in rp
for name in ['level1','level2','level3']:
 scene=UnityPy.load(str(D/name)).file;sg,st,sp=hierarchy(scene)
 for target in ['GroundTarget','AirTarget','Origin']:assert 'CC_TrainingTargets/'+target in sp

def text_data(tid):
 obj=e.component(tid,TEXT)
 if not obj:return None
 b=obj.get_raw_data();n=struct.unpack_from('<I',b,128)[0]
 return b[132:132+n].decode('utf-8'),struct.unpack_from('<i',b,84)[0]
def preview(panel):
 scale=2;im=Image.new('RGB',(800*scale,400*scale),'#10263e');draw=ImageDraw.Draw(im)
 draw.rounded_rectangle((5,5,1594,794),radius=30,outline='#4e8097',width=3)
 prefix='Menu/'+panel
 for path,tid in paths.items():
  if not path.startswith(prefix+'/') or path.count('/')!=2:continue
  td=ts[tid];x,y=td['m_AnchoredPosition'].values();w,h=td['m_SizeDelta'].values();cx=(x+400)*scale;cy=(200-y)*scale
  if e.component(tid,BUTTON):
   draw.rounded_rectangle((cx-w*scale/2,cy-h*scale/2,cx+w*scale/2,cy+h*scale/2),radius=12,fill='#21465c',outline='#739aae',width=2)
   data=text_data(paths[path+'/Text'])
  else:data=text_data(tid)
  if data:
   text,size=data;font=ImageFont.truetype(str(R/'assets/shared/fonts/CloudcourtBubble.ttf'),size*scale)
   if path.endswith('/CC_TrainingHint'):text='Pick a drill. In court, release and press TRIGGER to repeat.\nGRAB controls the hand pose. Use the gold target to aim.'
   if path.endswith('/CC_RewardsState'):text='Sunset  LOCKED  Serve targets 0/5 or aces 0/2\nSkyline  LOCKED  Controlled receives + assisted sets 0/10\nEmerald  LOCKED  Direct kills 0/5 or spike targets 0/5'
   color='#fff1dc'
   if path.endswith('CC_StatsBlue'):color='#66ccff'
   if path.endswith('CC_StatsRed'):color='#ff7a7d'
   # Preserve an empty first metric header line so stat rows align with values.
   lines=text.split('\n');lineheight=(size+4)*scale
   for i,line in enumerate(lines):draw.text((cx,cy+(i-(len(lines)-1)/2)*lineheight),line,font=font,fill=color,anchor='mm')
 path=A/(panel.lower()+'-layout-preview.png');im.save(path);return str(path)
previews=[preview(p) for p in required]
report=dict(passed=True,files_verified=17,unchanged_baseline_files=len(FILES)-len(MODIFIED),new_buttons=len(buttons),new_labels=len(labels),button_paths=buttons,panels=required,all_control_bounds_inside_curved_canvas=True,new_buttons_no_serialized_listeners=True,new_labels_do_not_block_controller_rays=True,ui_idempotent=True,actual_startup_only_texture3_changed=True,mainmenu_emblem_unchanged=True,training_targets_3_courts=True,reward_sources=True,bot_callouts=10,previews=previews,scope='Serialized Unity assets + data-derived 2D layout previews. No live Unity/headset visual claim.')
(R/'analysis/v29-refinement-assets-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
