"""Exact call-site integration for the independently tested map_v19.c module."""
import struct

MAP_CALLS_V19 = [
    ('room_map_property', 0x319857, 0x60b4c0, 'create_room_map_hook'),
    ('room_map_environment', 0x32a445, 0x251940, 'online_environment_map_hook'),
]


def patch_map_calls_v19(result, original_pe, patches, exports, delta):
    """Use from build_patch.py after section insertion, before saving its result.

    `exports` are RVAs from the helper DLL, before adding `delta`, matching the
    existing builder's export table. No function-entry trampoline is necessary.
    """
    for name, site, original_target, export in MAP_CALLS_V19:
        before = b'\xe8' + struct.pack('<i', original_target - site - 5)
        assert original_pe.get_data(site, 5) == before, (name, 'original build mismatch')
        assert export in exports, ('Missing native map module export', export)
        target = exports[export] + delta
        offset = original_pe.get_offset_from_rva(site)
        result[offset:offset+5] = b'\xe8' + struct.pack('<i', target-site-5)
        patches.append(dict(name=name, rva=site, length=5, original=before.hex(), hook=target, kind='call'))
