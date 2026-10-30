"""Compose V30 candidate from immutable V29, without working/live writes."""
from pathlib import Path
import argparse,hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_assets_v29 import FILES
from build_match_settings_v30 import apply_match_settings_v30
from build_launch_ui_v30 import apply_launch_ui_v30
from build_bomb_launch_v30 import apply_bomb_launch_v30
from build_music_v30 import write_audio_art_v30,apply_music_v30
MODIFIED=['resources.assets','level0','sharedassets0.assets','sharedassets0.resource']
def compose_assets_v30(source,output):
 source=Path(source).resolve();output=Path(output).resolve()
 assert source!=output and 'working' not in output.parts and 'sources' not in output.parts
 assert all((source/n).is_file() for n in FILES)
 output.mkdir(parents=True,exist_ok=True)
 menu=UnityPy.load(str(source/'level0')).file
 audio=UnityPy.load(str(source/'sharedassets0.assets')).file
 resources=UnityPy.load(str(source/'resources.assets')).file
 report=dict(baseline=str(source),output=str(output),native_binary='Immutable V29 placeholder. Replace only through production native build before release.')
 report['bomb_launch']=apply_bomb_launch_v30(resources)
 report['launch']=apply_launch_ui_v30(menu)
 report['match_settings']=apply_match_settings_v30(menu)
 pcm,tracks=write_audio_art_v30();bank,audit=apply_music_v30(audio,(source/'sharedassets0.resource').read_bytes(),pcm)
 report.update(playlist=tracks,audio=audit,music_seconds=len(pcm)/22050)
 replacements={'resources.assets':resources.save(),'level0':menu.save(),'sharedassets0.assets':audio.save(),'sharedassets0.resource':bank}
 rows=[]
 for n in FILES:
  old=(source/n).read_bytes();data=replacements.get(n,old);(output/n).write_bytes(data)
  rows.append(dict(path=n,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),changed_from_v29=data!=old))
 report.update(files=rows,file_count=len(rows))
 (R/'analysis/v30-composed-assets.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=R/'versions/cloudcourt-v29-antes-v30');p.add_argument('--output',type=Path,default=R/'visuals-v30');a=p.parse_args()
 d=compose_assets_v30(a.source,a.output);print(json.dumps({k:d[k] for k in ['output','file_count','music_seconds','files']}))
