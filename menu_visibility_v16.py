"""High-contrast VR menu styling, including CurvedUI's serialized color cache."""
import copy

def rgba(value):
 return {**{k:int(value[i:i+2],16)/255 for k,i in zip('rgb',(0,2,4))},'a':1.}
DARK=rgba('10233F');LIGHT=rgba('FFF5DC');WHITE=rgba('FFFFFF')
STATES={'m_NormalColor':rgba('263B56'),'m_HighlightedColor':rgba('2B4669'),'m_SelectedColor':rgba('324D70'),'m_PressedColor':rgba('553141'),'m_DisabledColor':rgba('26303F')}

def apply_menu_visibility(file):
 trees={}
 for obj in file.objects.values():
  if obj.type.name in ['GameObject','Transform','RectTransform','MonoBehaviour']:
   try:trees[obj.path_id]=obj.read_typetree()
   except Exception:pass
 parents={d['m_GameObject']['m_PathID']:trees.get(d.get('m_Father',{}).get('m_PathID'),{}).get('m_GameObject',{}).get('m_PathID') for d in trees.values() if 'm_LocalPosition' in d}
 buttons={d['m_GameObject']['m_PathID'] for d in trees.values() if 'm_Colors' in d and 'm_TargetGraphic' in d}
 graphics={d['m_GameObject']['m_PathID']:copy.deepcopy(d['m_Color']) for d in trees.values() if 'm_Color' in d and 'm_GameObject' in d};count=0
 for pid,d in trees.items():
  if 'm_Colors' not in d or 'm_TargetGraphic' not in d:continue
  d['m_Colors'].update(copy.deepcopy(STATES));d['m_Colors']['m_ColorMultiplier']=1.
  file.objects[pid].save_typetree(d);count+=1
  target=d['m_TargetGraphic'];gid=target['m_PathID']
  if target['m_FileID']==0 and gid in trees and 'm_Sprite' in trees[gid]:
   image=trees[gid];image['m_Color']=WHITE.copy();image['m_Enabled']=1
   image['m_FillCenter']=1;image['m_FillAmount']=1.
   file.objects[gid].save_typetree(image);graphics[image['m_GameObject']['m_PathID']]=WHITE.copy()
 def on_button(go):
  seen=set()
  while go and go not in seen:
   if go in buttons:return True
   seen.add(go);go=parents.get(go)
  return False
 labels=0
 for pid,d in trees.items():
  if 'm_Text' not in d:continue
  d['m_Color']=LIGHT.copy()
  if 'm_FontData' in d and on_button(d['m_GameObject']['m_PathID']):
   fd=d['m_FontData'];fd['m_BestFit']=1;fd['m_MinSize']=10;fd['m_MaxSize']=max(10,fd['m_FontSize'])
  file.objects[pid].save_typetree(d);graphics[d['m_GameObject']['m_PathID']]=d['m_Color'].copy();labels+=1
 caches=0
 for pid,d in trees.items():
  if 'savedColor' in d and d.get('m_GameObject',{}).get('m_PathID') in graphics:
   d['savedColor']=graphics[d['m_GameObject']['m_PathID']].copy();file.objects[pid].save_typetree(d);caches+=1
 return {'selectables':count,'labels':labels,'curved_ui_caches':caches}

def contrast(a,b):
 def lum(c):
  f=lambda x:x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
  return sum(w*f(c[k]) for w,k in zip([.2126,.7152,.0722],'rgb'))
 x,y=sorted([lum(a),lum(b)]);return (y+.05)/(x+.05)
