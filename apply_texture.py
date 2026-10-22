import sys,pathlib,hashlib,json,shutil
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from PIL import Image
p=R/'working/VolleyballFever_Data/resources.assets'
backup=R/'backup/resources.assets'
if not backup.exists():shutil.copy2(p,backup)
e=UnityPy.load(str(p));f=e.file
obj=next(o for o in e.objects if o.path_id==40 and o.type.name=='Texture2D')
t=obj.read();assert t.m_Name=='VolleyballD'
before={'width':t.m_Width,'height':t.m_Height,'format':t.m_TextureFormat,'mips':t.m_MipCount,'stream':str(t.m_StreamData)}
source=Image.open(R/'assets/Mikasa-BV550C-atlas.png').convert('RGB')
t.set_image(source,mipmap_count=t.m_MipCount or 1);t.save()
p.write_bytes(f.save())
# Read back the serialized file and decode its texture, verifying the result.
check=UnityPy.load(str(p));new=next(o for o in check.objects if o.path_id==40).read()
assert new.m_Name=='VolleyballD' and new.m_Width==1024 and new.m_Height==1024
new.image.save(R/'analysis/Mikasa-texture-readback.png')
assert len(list(e.objects))==len(list(check.objects))
report={'file':'VolleyballFever_Data/resources.assets','path_id':40,'before':before,'after':{'format':new.m_TextureFormat,'mips':new.m_MipCount,'embedded_bytes':len(new.image_data)},'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects_preserved':len(list(check.objects)),'verified':'Saved file reopened and texture decoded successfully'}
(R/'analysis/texture-patch-manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
