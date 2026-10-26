"""Stage explicit v23 sources and authored previews; exclude game assets/binaries."""
from pathlib import Path
import hashlib, json, shutil

R = Path(__file__).resolve().parent
D = R.parent/'Caioba-github'
SOURCES = '''input_v19.c build_patch.py Apply-Complete-Mod.ps1 test_input_v19.py
test_celebration_v15.py backup_v23.py build_hands_v23.py build_cloudcourt_v23.py
test_hands_assets_v23.py preview_hands_v23.py preview_hands_bot_v23.py
test_pause_audio_v23.py probe_pause_audio_v23.py package_cloudcourt_v23.py
finish_cloudcourt_v23.py stage_cloudcourt_v23.py CHECKPOINT-V23.md'''.split()
REPORTS = '''v23-hands-assets-tests.json v23-pause-audio-native-tests.json
v23-pause-audio-comparison.json v23-regression.json v23-release-summary.json'''.split()
ART = {'analysis/v23-hands-preview.png':'assets/v23/hands-preview.png',
       'analysis/v23-hands-comparison.png':'assets/v23/hands-comparison.png'}

def main():
    entries, binary = [], []
    for name in SOURCES:
        path = R/name
        dest = D/name
        dest.parent.mkdir(exist_ok=True, parents=True)
        shutil.copyfile(path, dest)
        entries.append(dict(path=name, mode='100644', type='blob',
                            content=path.read_text(encoding='utf-8-sig')))
    for name in REPORTS:
        content = (R/'analysis'/name).read_text(encoding='utf-8-sig')
        target = 'validation/cloudcourt-v23/'+name
        dest = D/target
        dest.parent.mkdir(exist_ok=True, parents=True)
        dest.write_text(content, encoding='utf-8')
        entries.append(dict(path=target, mode='100644', type='blob', content=content))
    readme = (D/'README.md').read_text(encoding='utf-8')
    start = readme.index('Current checkpoint:')
    end = readme.index('\n', start)
    readme = readme[:start] + ('Current checkpoint: **Cloudcourt-v23-maos-audio**. '
        '[Release notes](CHECKPOINT-V23.md). Rounded, consistent default, setting and thumbs-up hands; '
        'default thickness reduced by 10%. UI click feedback survives a paused audio listener without '
        'resuming gameplay audio. Retains v22 room compatibility and physics. Quest 3 and real two-PC '
        'playtests remain pending.') + readme[end:]
    (D/'README.md').write_text(readme, encoding='utf-8')
    entries.append(dict(path='README.md', mode='100644', type='blob', content=readme))
    for source, target in ART.items():
        path = R/source
        dest = D/target
        dest.parent.mkdir(exist_ok=True, parents=True)
        shutil.copyfile(path, dest)
        data = path.read_bytes()
        binary.append(dict(path=target, source=source, bytes=len(data),
            git_blob_sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()))
    (R/'analysis/v23-publish-text.json').write_text(json.dumps(entries, ensure_ascii=False), encoding='utf-8')
    (R/'analysis/v23-publish-binary.json').write_text(json.dumps(binary, indent=2))
    groups, group, size = [], [], 0
    for row in entries:
        n = len(json.dumps(row).encode())
        if group and size+n > 30000:
            groups.append(group)
            group, size = [], 0
        group.append(row)
        size += n
    if group:
        groups.append(group)
    for i, group in enumerate(groups):
        (R/'analysis'/f'v23-publish-group-{i}.json').write_text(json.dumps(group, ensure_ascii=True), encoding='ascii')
    print(json.dumps(dict(text_entries=len(entries), own_previews=len(binary), groups=len(groups), scoped=True)))

if __name__ == '__main__':
    main()
