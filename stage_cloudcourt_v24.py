"""Publish explicit authored sources/reports; no game files, binary deltas or ZIP."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parent
D=R.parent/'Caioba-github'
SOURCES='''mode_2v2.c formation_serve.c lobby_v18.c hand_visuals_v21.c online_2v2.c
celebration_v15.c serve_feedback_v21.c comfort_v14.c identity_v16.c customization_v19.c spawn_input_v24.c
graphics_v24.c sleeves_v24.c build_patch.py Apply-Complete-Mod.ps1 backup_v24.py
build_cloudcourt_v24.py build_graphics_v24.py build_sleeves_v24.py package_cloudcourt_v24.py
verify_cloudcourt_v24.py finish_cloudcourt_v24.py stage_cloudcourt_v24.py CHECKPOINT-V24.md
test_spawn_input_v24.py test_online_2v2.py test_lobby_integrated_v21.py
test_bot_target_v24.py test_bot_target_integrated_v24.py test_graphics_v24.py
test_graphics_v24_harness.c test_sleeves_v24.py test_sleeves_native_v24.py
test_sleeves_v24_harness.c run_regression_v24.py probe_graphics_v24.py
prepare_probe_graphics_v24.py probe_rendering_v24.py prepare_probe_rendering_v24.py'''.split()
REPORTS='''v24-regression.json v24-integration-audit.json v24-spawn-input-tests.json
v24-bot-target-native-tests.json v24-bot-target-integrated-tests.json
v24-sleeves-assets-tests.json v24-sleeves-native-tests.json v24-graphics-tests.json
v24-ui-raycast-tests.json v24-graphics-rendering-unity.json v24-release-summary.json'''.split()

def main():
 entries=[]
 for name in SOURCES:
  path=R/name;dest=D/name;dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(path,dest)
  entries.append(dict(path=name,mode='100644',type='blob',content=path.read_text(encoding='utf-8-sig')))
 for name in REPORTS:
  report=json.loads((R/'analysis'/name).read_text(encoding='utf-8-sig'))
  report.pop('native_fixture',None)
  target='validation/cloudcourt-v24/'+name;content=json.dumps(report,indent=2)
  dest=D/target;dest.parent.mkdir(exist_ok=True,parents=True);dest.write_text(content,encoding='utf-8')
  entries.append(dict(path=target,mode='100644',type='blob',content=content))
 readme=(D/'README.md').read_text(encoding='utf-8');start=readme.index('Current checkpoint:');end=readme.index('\n',start)
 readme=readme[:start]+('Current checkpoint: **Cloudcourt-v24-celebracao-graficos**. '
  '[Release notes](CHECKPOINT-V24.md). Bots celebrate toward the scoring teammate; '
  'trigger-only serve/lobby ball spawning, four persisted graphics presets and outfit-matched wrist sleeves. '
  'All online peers must use v24 rooms. Physics unchanged; actual Quest 3 rendering/FPS and two-PC tests remain pending.')+readme[end:]
 (D/'README.md').write_text(readme,encoding='utf-8');entries.append(dict(path='README.md',mode='100644',type='blob',content=readme))
 (R/'analysis/v24-publish-text.json').write_text(json.dumps(entries,ensure_ascii=False),encoding='utf-8')
 groups=[];group=[];size=0
 for row in entries:
  n=len(json.dumps(row).encode())
  if group and size+n>30000:groups.append(group);group=[];size=0
  group.append(row);size+=n
 if group:groups.append(group)
 for i,group in enumerate(groups):(R/'analysis'/f'v24-publish-group-{i}.json').write_text(json.dumps(group,ensure_ascii=True),encoding='ascii')
 print(json.dumps(dict(text_entries=len(entries),groups=len(groups),no_game_binaries_or_archives=True)))

if __name__=='__main__':main()
