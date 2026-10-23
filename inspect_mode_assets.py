import sys,pathlib,json,struct
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
env=UnityPy.load(str(R/'working/VolleyballFever_Data'))
out=[]
for o in env.objects:
 if o.type.name!='MonoBehaviour':continue
 try:
  d=o.read(check_read=False);s=d.m_Script.deref().read()
  if s.m_ClassName not in ['BotArea','Team','Bot','SoloPageController']:continue
  out.append({'file':o.assets_file.name,'id':o.path_id,'class':s.m_ClassName,'raw':o.get_raw_data().hex()})
 except Exception:continue
(R/'analysis/mode-assets.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))

