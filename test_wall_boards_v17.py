"""Scoreboard visibility, lookup paths, typefaces and preserved scene objects."""
from pathlib import Path
import argparse
import json
import struct
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import UnityPy
from fix_gloves_v16 import hierarchy
from fix_wall_boards_v17 import repair_wall_boards


def validate(file):
    objects, transforms, paths = hierarchy(file)
    rows = []
    font = UnityPy.load(str(R / 'working/VolleyballFever_Data/sharedassets0.assets')).file.objects[188].read_typetree()
    assert font['m_Name'] == 'Cloudcourt Bubble' and len(font['m_FontData']) > 10000
    def active(i):
        t = transforms[i]
        parent = t['m_Father']['m_PathID']
        return objects[t['m_GameObject']['m_PathID']]['m_IsActive'] and (active(parent) if parent in transforms else True)
    for index in range(2):
        root = f'CloudBoard{index}'
        group = objects[transforms[paths[root + '/CanvasGroup']]['m_GameObject']['m_PathID']]
        group_component = next(file.objects[c['component']['m_PathID']] for c in group['m_Component']
                               if file.objects[c['component']['m_PathID']].type.name == 'CanvasGroup')
        data = group_component.read_typetree()
        assert data['m_Enabled'] and data['m_Alpha'] == 1
        assert not data['m_Interactable'] and not data['m_BlocksRaycasts']
        for name, expected_size in [('Score', 76), ('Text', 28)]:
            path = root + '/CanvasGroup/' + name
            assert active(paths[path]), f'GameObject.Find cannot find inactive label: {path}'
            t = transforms[paths[path]]
            assert t['m_AnchorMin'] == t['m_AnchorMax'] == dict(x=.5, y=.5)
            assert t['m_SizeDelta']['x'] >= 620 and t['m_SizeDelta']['y'] >= 60
            g = objects[t['m_GameObject']['m_PathID']]
            text = next(file.objects[c['component']['m_PathID']] for c in g['m_Component']
                        if file.objects[c['component']['m_PathID']].type.name == 'MonoBehaviour')
            raw = text.get_raw_data()
            assert struct.unpack_from('<q', raw, 20)[0] == 572 and raw[12]
            assert not raw[60], 'A wall score label must not intercept the menu laser.'
            file_id, path_id = struct.unpack_from('<iq', raw, 72)
            assert file.externals[file_id-1].path.endswith('sharedassets0.assets') and path_id == 188
            assert struct.unpack_from('<i', raw, 84)[0] == expected_size
            assert struct.unpack_from('<f', raw, 56)[0] > .95
            rows.append(path)
        for name in ('Set', 'TextMeshPro Text', 'TextMeshPro Text (1)', 'TextMeshPro Text (2)'):
            assert not active(paths[root + '/CanvasGroup/' + name]), 'Retired clone labels must stay hidden.'
    return {'passed': True, 'active_score_paths': rows,
            'checks': ['score lookup paths active through all parents', 'opaque canvas groups',
                       'authored Cloudcourt font dependency', 'centered fixed-size label rects',
                       'decorative labels do not raycast', 'retired score/TMP labels remain hidden'],
            'scope': 'Serialized visibility and lookup contract; headset rendering still needs visual confirmation.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--asset', type=Path)
    args = parser.parse_args()
    if args.asset:
        file = UnityPy.load(str(args.asset)).file
        report = validate(file)
    else:
        source = R / 'working/VolleyballFever_Data/level3'
        before = UnityPy.load(str(source)).file
        file = UnityPy.load(str(source)).file
        change = repair_wall_boards(file)
        output = R / 'analysis/wall-boards-repaired-level3'
        output.write_bytes(file.save())
        file = UnityPy.load(str(output)).file
        report = validate(file)
        allowed = set(change['changed_object_ids'])
        assert set(file.objects) == set(before.objects)
        assert all(o.get_raw_data() == file.objects[i].get_raw_data() for i, o in before.objects.items() if i not in allowed)
        original = {i: o.get_raw_data() for i, o in file.objects.items()}
        repair_wall_boards(file)
        output.write_bytes(file.save())
        repeated = UnityPy.load(str(output)).file
        assert original == {i: o.get_raw_data() for i, o in repeated.objects.items()}
        report.update(change, unrelated_scene_objects_unchanged=True, idempotent=True)
    (R / 'analysis/v17-wall-board-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
