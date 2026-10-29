"""Verified integration entries for gameplay_v19.c; no file mutation here.

build_patch.py may import gameplay_v19_entries and V19_CALLS, appending the former
to its entry list and the latter to its normal call-site patches. Include
gameplay_v19.c after the existing mode modules when compiling spin_mod.c.
All offsets apply only to build 9216628.
"""
from pathlib import Path
import json, struct, sys

V19_ENTRIES = [('bot_update', 0x271BE0)]
V19_CALLS = [('indoor_beach_points_blue', 0x2586C6, 0xEF34B0, 'points_per_set_hook'),
             ('indoor_beach_points_red', 0x258711, 0xEF34B0, 'points_per_set_hook'),
             ('best_of_three_blue', 0x2589CA, 0xEF3530, 'sets_to_win_hook'),
             ('best_of_three_red', 0x2589F6, 0xEF3530, 'sets_to_win_hook')]

def gameplay_v19_entries(original_pe):
    # Confirm the inline jump and the settings reads in the actual rally code.
    assert original_pe.get_data(0x271EBB, 8) == bytes.fromhex('f30f11b798000000')
    for site, target in ((0x2586C6, 0xEF34B0), (0x258711, 0xEF34B0),
                         (0x2589CA, 0xEF3530), (0x2589F6, 0xEF3530)):
        assert original_pe.get_data(site, 5) == b'\xe8' + struct.pack('<i', target-site-5)
    return V19_ENTRIES.copy()

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root/'tools/python'))
    import pefile
    entries = gameplay_v19_entries(pefile.PE(str(root/'backup/GameAssembly.dll')))
    report = {'entries': [(name, hex(rva)) for name, rva in entries],
              'callsite_patches': [(name, hex(site), hex(target), hook) for name, site, target, hook in V19_CALLS],
              'include': 'gameplay_v19.c after lobby_v18.c',
              'best_of_three': '2 set wins; original requires a two-point lead',
              'points': {'Indoor': 25, 'Beach': 21},
              'real_bot_update': 'covers the inline jump, unlike the old Jump-only hook',
              'setting_arc_and_target_changed': False}
    (root/'analysis/v19-gameplay-integration.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
