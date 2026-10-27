"""Explicit source/report publication; no game binaries, ZIPs or binary deltas."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parent
D=R.parent/'Caioba-github'
SOURCES='''spawn_input_v24.c formation_serve.c build_patch.py Apply-Complete-Mod.ps1
backup_v25.py package_cloudcourt_v25.py verify_cloudcourt_v25.py finish_cloudcourt_v25.py
stage_cloudcourt_v25.py CHECKPOINT-V25.md test_trigger_integrated_v25.py
test_pressure_v25.py test_pressure_v25_harness.c'''.split()
REPORTS='''v25-pressure-tests.json v25-trigger-integrated-tests.json
v25-integration-audit.json v25-release-summary.json'''.split()

def main():
 entries=[]
 for name in SOURCES:
  path=R/name;dest=D/name;dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(path,dest)
  entries.append(dict(path=name,mode='100644',type='blob',content=path.read_text(encoding='utf-8-sig')))
 for name in REPORTS:
  target='validation/cloudcourt-v25/'+name;content=(R/'analysis'/name).read_text(encoding='utf-8-sig')
  dest=D/target;dest.parent.mkdir(exist_ok=True,parents=True);dest.write_text(content,encoding='utf-8')
  entries.append(dict(path=target,mode='100644',type='blob',content=content))
 readme=(D/'README.md').read_text(encoding='utf-8');start=readme.index('Current checkpoint:');end=readme.index('\n',start)
 readme=readme[:start]+('Current checkpoint: **Cloudcourt-v25-trigger-fix**. [Repair notes](CHECKPOINT-V25.md). '
  'Fixes analog-only trigger acquisition through the original native hand predicate and throw/release path. '
  'Digital input remains supported; GRAB/A alone cannot spawn balls. Retains all v24 features and room protocol. '
  'Physical Quest 3 confirmation remains pending.')+readme[end:]
 (D/'README.md').write_text(readme,encoding='utf-8');entries.append(dict(path='README.md',mode='100644',type='blob',content=readme))
 (R/'analysis/v25-publish-text.json').write_text(json.dumps(entries,ensure_ascii=False),encoding='utf-8')
 groups=[];group=[];size=0
 for row in entries:
  n=len(json.dumps(row).encode())
  if group and size+n>30000:groups.append(group);group=[];size=0
  group.append(row);size+=n
 if group:groups.append(group)
 for i,group in enumerate(groups):(R/'analysis'/f'v25-publish-group-{i}.json').write_text(json.dumps(group,ensure_ascii=True),encoding='ascii')
 print(json.dumps(dict(text_entries=len(entries),groups=len(groups),no_game_binaries_or_archives=True)))

if __name__=='__main__':main()
