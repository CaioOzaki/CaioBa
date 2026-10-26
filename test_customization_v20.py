"""Regression for invisible v19 UI: real encoded alpha, all mipmaps, narrow edit."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import numpy as np
import UnityPy
from PIL import Image
from build_customization_fix_v20 import ATLASES, apply_customization_fix, mip_report


def opaque_atlas(texture):
    levels = mip_report(texture)
    assert len(levels) == 9
    assert all(x['opaque_pixels'] == x['pixels'] for x in levels), 'Encoded atlas contains transparent pixels.'
    return levels


def validate(asset, before_path):
    before = UnityPy.load(str(before_path)).file
    file = UnityPy.load(str(asset)).file
    assert set(file.objects) == set(before.objects), 'Unexpected added/deleted objects.'
    modified = [pid for pid, obj in before.objects.items()
                if obj.get_raw_data() != file.objects[pid].get_raw_data()]
    assert set(modified) == set(ATLASES), modified
    metrics = {}
    for ident, (_, filename) in ATLASES.items():
        old = before.objects[ident].read()
        old_rejected = False
        try:
            opaque_atlas(old)
        except AssertionError:
            old_rejected = True
        assert old_rejected, 'Regression fixture does not reproduce old invisible previews.'
        tex = file.objects[ident].read()
        levels = opaque_atlas(tex)
        assert tex.m_TextureFormat == 12 and len(tex.image_data) == len(old.image_data)
        tree = file.objects[ident].read_typetree()
        previous = before.objects[ident].read_typetree()
        # The existing texture metadata/bindings are correct. Only its bytes and
        # codec change; there is no reason to touch colors, geometry or the menu.
        changed_keys = {k for k in tree if tree[k] != previous[k]}
        assert changed_keys == {'image data', 'm_TextureFormat'}, changed_keys
        decoded = np.asarray(tex.image.convert('RGBA'))
        source = np.asarray(Image.open(R / 'assets/customization-v19' / filename).convert('RGBA'))
        assert np.all(decoded[:, :, 3] == 255)
        delta = np.abs(decoded[:, :, :3].astype(np.int16) - source[:, :, :3].astype(np.int16))
        assert delta.mean() < 3.5 and np.percentile(delta, 99) <= 10, (delta.mean(), np.percentile(delta, 99))
        # Source and serialized orientation must agree for all nine choices.
        cells = []
        for index in range(9):
            row, col = divmod(index, 3)
            tile = decoded[row * 512:(row + 1) * 512, col * 512:(col + 1) * 512]
            expected = source[row * 512:(row + 1) * 512, col * 512:(col + 1) * 512]
            assert np.abs(tile[:, :, :3].astype(np.int16) - expected[:, :, :3].astype(np.int16)).mean() < 4.5
            cells.append(hashlib.sha256(tile.tobytes()).hexdigest())
        assert len(set(cells)) == 9
        metrics[str(ident)] = dict(before_rejected=True, mips=levels, bytes=len(tex.image_data),
                                  rgb_mean_error=float(delta.mean()), rgb_p99=float(np.percentile(delta, 99)),
                                  all_nine_choices_present=True)
    snapshot = {pid: obj.get_raw_data() for pid, obj in file.objects.items()}
    apply_customization_fix(file)
    assert all(obj.get_raw_data() == snapshot[pid] for pid, obj in file.objects.items()), 'Repair is not idempotent.'
    return dict(passed=True, old_v19_rejected=True, new_all_mips_opaque=True,
                idempotent=True, modified_ids=modified, other_objects_byte_identical=True,
                gpu_bytes_unchanged=True, atlases=metrics,
                scope='Serialized RGBA payload and structure. Unity render screenshots are separate evidence.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--asset', type=Path, default=R / 'visuals-v20-ui/resources.assets')
    parser.add_argument('--before', type=Path, default=R / 'versions/cloudcourt-v19-antes-v20/resources.assets')
    args = parser.parse_args()
    result = validate(args.asset, args.before)
    (R / 'analysis/v20-customization-regression.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'atlases'}, indent=2))
