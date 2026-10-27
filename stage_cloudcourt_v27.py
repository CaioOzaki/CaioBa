"""Stage scoped elbow sources and concise validation; no gamefiles or ZIPs."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parent;D=R.parent/'Caioba-github'
SOURCES='''elbow_v27.c mode_2v2.c build_patch.py Apply-Complete-Mod.ps1 backup_v27.py
test_elbow_solver_v27.py test_elbow_v27.py test_elbow_integrated_v27.py
build_plain_balls_v27.py test_plain_balls_v27.py preview_plain_balls_v27.py
verify_cloudcourt_v27.py package_cloudcourt_v27.py finish_cloudcourt_v27.py
stage_cloudcourt_v27.py CHECKPOINT-V27.md'''.split()
REPORTS='''elbow-v27-audit.md v27-integration-audit.json v27-release-summary.json v27-installer-checks.json
v27-plain-balls-tests.json'''.split()
def main():
 entries=[]
 def add(target,content):
  assert Path(target).suffix in ('.c','.py','.ps1','.md','.json')
  dest=D/target;dest.parent.mkdir(exist_ok=True,parents=True);dest.write_text(content,encoding='utf-8')
  entries.append(dict(path=target,mode='100644',type='blob',content=content))
 for n in SOURCES:add(n,(R/n).read_text(encoding='utf-8-sig'))
 for n in REPORTS:add('validation/cloudcourt-v27/'+n,(R/'analysis'/n).read_text(encoding='utf-8-sig'))
 for n in ['elbow-v27-results.json','elbow-v27-integrated-results.json']:
  report=json.loads((R/'analysis'/n).read_text());samples=report.pop('samples',[])
  report['selected_samples']=samples[:2];report['all_case_readbacks_kept_locally']=True
  report['reproducible_from_published_test']=True
  add('validation/cloudcourt-v27/'+n,json.dumps(report,indent=2))
 art=R/'assets/cloudcourt-v27';art.mkdir(exist_ok=True)
 (art/'README.md').write_text('''# Cloudcourt v27 ball artwork

Own procedural texture source for the existing dual-venue UV atlas. Indoor keeps
its yellow/blue panels. Beach uses broad perpendicular white/blue/yellow groups
with orange/red fades and dot accents inspired by the supplied references.
Neither texture contains text, logos or badges. No reference photograph or
original game artwork is redistributed. The preview is an offline rasterization
of the actual serialized mesh/UV/texture; it is not a headset capture.
Only texture40 pixel bytes change. Dimensions, twelve mips, GPU bytes, mesh,
materials, colliders and game rules remain unchanged.
''',encoding='utf-8')
 add('assets/cloudcourt-v27/README.md',(art/'README.md').read_text())
 add('assets/cloudcourt-v27/plain-balls-report.json',(art/'plain-balls-report.json').read_text())
 readme=(D/'README.md').read_text(encoding='utf-8');a=readme.index('Current checkpoint:');b=readme.index('\n',a)
 readme=readme[:a]+('Current checkpoint: **Cloudcourt-v27-avatar-elbow**. [Repair notes](CHECKPOINT-V27.md). '
  'Corrects the inward player elbow on the viewer-right side of a front-facing avatar. '
  'Keeps tracked wrists, the original analytic solve, outward poses and opposite arm. '
  'Both balls have no lettering; Beach follows broad white/blue/yellow reference panels with red/orange accents. '
  'Other v26 features and wire format retained. Physical Quest and two-PC confirmation remain pending.')+readme[b:]
 add('README.md',readme)
 images=[]
 for n in ['ball-indoor.png','ball-beach.png','ball-dual-atlas.png','actual-ball-mesh-preview.png']:
  p=art/n;target='assets/cloudcourt-v27/'+n;dest=D/target;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
  images.append(dict(path=target,source=str(p.resolve()),bytes=p.stat().st_size))
 groups=[];group=[];size=0
 for row in entries:
  n=len(json.dumps(row).encode())
  if group and size+n>30000:groups.append(group);group=[];size=0
  group.append(row);size+=n
 if group:groups.append(group)
 for i,g in enumerate(groups):(R/f'analysis/v27-publish-group-{i}.json').write_text(json.dumps(g,ensure_ascii=True),encoding='ascii')
 result=dict(text_entries=len(entries),groups=len(groups),images=images,only_own_png_art=True,no_game_binaries_or_archives=True)
 (R/'analysis/v27-stage-report.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
