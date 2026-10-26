"""Compose only v23 hand geometry from the immutable delivered v22 resource."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_hands_v23 import build_resources_v23
def main():
 source=R/'versions/cloudcourt-v22-antes-v23/resources.assets'
 out=R/'visuals-v23-integrated';out.mkdir(exist_ok=True)
 f=UnityPy.load(str(source)).file;before={i:o.get_raw_data() for i,o in f.objects.items()}
 report=build_resources_v23(f);data=f.save();(out/'resources.assets').write_bytes(data)
 check=UnityPy.load(data).file
 assert set(check.objects)==set(f.objects)
 assert all(check.objects[i].get_raw_data()==o.get_raw_data() for i,o in f.objects.items())
 changed=sorted(i for i,b in before.items() if check.objects[i].get_raw_data()!=b)
 assert changed==report['changed_existing_ids']
 report.update(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
  sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),all_original_physics_scripts_materials_textures_unchanged=True)
 (out/'build-report.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(dict(changed=changed,added=report['added_ids'],sha256=report['sha256'])))
if __name__=='__main__':main()
