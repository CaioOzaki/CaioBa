"""Compose only authorized v26 deltas from the immutable delivered v25 files."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_art_v26 import build_art_assets_v26
from build_ui_v26 import build_menu_v26

def main():
 source=R/'versions/cloudcourt-v25-antes-v26';out=R/'visuals-v26-integrated';out.mkdir(exist_ok=True)
 names=['resources.assets','level0','level1','level3']
 files={n:UnityPy.load(str(source/n)).file for n in names}
 before={n:{i:o.get_raw_data() for i,o in f.objects.items()} for n,f in files.items()}
 reports=dict(art=build_art_assets_v26(files),menu=build_menu_v26(files['level0']))
 reports['files']={}
 for n,f in files.items():
  data=f.save();(out/n).write_bytes(data);check=UnityPy.load(data).file
  assert set(check.objects)==set(f.objects)
  assert all(check.objects[i].get_raw_data()==o.get_raw_data() for i,o in f.objects.items())
  reports['files'][n]=dict(source_sha256=hashlib.sha256((source/n).read_bytes()).hexdigest(),
    sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),
    changed_existing=[i for i,b in before[n].items() if check.objects[i].get_raw_data()!=b],
    created=sorted(set(check.objects)-set(before[n])))
 (out/'build-report.json').write_text(json.dumps(reports,indent=2))
 print(json.dumps(reports['files'],indent=2))
if __name__=='__main__':main()
