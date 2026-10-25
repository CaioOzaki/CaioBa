"""Explicit source and own-art allowlist. Never stage extracted game assets."""
from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parent;D=R.parent/'Caioba-github'
SOURCES=['mode_2v2.c','formation_serve.c','online_2v2.c','comfort_v14.c','identity_v16.c',
 'customization_v19.c','input_v19.c','map_v19.c','gameplay_v19.c','build_patch.py',
 'fix_gameplay_v19.py','fix_map_v19.py','build_cloudcourt_v19.py',
 'build_customization_art_v19.py','build_menu_v19.py','silence_beach_v19.py',
 'audit_assets_v19.py','test_2v2.py','test_online_2v2.py','test_comfort_v14.py',
 'test_cloudcourt_v16.py','test_identity_rpc_v16.py','test_customization_v19.py',
 'test_customization_art_v19.py','test_input_v19.py','test_input_v19_harness.c',
 'test_map_v19.py','test_gameplay_v19.py','test_bot_contact_v19.py','test_menu_v19.py',
 'test_silence_beach_v19.py','run_validation_v19.py','package_cloudcourt_v19.py',
 'finish_v19.py','record_publication_v19.py','stage_v19.py','Apply-Complete-Mod.ps1','CHECKPOINT-V19.md']
TEXT=['assets/customization-v19/'+n for n in ['README.md','catalog.json','unity-bindings.json']]
BINARY=[p.relative_to(R).as_posix() for p in sorted((R/'assets/customization-v19').glob('*.png'))]
REPORTS=['v19-regressions.json','v19-gameplay-tests.json','v19-bot-contact-tests.json',
 'v19-customization-runtime-tests.json','v19-avatar-art-validation.json','v19-menu-validation.json',
 'v19-input-validation.json','v19-map-validation.json','v19-beach-silence-validation.json',
 'v19-final-assets-tests.json','v19-release-summary.json']
entries=[]
for name in SOURCES+TEXT:
 src=R/name;dest=D/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
 entries.append({'path':name,'mode':'100644','type':'blob','content':dest.read_text(encoding='utf-8-sig')})
for name in BINARY:
 dest=D/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,dest)
for name in REPORTS:
 src=R/'analysis'/name;target='validation/cloudcourt-v19/'+name
 dest=D/target;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
 entries.append({'path':target,'mode':'100644','type':'blob','content':dest.read_text(encoding='utf-8-sig')})
readme='''# Cloudcourt VR — v19

Current checkpoint: **Cloudcourt-v19-customizacao**. [Changes and validation](CHECKPOINT-V19.md).

- Bots jump through the real inlined Update path, reaching a 2m apex and timing attacks for descending sets. The approved player set trajectory and target remain unchanged.
- Nine independent emoji faces and nine outfits, giving 81 combinations. Customize from the main menu or pause overlay; preferences persist and online peers receive each player's choice. [PNG previews and catalog](assets/customization-v19/README.md).
- Quest A and both digital/analog triggers feed the same menu submit state. Valid button clicks play a cached 2D sound. Clicking UI in the lobby does not request a practice ball.
- Beach sea/bird AudioSources disabled. Indoor and Beach are the available courts. The host chooses the online map before creating the room and all peers follow its Photon room property.
- Best of three sets with a two-point lead: Indoor25 / Beach21. Sets/points options and the night court are hidden.

Room namespaces: **Cloudcourt-2v2-v19 / Cloudcourt-4v4-v19**. All friends need v19, the same format and region. Earlier v18 beach, audio, lobby and gameplay fixes are preserved.

Build on a compatible local v18 working copy: compile `spin_mod.c`, run `build_patch.py`, then `build_cloudcourt_v19.py`. It applies only v19 UI/art/audio-source changes to existing assets. Do not run the old v16 assembly over this release. `package_cloudcourt_v19.py` builds and tests a reversible 17-file installer for the compatible original Steam build 9216628 or v18. Previous ZIPs remain local.

Validation: `run_validation_v19.py` covers 23 native suites, including original Bot.Update and scoring control flow. `audit_assets_v19.py`, `test_menu_v19.py`, `test_customization_art_v19.py` and `test_silence_beach_v19.py` cover the final serialized assets. Controlled menu/Indoor and Beach startup checks passed. Engine stubs, UV sampling and startup checks do not establish actual Quest 3 comfort/input or live two-PC behavior; those still need playtesting.

Own compatible base game required. This repository contains mod sources, own procedural artwork and previously included CC0 effects with their licenses. It does not contain game DLLs, extracted original meshes/textures/audio, backups or distribution ZIPs. A clean clone alone is not a complete game build; compatible local assets, backups and tool dependencies are required. The cleaned branch continues to exclude abandoned experimental files.

Visual identity: https://www.figma.com/design/1sIgjKcMItHmbLIu1dnch0?node-id=2-24

Earlier release: [v18](CHECKPOINT-V18.md). [Sound credits](assets/audio-v18/CREDITS.md).
'''
(D/'README.md').write_text(readme,encoding='utf-8')
entries.append({'path':'README.md','mode':'100644','type':'blob','content':readme})
assert all(not e['path'].lower().endswith(('.dll','.assets','.resource','.ress','.bin','.zip')) for e in entries)
(R/'analysis/v19-publish-text.json').write_text(json.dumps(entries,ensure_ascii=False),encoding='utf-8')
(R/'analysis/v19-publish-binary.json').write_text(json.dumps([{'path':name,
 'bytes':(R/name).stat().st_size,'sha256':hashlib.sha256((R/name).read_bytes()).hexdigest(),
 'git_blob_sha':hashlib.sha1(b'blob '+str((R/name).stat().st_size).encode()+b'\0'+(R/name).read_bytes()).hexdigest()}
 for name in BINARY],indent=2),encoding='utf-8')
print(json.dumps({'text_entries':len(entries),'own_pngs':len(BINARY),
 'binary_bytes':sum((R/name).stat().st_size for name in BINARY)}))
