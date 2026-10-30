"""In-memory V30 pause-menu Settings access using the native controller.
A full modal backdrop prevents clicks leaking to the still-owned InGame page.
"""
from build_menu_v19 import MenuEditor,IMAGE,save_tree,set_raw,button_layout

def apply_match_settings_v30(menu):
 e=MenuEditor(menu);s='Menu/Pages/Settings'
 e.button('Menu/Pages/InGame/CC_MatchSettings','SETTINGS',265,22,200,40,17)
 blocker=e.ensure(s+'/CC_MatchSettingsBlocker','Menu/Pages/Alert/Background')
 e.rect(blocker,0,0,800,400);e.color(blocker,(.045,.09,.15,.99))
 image=e.component(blocker,IMAGE);b=bytearray(image.get_raw_data());b[60]=1;set_raw(image,b)
 e.active(blocker,False)
 # Draw the blocker behind Settings controls, but place the full Settings
 # page after InGame among siblings so its modal catches rays first.
 st=e.find(s);t=menu.objects[st];d=t.read_typetree()
 d['m_Children']=[x for x in d['m_Children'] if x['m_PathID']!=blocker]
 d['m_Children'].insert(0,dict(m_FileID=0,m_PathID=blocker));save_tree(t,d)
 parent=menu.objects[d['m_Father']['m_PathID']];pd=parent.read_typetree()
 pd['m_Children']=[x for x in pd['m_Children'] if x['m_PathID']!=st]
 pd['m_Children'].append(dict(m_FileID=0,m_PathID=st));save_tree(parent,pd)
 e.text(e.find(s+'/CC_AudioControls/CC_PlaylistCredit'),'NEW LOFI PLAYLIST  /  3 original CC0 tracks',15)
 return dict(created=e.created,native_controller_reused=True,available_in_match=['Game','Sound'],modal_backdrop_default_active=False,native_pause_ownership_preserved=True)
