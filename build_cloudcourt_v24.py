"""Compose authorized v24 assets from immutable delivered v23 resources/menu."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_sleeves_v24 import build_resources_v24
from build_graphics_v24 import build_menu_v24

def main():
 source=R/'versions/cloudcourt-v23-antes-v24'
 out=R/'visuals-v24-integrated';out.mkdir(exist_ok=True)
 reports={}
 for name,builder in [('resources.assets',build_resources_v24),('level0',build_menu_v24)]:
  src=source/name;file=UnityPy.load(str(src)).file
  before={i:o.get_raw_data() for i,o in file.objects.items()}
  report=builder(file);data=file.save();(out/name).write_bytes(data)
  check=UnityPy.load(data).file
  assert set(check.objects)==set(file.objects)
  assert all(check.objects[i].get_raw_data()==o.get_raw_data() for i,o in file.objects.items())
  changed=sorted(i for i,raw in before.items() if check.objects[i].get_raw_data()!=raw)
  report.update(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),actual_changed_existing_ids=changed)
  reports[name]=report
 (out/'build-report.json').write_text(json.dumps(reports,indent=2))
 print(json.dumps({k:dict(sha256=v['sha256'],changed=len(v['actual_changed_existing_ids'])) for k,v in reports.items()}))

if __name__=='__main__':main()
