"""Stage only reviewed sources, summaries and original v21 preview artwork."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent;D=R.parent/'Caioba-github'
SOURCES='''mode_2v2.c formation_serve.c comfort_v14.c online_2v2.c celebration_v15.c
score_outline_v20.c identity_v16.c customization_v19.c lobby_v18.c avatar_style_v21.c
hand_visuals_v21.c serve_feedback_v21.c build_patch.py build_cloudcourt_v21.py
build_environment_v21.py build_bot_appearance_v21.py build_avatar_v21.py build_lobby_v21.py
build_english_v21.py fix_lobby_v21.py test_formation_serve.py test_online_2v2.py
test_cloudcourt_v16.py test_identity_rpc_v16.py test_celebration_v15.py test_score_outline_v20.py
test_avatar_v21.py test_customization_v19.py test_landing_v20.py test_serve_feedback_v21.py
test_lobby_v21.py test_lobby_assets_v21.py test_lobby_integrated_v21.py
test_bot_celebration_integrated_v21.py test_hand_visuals_integrated_v21.py
test_environment_v21.py test_english_v21.py test_integration_v21.py preview_environment_v21.py
package_cloudcourt_v21.py backup_v21.py finish_cloudcourt_v21.py stage_cloudcourt_v21.py
Apply-Complete-Mod.ps1 CHECKPOINT-V21.md assets/audio-v21/CREDITS.md'''.split()
REPORTS='''v21-regression-final.json v21-integration-assets.json v21-avatar-tests.json
v21-english-validation.json v21-lobby-tests.json v21-lobby-assets-tests.json
v21-lobby-integrated-tests.json v21-score-outline-tests.json v21-serve-feedback-tests.json
v21-bot-celebration-integrated-tests.json v21-hand-visuals-integrated-tests.json
v20-landing-tests.json v21-release-summary.json'''.split()
ART={
 'visuals-v21-environment/orla-geometry-preview.png':'assets/v21/orla-geometry-preview.png',
 'visuals-v21-environment/arena-section-preview.png':'assets/v21/arena-section-preview.png',
 'visuals-v21-environment/bots-appearance-preview.png':'assets/v21/bots-appearance-preview.png',
 'visuals-v21-environment/yellow-blue-ball-atlas.png':'assets/v21/yellow-blue-ball-atlas.png',
 'visuals-v21-avatar/hands-and-tones.png':'assets/v21/hands-and-tones.png'}

def main():
    entries=[];binary=[]
    for name in SOURCES:
        p=R/name;assert p.is_file(),name
        dest=D/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        entries.append(dict(path=name,mode='100644',type='blob',content=p.read_text(encoding='utf-8-sig')))
    for name in REPORTS:
        p=R/'analysis'/name;assert p.is_file(),name
        content=p.read_text();target='validation/cloudcourt-v21/'+name
        dest=D/target;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(content,encoding='utf-8')
        entries.append(dict(path=target,mode='100644',type='blob',content=content))
    readme=(D/'README.md').read_text(encoding='utf-8')
    begin=readme.index('Current checkpoint:');end=readme.index('\n',begin)
    readme=readme[:begin]+'Current checkpoint: **Cloudcourt-v21-orla-gestos**. [Release notes](CHECKPOINT-V21.md). Immediate customization previews, six hand tones, setting/thumbs-up gestures, own-team bot celebrations, original serve whistle, one-ball online practice, and the urban Beach. Both online formats use v21 rooms. Physical Quest 3 and live two-PC validation remain pending.'+readme[end:]
    (D/'README.md').write_text(readme,encoding='utf-8')
    entries.append(dict(path='README.md',mode='100644',type='blob',content=readme))
    for source,target in ART.items():
        p=R/source;dest=D/target;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        data=p.read_bytes();binary.append(dict(path=target,source=source,bytes=len(data),
            git_blob_sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()))
    assert all(Path(e['path']).suffix not in ('.dll','.assets','.resource','.zip','.bin') for e in entries)
    (R/'analysis/v21-publish-text.json').write_text(json.dumps(entries,ensure_ascii=False),encoding='utf-8')
    (R/'analysis/v21-publish-binary.json').write_text(json.dumps(binary,indent=2))
    print(json.dumps(dict(text_entries=len(entries),own_previews=len(binary),source_only=True)))
if __name__=='__main__':main()
