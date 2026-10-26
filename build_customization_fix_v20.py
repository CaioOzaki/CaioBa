"""Repair invisible v19 avatar previews by encoding opaque BC3 atlas mipmaps.

The v19 BC7 encoder returned valid RGB with near-zero alpha in most atlas cells
and all lower mipmaps. UI/Default blends alpha, so the RawImages disappeared.
This narrowly replaces two texture payloads; materials, UVs and UI stay intact.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import numpy as np
import texture2ddecoder
import UnityPy
from PIL import Image
from UnityPy.enums import TextureFormat

ATLASES = {1329: ('Cloudcourt v19 Faces 3x3', 'faces-atlas.png'),
           1330: ('Cloudcourt v19 Outfits 3x3', 'outfits-atlas.png')}


def mip_report(texture):
    """Inspect every serialized mip, not just UnityPy's base-image RGB output."""
    decoder = {int(TextureFormat.BC7): texture2ddecoder.decode_bc7,
               int(TextureFormat.DXT5): texture2ddecoder.decode_bc3}[texture.m_TextureFormat]
    offset = 0
    width, height = texture.m_Width, texture.m_Height
    result = []
    for level in range(texture.m_MipCount):
        length = ((width + 3) // 4) * ((height + 3) // 4) * 16
        payload = texture.image_data[offset:offset + length]
        assert len(payload) == length, (level, width, height, len(payload), length)
        rgba = np.frombuffer(decoder(payload, width, height), dtype=np.uint8).reshape(height, width, 4)
        alpha = rgba[:, :, 3]
        result.append(dict(level=level, width=width, height=height, bytes=length,
                           alpha_min=int(alpha.min()), alpha_mean=float(alpha.mean()),
                           alpha_max=int(alpha.max()), opaque_pixels=int((alpha == 255).sum()),
                           pixels=width * height))
        offset += length
        width //= 2
        height //= 2
    assert offset == len(texture.image_data), (offset, len(texture.image_data))
    return result


def apply_customization_fix(resources, art_dir=None):
    """Idempotent in-memory repair, safe after the other agents' asset builders."""
    art_dir = Path(art_dir or R / 'assets/customization-v19')
    report = {}
    for ident, (name, filename) in ATLASES.items():
        obj = resources.objects[ident]
        tex = obj.read()
        assert tex.m_Name == name and tex.m_Width == tex.m_Height == 1536
        assert tex.m_MipCount == 9 and tex.m_TextureFormat in (12, 25)
        before_format = tex.m_TextureFormat
        before = mip_report(tex)
        source = Image.open(art_dir / filename).convert('RGBA')
        assert source.size == (1536, 1536)
        assert np.all(np.asarray(source)[:, :, 3] == 255), 'Avatar artwork must be opaque.'
        # BC3 preserves this exact opaque alpha in all nine levels. Its GPU/data
        # size is identical to BC7 and the existing desktop VR runtime supports it.
        tex.set_image(source, target_format=TextureFormat.DXT5, mipmap_count=9)
        after = mip_report(tex)
        assert all(m['opaque_pixels'] == m['pixels'] for m in after), 'Non-opaque encoded atlas.'
        tex.save()
        report[str(ident)] = dict(name=name, format_before=before_format,
                                   format_after=int(TextureFormat.DXT5), mipmaps_before=before,
                                   mipmaps_after=after, bytes=len(tex.image_data))
    return {'changed_object_ids': list(ATLASES), 'atlases': report,
            'gpu_bytes_total': sum(x['bytes'] for x in report.values()),
            'unchanged': 'All geometry, materials, UVs, UI wiring and gameplay objects.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=R / 'versions/cloudcourt-v19-antes-v20/resources.assets')
    parser.add_argument('--output', type=Path, default=R / 'visuals-v20-ui/resources.assets')
    parser.add_argument('--art-dir', type=Path)
    args = parser.parse_args()
    assert args.input.resolve() != args.output.resolve(), 'Use a separate fixture output.'
    resources = UnityPy.load(str(args.input)).file
    before_hash = hashlib.sha256(args.input.read_bytes()).hexdigest()
    report = apply_customization_fix(resources, args.art_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(resources.save())
    report.update(input=str(args.input), input_sha256=before_hash, output=str(args.output),
                  output_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest())
    (R / 'analysis/v20-customization-alpha-repair.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'atlases'}, indent=2))


if __name__ == '__main__':
    main()
