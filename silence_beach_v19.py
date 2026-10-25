"""Silence only the beach sea/bird ambient AudioSources, preserving all else."""
from pathlib import Path
import argparse, hashlib, json, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import UnityPy

TARGETS = {'level1': (230, 231), 'level2': (256,)}


def silence(file, ids):
    changed = []
    for ident in ids:
        obj = file.objects[ident]
        assert obj.type.name == 'AudioSource'
        d = obj.read_typetree()
        name = file.objects[d['m_GameObject']['m_PathID']].read_typetree()['m_Name']
        assert any(key in name.lower() for key in ('beach', 'seagull')), name
        d.update(m_Enabled=0, m_PlayOnAwake=False, m_Volume=0., Mute=True)
        obj.save_typetree(d)
        changed.append({'object': ident, 'name': name})
    return changed


def build(source, output):
    output.mkdir(parents=True, exist_ok=True)
    report = {'scenes': [], 'changes_only': ['m_Enabled', 'm_PlayOnAwake', 'm_Volume', 'Mute']}
    for name, ids in TARGETS.items():
        original = (source / name).read_bytes()
        sha = hashlib.sha256(original).hexdigest()
        backup = output / (name + '-before-silence-' + sha[:16] + '.backup')
        if not backup.exists():
            backup.write_bytes(original)
        file = UnityPy.load(original).file
        changes = silence(file, ids)
        (output / name).write_bytes(file.save())
        report['scenes'].append({'name': name, 'sources': changes, 'backup': str(backup)})
    (output / 'silence-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=R / 'working/VolleyballFever_Data')
    parser.add_argument('--output', type=Path, default=R / 'visuals-v19-silent-beach')
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.output), indent=2))
