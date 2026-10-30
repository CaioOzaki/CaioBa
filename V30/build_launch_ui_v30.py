"""Remove the obsolete platform gate from the existing Solo Extras button.
The original Bomb Button is now the format-independent Extras entry. Its native
ActiveOnPlatform.Awake hides it on first Windows activation, after Solo layout.
Only that component is removed; native button, transform and routing stay intact.
"""
import struct
from build_menu_v19 import MenuEditor,save_tree

def apply_launch_ui_v30(menu):
 e=MenuEditor(menu);t=e.find('Menu/Pages/Solo/Bomb Button')
 tr=menu.objects[t].read_typetree();go=menu.objects[tr['m_GameObject']['m_PathID']];g=go.read_typetree()
 removed=[]
 for entry in list(g['m_Component']):
  oid=entry['component']['m_PathID'];o=menu.objects[oid]
  if o.type.name!='MonoBehaviour':continue
  raw=o.get_raw_data()
  if len(raw)==40 and struct.unpack_from('<iq',raw,16)==(1,957):
   g['m_Component'].remove(entry);removed.append(oid);del menu.objects[oid]
 assert len(removed)<=1,removed
 g['m_IsActive']=True;save_tree(go,g)
 return dict(extras_obsolete_platform_gate_removed=removed,extras_visible_on_first_solo=True)
