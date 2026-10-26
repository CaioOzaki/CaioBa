"""Scoped sources/own previews only; preserve cleaned remote tree."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parent;D=R.parent/'Caioba-github'
SOURCES=['build_bots_v20.py','restore_middlepart_v20_1.py','test_middlepart_v20_1.py','test_bots_assets_v20.py',
 'backup_middlepart_v20_1.py','package_middlepart_v20_1.py','finish_middlepart_v20_1.py',
 'stage_middlepart_v20_1.py','record_middlepart_v20_1.py','Apply-Complete-Mod.ps1','CHECKPOINT-V20-1-MIDDLEPART.md',
 'assets/bots-v20/README.md','assets/bots-v20/catalog.json','assets/bots-v20/unity-bindings.json']
BINARY=['assets/bots-v20/'+n for n in ['bot-01-modelo.png','bot-01-costas.png','bots-gallery.png']]
entries=[]
for name in SOURCES:
 p=D/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,p)
 entries.append(dict(path=name,mode='100644',type='blob',content=p.read_text(encoding='utf-8-sig')))
for name in ['v20-1-middlepart-tests.json','v20-1-release-summary.json']:
 target='validation/cloudcourt-v20-1/'+name;p=D/target;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'analysis'/name,p)
 entries.append(dict(path=target,mode='100644',type='blob',content=p.read_text()))
readme=(D/'README.md').read_text(encoding='utf-8')
old='Current checkpoint: **Cloudcourt-v20-personagens-menu**. [Release notes](CHECKPOINT-V20.md).'
new='Current checkpoint: **Cloudcourt-v20-1-middle-part**. [Middle-part restoration](CHECKPOINT-V20-1-MIDDLEPART.md). BOT1 uses its preferred pre-v20 hair again; the other eight bots, face/outfit textures, physics and all v20 features are preserved. The same v20 room namespaces remain compatible. The new complete installer accepts the original compatible build or v20. [Base v20 release notes](CHECKPOINT-V20.md).'
assert old in readme or new in readme;readme=readme.replace(old,new);(D/'README.md').write_text(readme,encoding='utf-8');entries.append(dict(path='README.md',mode='100644',type='blob',content=readme))
for name in BINARY:shutil.copyfile(R/name,D/name)
(R/'analysis/v20-1-publish-text.json').write_text(json.dumps(entries,ensure_ascii=False),encoding='utf-8')
binary=[]
for name in BINARY:
 data=(R/name).read_bytes();binary.append(dict(path=name,bytes=len(data),git_blob_sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()))
(R/'analysis/v20-1-publish-binary.json').write_text(json.dumps(binary,indent=2))
print(json.dumps({'text_entries':len(entries),'own_pngs':len(binary)}))
