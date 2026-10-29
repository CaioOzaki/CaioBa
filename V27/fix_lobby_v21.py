"""Narrow native v21 lobby integrations; caller owns the output binary."""
import struct

LOBBY_ENTRIES_V21=[('lobby_hand_update',0x312f60),('lobby_update',0x315d40)]
LOBBY_CALLS_V21=[('lobby_jump_area',0x31c2cf,0xa0c080,'lobby_jump_area_hook')]

def patch_lobby_calls_v21(result,p,patches,exports,delta):
 for name,site,target,hookname in LOBBY_CALLS_V21:
  before=p.get_data(site,5);assert before==b'\xe8'+struct.pack('<i',target-site-5)
  hook=exports[hookname]+delta;offset=p.get_offset_from_rva(site)
  result[offset:offset+5]=b'\xe8'+struct.pack('<i',hook-site-5)
  patches.append(dict(name=name,rva=site,length=5,original=before.hex(),hook=hook,kind='call'))
