"""Explicit v22 sources/art only; do not publish game binaries or experiments."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent;D=R.parent/'Caioba-github'
SOURCES='''mode_2v2.c online_2v2.c serve_feedback_v21.c landing_v20.c hand_visuals_v21.c
score_outline_v20.c build_patch.py Apply-Complete-Mod.ps1 test_online_2v2.py
test_landing_v20.py test_lobby_integrated_v21.py test_score_outline_v20.py
backup_v22.py build_bot_restore_v22.py build_cloudcourt_v22.py build_environment_v22.py
build_hands_v22.py build_ui_v22.py package_cloudcourt_v22.py preview_environment_v22.py
preview_hands_v22.py probe_ui_v22.py test_bots_restore_v22.py test_environment_v22.py
test_hands_assets_v22.py test_hands_integrated_v22.py test_hands_v22.py
test_integration_v22.py test_landing_projection_v22.py test_ui_v22.py
finish_cloudcourt_v22.py stage_cloudcourt_v22.py CHECKPOINT-V22.md'''.split()
REPORTS='''v22-regression.json v22-integration-assets.json v22-bot-restore-tests.json
v22-hands-assets-tests.json v22-hands-native-tests.json v22-hands-integrated-tests.json
v22-landing-projection-tests.json v22-ui-asset-tests.json v22-customization-native-tests.json
v22-score-outline-tests.json v22-ui-unity-before.json v22-ui-unity-after.json v22-release-summary.json'''.split()
ART={'analysis/v22-hands-preview.png':'assets/v22/hands-preview.png',
 'visuals-v22-bots/restored-bots.png':'assets/v22/restored-bots.png',
 'visuals-v22-environment/orla-actual-mesh-preview.png':'assets/v22/orla-preview.png',
 'visuals-v22-environment/post-actual-mesh-preview.png':'assets/v22/posts-preview.png',
 'visuals-v22-environment/board-actual-mesh-preview.png':'assets/v22/boards-preview.png'}
def main():
 entries=[];binary=[]
 for name in SOURCES:
  p=R/name;dest=D/name;dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(p,dest)
  entries.append(dict(path=name,mode='100644',type='blob',content=p.read_text(encoding='utf-8-sig')))
 for name in REPORTS:
  p=R/'analysis'/name;target='validation/cloudcourt-v22/'+name;dest=D/target;dest.parent.mkdir(exist_ok=True,parents=True)
  content=p.read_text(encoding='utf-8-sig');dest.write_text(content,encoding='utf-8')
  entries.append(dict(path=target,mode='100644',type='blob',content=content))
 readme=(D/'README.md').read_text(encoding='utf-8');start=readme.index('Current checkpoint:');end=readme.index('\n',start)
 readme=readme[:start]+'Current checkpoint: **Cloudcourt-v22-correcoes**. [Corrective release notes](CHECKPOINT-V22.md). Fixes the real Done raycast failure, anatomical hands and connected bot arm until the serve whistle, historical bot looks, floor feedback and requested Beach/Indoor visuals. Both online formats use v22 rooms. Quest 3 and real two-PC playtests remain pending.'+readme[end:]
 (D/'README.md').write_text(readme,encoding='utf-8');entries.append(dict(path='README.md',mode='100644',type='blob',content=readme))
 for source,target in ART.items():
  p=R/source;dest=D/target;dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(p,dest);b=p.read_bytes()
  binary.append(dict(path=target,source=source,bytes=len(b),git_blob_sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()))
 (R/'analysis/v22-publish-text.json').write_text(json.dumps(entries,ensure_ascii=False),encoding='utf-8')
 (R/'analysis/v22-publish-binary.json').write_text(json.dumps(binary,indent=2))
 groups=[];group=[];size=0
 for row in entries:
  n=len(json.dumps(row).encode())
  if group and size+n>30000:groups.append(group);group=[];size=0
  group.append(row);size+=n
 if group:groups.append(group)
 for i,group in enumerate(groups):(R/'analysis'/f'v22-publish-group-{i}.json').write_text(json.dumps(group,ensure_ascii=True),encoding='ascii')
 print(json.dumps(dict(text_entries=len(entries),own_previews=len(binary),groups=len(groups),scoped=True)))
if __name__=='__main__':main()
