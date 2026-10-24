"""Replace the visible no-room Discord invitation in the literal table only."""
import struct,json,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parent;B=R/'visuals-v16';rel='VolleyballFever_Data/il2cpp_data/Metadata/global-metadata.dat'
source=Path(os.environ.get('VOLLEY_RIOT_GAME_DIRECTORY',r'C:\Program Files (x86)\Steam\steamapps\common\Volleyball'))/rel
raw=source.read_bytes();data=bytearray(raw)
table,size,start,length=struct.unpack_from('<IIII',data,8)
changes=[]
for at in range(table,table+size,8):
 n,index=struct.unpack_from('<II',data,at)
 text=bytes(data[start+index:start+index+n]).decode('utf8')
 if text=='No rooms found.\nJoin us on Discord :)':
  new=b'No rooms found.\nCreate a room.'
  assert len(new)<=n
  # Fixed-width padding preserves every string/data index and metadata offset.
  data[start+index:start+index+n]=new+b' '*(n-len(new));changes.append(text)
assert len(changes)==1
dest=B/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
m=json.loads((B/'manifest.json').read_text());m=[x for x in m if x['path']!=rel]
m.append({'path':rel,'before':hashlib.sha256(raw).hexdigest(),'after':hashlib.sha256(data).hexdigest()})
(B/'manifest.json').write_text(json.dumps(m,indent=2))
print('metadata literals verified:',len(changes))
