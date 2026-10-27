"""Run installed-output native lobby hooks and original attachment trampoline.

Reads working/GameAssembly.dll; mutates only emulator state and a JSON report.
"""
from pathlib import Path
import hashlib,json,struct
__file__=str(Path(__file__).with_name('test_lobby_v18.py'))
exec(Path(__file__).read_text().split('\nchecks=[]')[0])
class IntegratedLobbyEngine(LobbyEngine):
 def __init__(self,base):
  self.selector_visible=True;self.menu_down=False;self.angular={};self.triggers=[False,False]
  super().__init__(base);self.menu=self.alloc();self.ptr(self.page+0x68,self.menu)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c=[u.reg_read(reg) for reg in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==0xa2710 and a==4:self.ret(self.triggers[self.controllers.index(c)]);return
  if r==0xec5cd0:self.angular[a]=self.vec(b);self.ret()
  elif r==ex['lobby_update_trampoline']:self.ret()
  elif r==0x314470:self.ret(self.menu_down)
  elif r in (0x318350,0x3183d0):
   assert a==self.menu;self.selector_visible=r==0x3183d0;self.ret()
  else:super().hook(u,addr,size,user)
 def update(self,hand,down):
  self.grab=down;self.triggers[self.u.mem_read(hand+0x24,1)[0]]=down;self.call('lobby_hand_update_hook',hand)

manifest=json.loads((R/'analysis/native-patch-manifest.json').read_text())
assert manifest['network_version']=='Cloudcourt-2v2-v24 / Cloudcourt-4v4-v24'
patches={x['name']:x for x in manifest['patches']}
for name in ('lobby_hand_update','lobby_update','lobby_jump_area'):
 item=patches[name];raw=p.get_data(item['rva'],5)
 assert raw[0]==(0xe8 if item.get('kind')=='call' else 0xe9)
 assert item['rva']+5+struct.unpack('<i',raw[1:])[0]==item['hook']==ex[name+'_hook']
cases=[]
for base in (0x180000000,0x190000000):
 for fmt in (2,4):
  e=IntegratedLobbyEngine(base);e.flag('online_format',fmt)
  left=e.hand(0);right=e.hand(1);e.time+=1
  e.update(left,True);ball=e.q(left+0x30);assert e.spawned==[ball] and ball and e.q(ball+0xd8)==left
  rb=e.alloc();e.ptr(ball+0x98,rb);e.ptr(ball+0x30,rb);e.rb_velocity[rb]=(3,4,5)
  e.update(right,True);assert e.q(right+0x30)==ball and not e.q(left+0x30)
  for _ in range(6):e.update(left,True);e.update(right,True)
  assert e.q(right+0x30)==ball and not e.q(left+0x30) and len(e.spawned)==1
  for i in range(20):
   hand=left if i%2 else right;e.update(hand,False);e.update(hand,True)
   assert e.q(hand+0x30)==ball and e.q(ball+0xd8)==hand
  assert e.spawned==[ball] and e.rb_velocity[rb]==e.angular[rb]==(0.,0.,0.)
  # Existing button dispatch must reach the selector actions in the integrated
  # DLL, and menu input must reopen without disabling the practice controller.
  button=e.alloc();e.names[button]='CC_LobbyClose';e.call('button_press_hook',button)
  assert not e.selector_visible and e.call('lobby_move_enabled_hook')==1
  e.names[button]='PuloTeams';selected=e.selected.copy();e.call('button_press_hook',button)
  assert e.selector_visible and e.selected==selected,'lobby Change Team must open the selector, not send an in-match swap'
  e.names[button]='CC_LobbyClose';e.call('button_press_hook',button);e.menu_down=True;e.call('lobby_update_hook',e.page)
  assert e.selector_visible and e.call('lobby_jump_area_hook',0,0)==1
  e.call('player_speed_hook');speed=struct.unpack('<f',struct.pack('<I',e.u.reg_read(UC_X86_REG_XMM0)&0xffffffff))[0];assert abs(speed-2.4)<1e-5
  e.call('lobby_start_hook',e.page);assert e.destroyed==[ball] and not e.call('lobby_move_enabled_hook')
  cases.append([hex(base),fmt])
report=dict(passed=True,actual_integrated_dll=True,sha256=hashlib.sha256((R/'working/GameAssembly.dll').read_bytes()).hexdigest(),cases=cases,checks=['manifest call/jump targets verified','native Hand.Update trampoline attachment','one owned ball after20 alternating recalls','held transfer and no old-hand regrab','both physics velocities cleared','actual button dispatch closes and Change Team reopens','controller menu reopens','same match movement speed','jump gate only enabled in practice','owned-ball cleanup'],scope='Integrated x64 native code with deterministic Unity/Photon API stubs; no physical headset or real two-PC claim.')
(R/'analysis/v21-lobby-integrated-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
