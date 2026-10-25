"""Check that only three ambient sources change; all scene objects survive."""
from pathlib import Path
import argparse, json, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import UnityPy
from silence_beach_v19 import TARGETS, silence


def validate(source, output):
    records = []
    changed_fields = {'m_Enabled', 'm_PlayOnAwake', 'm_Volume', 'Mute'}
    for name, ids in TARGETS.items():
        before = UnityPy.load(str(source / name)).file
        after = UnityPy.load(str(output / name)).file
        assert set(before.objects) == set(after.objects)
        for ident, obj in before.objects.items():
            if ident not in ids:
                assert obj.get_raw_data() == after.objects[ident].get_raw_data(), (name, ident)
                continue
            old, new = obj.read_typetree(), after.objects[ident].read_typetree()
            assert new['m_Enabled'] == 0 and not new['m_PlayOnAwake']
            assert new['m_Volume'] == 0 and new['Mute']
            assert {k: v for k, v in old.items() if k not in changed_fields} == {
                    k: v for k, v in new.items() if k not in changed_fields}
        silence(after, ids)
        assert after.save() == (output / name).read_bytes()
        records.append({'scene': name, 'only_changed_objects': list(ids), 'objects_preserved': len(before.objects)})
    result = {'passed': True, 'idempotent': True, 'scenes': records,
              'all_non_ambient_audio_and_scene_objects_unchanged': True, 'VR_tested': False}
    (R / 'analysis/v19-beach-silence-validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=R / 'versions/cloudcourt-v18-antes-v19')
    ap.add_argument('--output', type=Path, default=R / 'visuals-v19-silent-beach')
    args = ap.parse_args()
    print(json.dumps(validate(args.source, args.output), indent=2))
