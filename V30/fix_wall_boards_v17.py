"""Activate the authored gym score labels so runtime score lookup can find them."""
from pathlib import Path
import struct
from fix_gloves_v16 import hierarchy


def repair_wall_boards(scene):
    """Repair two scene scoreboards in memory; caller saves the Unity file."""
    objects, transforms, paths = hierarchy(scene)
    font_files = [i for i, entry in enumerate(scene.externals, 1)
                  if entry.path.replace('\\', '/').rsplit('/', 1)[-1].lower() == 'sharedassets0.assets']
    assert len(font_files) == 1, 'The shared Cloudcourt font must be an external scene dependency.'
    font_file = font_files[0]
    changed, labels = set(), []
    for index in range(2):
        root = f'CloudBoard{index}'
        for path in (root, root + '/CanvasGroup', root + '/CanvasGroup/Score', root + '/CanvasGroup/Text'):
            transform = transforms[paths[path]]
            gid = transform['m_GameObject']['m_PathID']
            go = objects[gid]
            go['m_IsActive'] = True
            scene.objects[gid].save_typetree(go)
            changed.add(gid)
            for c in go['m_Component']:
                obj = scene.objects[c['component']['m_PathID']]
                if obj.type.name == 'CanvasGroup':
                    data = obj.read_typetree()
                    data.update(m_Enabled=1, m_Alpha=1., m_Interactable=False, m_BlocksRaycasts=False)
                    obj.save_typetree(data)
                    changed.add(obj.path_id)
                elif path.endswith(('/Score', '/Text')) and obj.type.name == 'MonoBehaviour':
                    raw = bytearray(obj.get_raw_data())
                    if len(raw) < 132 or struct.unpack_from('<q', raw, 20)[0] != 572:
                        continue
                    raw[12] = 1  # Behaviour.m_Enabled
                    raw[60] = 0  # Decorative Graphic.m_RaycastTarget
                    struct.pack_into('<iq', raw, 72, font_file, 188)
                    obj.set_raw_data(bytes(raw))
                    changed.add(obj.path_id)
                    labels.append(dict(path=path, go_id=gid, text_id=obj.path_id))
    assert len(labels) == 4
    return {'labels': labels, 'font': dict(file_id=font_file, path_id=188),
            'changed_object_ids': sorted(changed),
            'reason': 'Inherited inactive UI.Text objects cannot be found by GameObject.Find or render.'}


if __name__ == '__main__':
    import argparse
    import json
    import sys
    R = Path(__file__).resolve().parent
    sys.path.insert(0, str(R / 'tools/python'))
    import UnityPy
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    assert args.input.resolve() != args.output.resolve(), 'Write to a separate output.'
    file = UnityPy.load(str(args.input)).file
    report = repair_wall_boards(file)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(file.save())
    print(json.dumps(report, indent=2))
