"""Publish only this explicit source, validation and own-art allowlist."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent;D=R.parent/'Caioba-github'
SOURCES=['mode_2v2.c','online_2v2.c','comfort_v14.c','identity_v16.c','celebration_v15.c',
 'build_patch.py','Apply-Complete-Mod.ps1','build_customization_art_v19.py',
 'test_customization_art_v19.py','test_online_2v2.py','bots_v20.c','landing_v20.c',
 'score_outline_v20.c','fix_bot_v20.py','build_bots_v20.py','build_customization_fix_v20.py',
 'build_landing_v20.py','build_scene_v20.py','build_cloudcourt_v20.py',
 'test_bots_assets_v20.py','test_bots_native_v20.py','test_customization_v20.py',
 'test_skin_cache_v20.py','test_landing_v20.py','test_scene_v20.py','test_score_outline_v20.py',
 'probe_customization_v20.py','audit_assets_v20.py','run_validation_v20.py',
 'package_cloudcourt_v20.py','finish_v20.py','record_publication_v20.py','stage_v20.py',
 'backup_v20.py','CHECKPOINT-V20.md','SCENE-V20.md']
TEXT=['assets/customization-v19/README.md']+['assets/bots-v20/'+n for n in ['README.md','catalog.json','unity-bindings.json']]
BINARY=[p.relative_to(R).as_posix() for p in sorted((R/'assets/bots-v20').glob('*.png'))]
REPORTS=['v20-regressions.json','v20-final-assets-audit.json','v20-customization-findings.json',
 'v20-customization-regression.json','v20-skin-cache-regression.json','v20-bot-assets-validation.json',
 'v20-bot-native-validation.json','v20-score-outline-tests.json','v20-scene-tests.json',
 'v20-landing-tests.json','v20-release-summary.json']
entries=[]
for name in SOURCES+TEXT:
 dest=D/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,dest)
 entries.append(dict(path=name,mode='100644',type='blob',content=dest.read_text(encoding='utf-8-sig')))
for name in BINARY:
 dest=D/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,dest)
for name in REPORTS:
 src=R/'analysis'/name;target='validation/cloudcourt-v20/'+name
 dest=D/target;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
 entries.append(dict(path=target,mode='100644',type='blob',content=dest.read_text(encoding='utf-8-sig')))
readme='''# Cloudcourt VR — v20

Current checkpoint: **Cloudcourt-v20-personagens-menu**. [Release notes](CHECKPOINT-V20.md).

- Fixed invisible customization previews: v19 BC7 compression corrupted alpha, especially in mipmaps. BC3 makes every mip opaque at the same 6 MB texture budget. Actual Unity desktop camera captures confirmed the before/after change. Avatar material binding now retries delayed and replaced materials; a native regression reproduces the old failure.
- Nine own cartoon bots, including the requested curtain bangs/blonde streak/septum character and the tall, slim young man with square glasses and dark blue jeans. Continuous hair coverage and curved strands replace the old hair geometry. The host picks without repetition and sends the chosen existing database index through the original assignment RPC. [Bot gallery and own art](assets/bots-v20/README.md).
- Character texture data reduced from 151 MB RGB24 to 33.6 MB opaque BC1 with verified mipmaps. Rig, IK and gameplay colliders preserved.
- Black score outlines, reordered Settings, and gym banners moved clear of structural beams (12 previous bound intersections reduced to zero).
- Floor points leave a green/red ring at the actual collision contact. The existing reliable EndRally RPC carries the mark and contact position to all peers. It clears at the next rally and has no collider or scoring effect.

All friends need **v20**, the same region and format. Room namespaces: **Cloudcourt-2v2-v20 / Cloudcourt-4v4-v20**. Earlier approved physics, assisted sets, 2v2/4v4, lobby and appearance options remain.

Build on a compatible local v19 working copy: compile `spin_mod.c`, run `build_patch.py`, then `build_cloudcourt_v20.py`. These apply narrow upgrades in place. Do not reconstruct old v16 assets over the current version. `package_cloudcourt_v20.py` builds/tests a reversible 17-file installer for the compatible original Steam build 9216628 or v19. Earlier ZIPs remain local.

`run_validation_v20.py` covers 27 native suites. `audit_assets_v20.py` compares the final assets with the v19 backup, including whitelist, colliders, alpha and geometry checks. The Unity preview probe restores PlayerPrefs and runs only in its disposable copy. The final package also passed reversible installer checks and controlled menu/Indoor/Beach startup. These checks do not establish live avatar appearance in Quest 3 or real two-PC multiplayer; those playtests remain pending.

Own compatible base game required. This repository includes mod sources, own art and previously included CC0 audio with its licenses. Game DLLs, extracted original assets, backups and distribution ZIPs are not published. A clean clone requires compatible local assets, backups and tools before it can build. The cleaned branch still excludes abandoned experimental files.

Earlier release: [v19](CHECKPOINT-V19.md). [Audio credits](assets/audio-v18/CREDITS.md).
'''
(D/'README.md').write_text(readme,encoding='utf-8');entries.append(dict(path='README.md',mode='100644',type='blob',content=readme))
assert len({e['path'] for e in entries})==len(entries)
assert all(not e['path'].lower().endswith(('.dll','.assets','.resource','.ress','.bin','.zip')) for e in entries)
(R/'analysis/v20-publish-text.json').write_text(json.dumps(entries,ensure_ascii=False),encoding='utf-8')
binary=[]
for name in BINARY:
 data=(R/name).read_bytes();binary.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
 git_blob_sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()))
(R/'analysis/v20-publish-binary.json').write_text(json.dumps(binary,indent=2),encoding='utf-8')
print(json.dumps({'text_entries':len(entries),'own_pngs':len(BINARY),'binary_bytes':sum(x['bytes'] for x in binary)}))
