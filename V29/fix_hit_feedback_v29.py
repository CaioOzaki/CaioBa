"""Patch only accepted local-contact haptic dispatches; caller owns its binary."""
import struct
HIT_CALLS_V29=[
 ('accepted_hit_haptic_left_v29',0xeed321,0xa3800,'hit_haptic_dispatch_v29'),
 ('accepted_hit_haptic_right_v29',0xeed386,0xa3800,'hit_haptic_dispatch_v29'),
]
def patch_hit_calls_v29(result,p,patches,exports,delta):
 for name,site,target,hookname in HIT_CALLS_V29:
  before=p.get_data(site,5)
  assert before==b'\xe8'+struct.pack('<i',target-site-5),(name,'unexpected original call')
  hook=exports[hookname]+delta;offset=p.get_offset_from_rva(site)
  result[offset:offset+5]=b'\xe8'+struct.pack('<i',hook-site-5)
  patches.append(dict(name=name,rva=site,length=5,original=before.hex(),hook=hook,kind='call'))
