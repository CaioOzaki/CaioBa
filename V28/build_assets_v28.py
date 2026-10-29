"""Compose v28 deltas from immutable v27 without altering the live installation."""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_bomb_v28 import apply_bomb_v28
from build_customization_v28 import apply_customization_v28
from build_settings_audio_v28 import write_audio_art,apply_audio_v28,apply_settings_logo_v28

def main():
 B=R/'versions/cloudcourt-v27-antes-v28';D=R/'visuals-v28';D.mkdir(exist_ok=True)
 files={n:UnityPy.load(str(B/n)).file for n in ['resources.assets','level0','sharedassets0.assets']}
 pcm,tracks=write_audio_art()
 reports={'bomb':apply_bomb_v28(files['resources.assets']),'customization':apply_customization_v28(files['resources.assets'],files['level0'])}
 reports['settings_logo']=apply_settings_logo_v28(files['resources.assets'],files['level0'])
 bank,audit=apply_audio_v28(files['sharedassets0.assets'],(B/'sharedassets0.resource').read_bytes(),pcm);reports.update(audio=audit,playlist=tracks)
 rows=[]
 for n,f in files.items():
  data=f.save();(D/n).write_bytes(data);rows.append(dict(path=n,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
 (D/'sharedassets0.resource').write_bytes(bank);rows.append(dict(path='sharedassets0.resource',sha256=hashlib.sha256(bank).hexdigest(),bytes=len(bank)))
 reports['outputs']=rows;(D/'assets-v28-report.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
 print(json.dumps({'composed_assets':rows,'playlist_minutes':len(pcm)/22050/60,'hats':reports['customization']['hats']}))
if __name__=='__main__':main()
