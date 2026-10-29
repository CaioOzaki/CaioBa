"""Compose v29 candidate from immutable v28: no working/live/install writes."""
from pathlib import Path
import argparse,hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_training_v29 import apply_training_v29
from build_rewards_art_v29 import apply_rewards_art_v29
from build_bots_refine_v29 import build_resources_v29
from build_refinement_ui_v29 import apply_refinement_ui_v29,apply_startup_wordmark_v29
FILES=['GameAssembly.dll','globalgamemanagers.assets','level0','level1','level2','level3','resources.assets','resources.resource','sharedassets0.assets','sharedassets0.resource','sharedassets1.assets','sharedassets1.resource','sharedassets2.assets','sharedassets2.resource','sharedassets3.assets','sharedassets4.assets','sharedassets4.resource']
MODIFIED=['resources.assets','level0','level1','level2','level3','globalgamemanagers.assets']

def compose_assets_v29(source,output):
    source=Path(source);output=Path(output)
    assert source.resolve()!=output.resolve() and 'working' not in output.resolve().parts and 'sources' not in output.resolve().parts
    assert all((source/n).is_file() for n in FILES)
    output.mkdir(parents=True,exist_ok=True)
    files={n:UnityPy.load(str(source/n)).file for n in MODIFIED}
    report=dict(baseline=str(source),output=str(output),training=[],native_binary='Unchanged v28 baseline placeholder. Root native build/staging must replace GameAssembly.dll before release.')
    report['rewards']=apply_rewards_art_v29(files['resources.assets'],files['level0'])
    report['bots']=build_resources_v29(files['resources.assets'],R/'assets/refinement-v29/bot-callouts')
    report['ui']=apply_refinement_ui_v29(files['level0'])
    report['startup']=apply_startup_wordmark_v29(files['globalgamemanagers.assets'])
    for name in ('level1','level2','level3'):report['training'].append(dict(scene=name,**apply_training_v29(files['resources.assets'],files[name])))
    rows=[]
    for name in FILES:
        original=(source/name).read_bytes();data=files[name].save() if name in files else original
        (output/name).write_bytes(data);rows.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),changed_from_v28=data!=original))
    report['files']=rows;report['file_count']=len(rows)
    (R/'analysis/v29-composed-assets.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (output/'assets-v29-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=R/'versions/cloudcourt-v28-antes-v29');p.add_argument('--output',type=Path,default=R/'visuals-v29');a=p.parse_args()
    result=compose_assets_v29(a.source,a.output)
    print(json.dumps(dict(output=result['output'],file_count=result['file_count'],files=result['files']),indent=2))
