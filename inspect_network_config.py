import pathlib,sys,struct,json
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
env=UnityPy.load(str(R/'working/VolleyballFever_Data/resources.assets'))
for o in env.objects:
 if o.type.name!='MonoBehaviour':continue
 try:
  d=o.read(check_read=False)
  if d.m_Name!='PhotonServerSettings':continue
  raw=o.get_raw_data();needle=d.m_Name.encode();start=raw.index(needle);off=(start+len(needle)+3)&~3
  def string():
   global off
   n=struct.unpack_from('<i',raw,off)[0];off+=4
   assert 0<=n<4096
   s=raw[off:off+n].decode();off=(off+n+3)&~3;return s
  for _ in range(4):string()
  name_server=bool(raw[off]);off=(off+1+3)&~3
  region=string();string();server=string()
  result={'UseNameServer':name_server,'FixedRegion':region,'Server':server,'source':o.assets_file.name}
  (R/'analysis/network-config-summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
 except (ValueError,AttributeError):continue
