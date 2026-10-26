"""In-memory lobby controls and verification of each venue's solid practice net.

Reuse the scene collider that already aligns with the visible net. Adding a
second collider would create overlapping physics surfaces during matches.
"""
from pathlib import Path
import copy,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
from build_menu_v19 import MenuEditor,save_tree
from fix_gloves_v16 import hierarchy
from build_scene_v20 import _world

def build_lobby_menu_v21(menu):
 e=MenuEditor(menu)
 close=e.button('Menu/Pages/InRoom/Buttons/CC_LobbyClose','Practice / Close',0,-178,214,36,17)
 # InRoom can always be reopened using the controller menu input. This named
 # control also supports opening the selector from an available game menu.
 show=e.button('Menu/Pages/InRoom/CC_LobbyChangeTeam','Change Team',0,-218,214,36,17)
 return dict(close_button_transform=close,change_team_transform=show,
             close_action='lobby_selector_hide_v21',show_action='lobby_selector_show_v21',created=e.created)

def ensure_lobby_net_v21(scene):
 gs,ts,paths=hierarchy(scene);path='Environment/Net net';t=paths[path]
 gid=ts[t]['m_GameObject']['m_PathID'];go=gs[gid]
 collider=next(scene.objects[c['component']['m_PathID']] for c in go['m_Component']
               if scene.objects[c['component']['m_PathID']].type.name=='BoxCollider')
 data=collider.read_typetree();data['m_Enabled']=True;data['m_IsTrigger']=False;save_tree(collider,data)
 # Preserve serialized geometry/material/layers and all existing gameplay.
 assert go['m_IsActive'];matrix=_world(ts,t)
 center=[float(x) for x in matrix[:3,3]]
 assert abs(center[0])<.02 and abs(center[2])<.02 and 1.7<center[1]<2.1,center
 return dict(path=path,collider_id=collider.path_id,solid=True,center=center,
             world_size=[float(abs(matrix[i,i])*data['m_Size'][k]) for i,k in enumerate('xyz')],
             duplicate_colliders_added=0)

def build_lobby_assets_v21(files):
 return dict(menu=build_lobby_menu_v21(files['level0']),
             nets={name:ensure_lobby_net_v21(files[name]) for name in ['level1','level2','level3']})
