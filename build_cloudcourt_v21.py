"""Compose reviewed v21 deltas from immutable v20.1 backup into a candidate.

No original/extracted binary goes into the public source repository. This
local build requires the user's compatible game installation and backups.
"""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_environment_v21 import build_environment_assets
from build_bot_appearance_v21 import apply_bot_appearance_v21
from build_avatar_v21 import build_resources,build_menu
from build_lobby_v21 import build_lobby_assets_v21
from build_english_v21 import apply_english_v21

BASE=R/'versions/cloudcourt-v20-1-antes-v21'
OUT=R/'visuals-v21-integrated'
NAMES=['level0','level1','level2','level3','level4','resources.assets']+[f'sharedassets{i}.assets' for i in range(5)]
H=lambda b:hashlib.sha256(b).hexdigest()

def source(name):
    p=BASE/name
    return p if p.exists() else R/'working/VolleyballFever_Data'/name

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    originals={n:source(n).read_bytes() for n in NAMES}
    files={n:UnityPy.load(b).file for n,b in originals.items()}
    before={n:{i:o.get_raw_data() for i,o in f.objects.items()} for n,f in files.items()}
    report={'environment':build_environment_assets(files),
            'bots':apply_bot_appearance_v21(files['sharedassets0.assets']),
            'hands':build_resources(files['resources.assets']),
            'customization':build_menu(files['level0']),
            'lobby':build_lobby_assets_v21(files)}
    report['english']=apply_english_v21(files)
    report['files']={}
    for n,f in files.items():
        changed=sorted(i for i,raw in before[n].items() if f.objects[i].get_raw_data()!=raw)
        added=sorted(set(f.objects)-set(before[n]))
        assert set(before[n])<=set(f.objects),'No existing object may be removed'
        if not changed and not added:continue
        data=f.save();assert len(data)<200*1024*1024
        out=OUT/n;out.write_bytes(data)
        check=UnityPy.load(str(out)).file
        assert set(f.objects)==set(check.objects)
        mismatches=[(i,o.type.name,len(o.get_raw_data()),len(check.objects[i].get_raw_data())) for i,o in f.objects.items() if check.objects[i].get_raw_data()!=o.get_raw_data()]
        assert not mismatches,(n,mismatches[:15])
        report['files'][n]=dict(source_sha256=H(originals[n]),sha256=H(data),bytes=len(data),changed=changed,added=added)
    (OUT/'build-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({n:{k:v for k,v in row.items() if k!='source_sha256'} for n,row in report['files'].items()},indent=2))
if __name__=='__main__':main()
