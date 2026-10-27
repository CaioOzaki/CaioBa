"""Explicit source/own-art publication. Never stage gamefiles/deltas/archives."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent;D=R.parent/'Caioba-github'
SOURCES='''ball_style_v26.c comfort_v14.c customization_v19.c formation_serve.c graphics_v24.c
hand_visuals_v21.c identity_v16.c lobby_v18.c mode_2v2.c online_2v2.c score_outline_v20.c spin_mod.c
build_patch.py Apply-Complete-Mod.ps1 backup_v26.py build_art_v26.py build_ui_v26.py build_cloudcourt_v26.py
test_art_v26.py preview_art_v26.py test_bot_pose_v26.py test_bot_pose_integrated_v26.py test_online_state_v26.py
test_ball_style_integrated_v26.py test_graphics_v26.py test_ui_native_v26.py test_trigger_integrated_v26.py
prepare_probe_ui_v26.py probe_ui_v26.py verify_cloudcourt_v26.py package_cloudcourt_v26.py finish_cloudcourt_v26.py
stage_cloudcourt_v26.py CHECKPOINT-V26.md'''.split()
REPORTS='''v26-ball-style-integrated-tests.json v26-bot-pose-integrated-tests.json v26-bot-pose-native-tests.json
v26-bot-pose-asset-safety.json v26-bot-pose-report.md v26-online-state-tests.json v26-online-audit.md
v26-graphics-tests.json v26-ui-native-tests.json v26-ui-unity-final.json v26-trigger-integrated-tests.json
v26-integration-audit.json v26-release-summary.json v26-installer-checks.json'''.split()
IMAGES=['ball-indoor.png','ball-beach.png','ball-dual-atlas.png','arena-flag.png',
        'actual-ball-mesh-preview.png','actual-arena-flag-preview.png']
def main():
 entries=[]
 def add(source,target):
  content=source.read_text(encoding='utf-8-sig');dest=D/target;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(content,encoding='utf-8')
  entries.append(dict(path=target,mode='100644',type='blob',content=content))
 for n in SOURCES:add(R/n,n)
 for n in REPORTS:add(R/'analysis'/n,'validation/cloudcourt-v26/'+n)
 add(R/'assets/cloudcourt-v26/art-report.json','assets/cloudcourt-v26/art-report.json')
 doc='''# CloudCourt v26 own art

Original procedural ball panel artwork and sphere mesh, gym flag artwork and emblem.
No manufacturer logo, branded image, original base-game texture or mesh is included.
build_art_v26.py generates the art and the targeted serialized deltas against a separately owned compatible base.
The indoor ball uses yellow/blue panels; Beach uses white/yellow/blue. Both say CloudCourt.
The actual mesh previews are offline readbacks; they are not headset or multiplayer captures.
The included game font remains covered by the existing OFL notice. Raster lettering does not include a font file.
'''
 docpath=R/'assets/cloudcourt-v26/README.md';docpath.write_text(doc,encoding='utf-8');add(docpath,'assets/cloudcourt-v26/README.md')
 readme=(D/'README.md').read_text(encoding='utf-8');a=readme.index('Current checkpoint:');b=readme.index('\n',a)
 readme=readme[:a]+('Current checkpoint: **Cloudcourt-v26-session-repair**. [Release notes](CHECKPOINT-V26.md). '
  'Repairs consecutive online sessions, lobby holding/net rendering, symmetric court limits, bot gaze/body pose, '
  'SDF outlines and preview lifecycles. Adds own venue ball artwork, vertical flags and host Indoor antennas. '
  'Graphics choices apply after restarting Cloudcourt. Native wire format retained; physical Quest/two-PC confirmation pending.')+readme[b:]
 (D/'README.md').write_text(readme,encoding='utf-8');entries.append(dict(path='README.md',mode='100644',type='blob',content=readme))
 images=[]
 for n in IMAGES:
  p=R/'assets/cloudcourt-v26'/n;target='assets/cloudcourt-v26/'+n;dest=D/target;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
  images.append(dict(path=target,source=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
 groups=[];group=[];size=0
 for row in entries:
  n=len(json.dumps(row).encode())
  if group and size+n>30000:groups.append(group);group=[];size=0
  group.append(row);size+=n
 if group:groups.append(group)
 for i,g in enumerate(groups):(R/f'analysis/v26-publish-group-{i}.json').write_text(json.dumps(g,ensure_ascii=True),encoding='ascii')
 report=dict(text_entries=len(entries),groups=len(groups),images=images,no_game_binaries_or_archives=True)
 (R/'analysis/v26-stage-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':main()
