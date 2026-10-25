"""Read-only final v19 asset comparison against the preserved v18 checkpoint."""
from pathlib import Path
import hashlib, json, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import UnityPy
from build_menu_v19 import build_menu, bind_v19_preview_assets


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changes(before, after):
    old, new = set(before.objects), set(after.objects)
    return {'added': sorted(new - old), 'removed': sorted(old - new),
            'modified': sorted(i for i in old & new
                               if before.objects[i].get_raw_data() != after.objects[i].get_raw_data()),
            'unchanged': sum(before.objects[i].get_raw_data() == after.objects[i].get_raw_data()
                             for i in old & new)}


def main():
    source, working = R / 'versions/cloudcourt-v18-antes-v19', R / 'working/VolleyballFever_Data'
    report = {'passed': False, 'working_assets_modified': False, 'VR_tested': False,
              'base': str(source), 'objects': {}, 'file_hashes': [], 'problems': []}
    try:
        for name in ('level0', 'resources.assets', 'level1', 'level2'):
            before = UnityPy.load(str(source / name)).file
            after = UnityPy.load(str(working / name)).file
            diff = changes(before, after)
            report['objects'][name] = diff
            assert not diff['removed'], (name, 'objects removed')
            if name == 'resources.assets':
                assert diff['modified'] == [67, 68, 902, 937]
                assert diff['added'] == [1329, 1330, 1331, 1332]
            elif name == 'level1':
                assert diff['modified'] == [230, 231] and not diff['added']
            elif name == 'level2':
                assert diff['modified'] == [256] and not diff['added']
            else:
                # Reconstruct the permitted UI delta entirely in memory, then
                # compare every actual object, not just selected button fields.
                expected = UnityPy.load(str(source / name)).file
                build_menu(expected)
                bind_v19_preview_assets(expected, R / 'assets/customization-v19/unity-bindings.json')
                expected = UnityPy.load(expected.save()).file
                assert set(expected.objects) == set(after.objects)
                mismatch = [i for i in expected.objects
                            if expected.objects[i].get_raw_data() != after.objects[i].get_raw_data()]
                assert not mismatch, ('level0 outside the exact UI builder delta', mismatch)
                assert [(e.path, e.type, e.guid) for e in expected.externals] == [
                    (e.path, e.type, e.guid) for e in after.externals]
                diff['matches_exact_menu_builder_delta'] = True
        changed_assets = {'level0', 'resources.assets', 'level1', 'level2'}
        original_files = sorted(p for p in source.iterdir() if p.is_file() and
                                (p.name.startswith('level') and p.name[5:].isdigit()
                                 or p.suffix in ('.assets', '.resource', '.dll')))
        for old in original_files:
            current = R / 'working/GameAssembly.dll' if old.name == 'GameAssembly.dll' else working / old.name
            record = {'name': old.name, 'v18_sha256': sha(old), 'working_sha256': sha(current)}
            record['same'] = record['v18_sha256'] == record['working_sha256']
            record['allowed_to_change'] = old.name in changed_assets or old.name == 'GameAssembly.dll'
            report['file_hashes'].append(record)
            assert record['same'] or record['allowed_to_change'], (old.name, 'unrelated file changed')
        report['suites'] = {name: json.loads((R / 'analysis' / file).read_text(encoding='utf-8'))
                            for name, file in [('menu', 'v19-menu-validation.json'),
                                               ('beach_silence', 'v19-beach-silence-validation.json'),
                                               ('avatar_art', 'v19-avatar-art-validation.json')]}
        assert all(suite['passed'] for suite in report['suites'].values())
        assert report['suites']['avatar_art']['unrelated_objects_unchanged']
        report['passed'] = True
        report['checks'] = ['Working level0 matches exact allowed UI builder delta',
                            'Working avatar changes restricted to UVs, two renderer pointers and four new art objects',
                            'Beach only three ambient AudioSources changed',
                            'Unrelated asset/resource files match v18 SHA256',
                            'Geometry, colliders, shaders and other scene objects preserved']
    except Exception as error:
        report['problems'].append(repr(error))
    path = R / 'analysis/v19-final-assets-tests.json'
    path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'suites'}, indent=2))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
