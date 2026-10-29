"""Redirect only SpawnBot's character-index boxing, not its other Int32 fields."""
import struct


def patch_bot_identity_v20(result, original_pe, patches, exports, delta):
    site,target=0x25513d,0x14ba70
    before=b'\xe8'+struct.pack('<i',target-site-5)
    assert original_pe.get_data(site,5)==before,'SpawnBot character-index call changed.'
    hook=exports['bot_character_box_hook']+delta
    offset=original_pe.get_offset_from_rva(site)
    result[offset:offset+5]=b'\xe8'+struct.pack('<i',hook-site-5)
    patches.append(dict(name='bot_unique_character',rva=site,length=5,original=before.hex(),hook=hook,kind='call'))
