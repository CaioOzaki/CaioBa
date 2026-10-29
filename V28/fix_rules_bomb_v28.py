"""Exact build9216628 hook integration. Root builder calls these explicitly."""
import struct
V28_ENTRIES=[('change_motion_v28',0x77e5c0),('solo_bomb_v28',0xef42e0),('bomb_ground_v28',0x2524c0),('bomb_team_a_v28',0x2540f0),('bomb_team_b_v28',0x2548d0)]
V28_CALLS=[('online_rules_prefab_v28',0x315658,0x60fb50,'online_rules_prefab_v28'),('online_ball_prefab_v28',0x3156b8,0x60fb50,'online_ball_prefab_v28')]
def patch_rules_bomb_v28(result,p,patches,exports,delta):
 # Go() inlines SetUpTeamBOffline after constructing the local team.
 # Its Bomb branch spawns only one opponent, even with the new four areas.
 site=0x253754;before=bytes.fromhex('0f85a8000000');assert p.get_data(site,6)==before
 offset=p.get_offset_from_rva(site);result[offset:offset+6]=b'\x90'*6
 patches.append(dict(name='bomb_full_roster_v28',rva=site,length=6,original=before.hex(),kind='branch_neutralized'))
 site=0x252430;before=bytes.fromhex('80797800741f4439417c750f')
 assert p.get_data(site,len(before))==before,'AllowedToHitBall build mismatch'
 target=exports['allowed_hit_v28_hook']+delta;offset=p.get_offset_from_rva(site)
 result[offset:offset+5]=b'\xe9'+struct.pack('<i',target-site-5)
 patches.append(dict(name='allowed_hit_v28',rva=site,length=5,original=before[:5].hex(),hook=target,kind='entry_replace'))
 for name,site,original,export in V28_CALLS:
  before=b'\xe8'+struct.pack('<i',original-site-5);assert p.get_data(site,5)==before,name
  target=exports[export]+delta;offset=p.get_offset_from_rva(site);result[offset:offset+5]=b'\xe8'+struct.pack('<i',target-site-5)
  patches.append(dict(name=name,rva=site,length=5,original=before.hex(),hook=target,kind='call'))
