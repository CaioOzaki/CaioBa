"""Exercise the shipped PowerShell installer only against disposable fixtures."""
import hashlib,json,shutil,subprocess,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent;package=R/'distribution/Volley-Riot-v16';fixture=R/'tools/v16-installer-fixture';prior=R/'tools/v16-fixture-v15'
m=json.loads((package/'patch.json').read_text());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(restore=False,expected=0):
 cmd=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(package/'Aplicar-mod.ps1'),'-GameDirectory',str(fixture)]
 if restore:cmd+=['-Restore']
 result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
 assert result.returncode==expected,(result.stdout,result.stderr)
 return result.stdout.strip()
def check(key):
 for f in m['files']:assert H(fixture/f['path'])==f[key],f['path']
results=[]
check('original_sha256')
results.append(run());check('modified_sha256')
results.append(run());check('modified_sha256')
results.append(run(True));check('original_sha256')
results.append(run(True));check('original_sha256')
for f in m['files']:shutil.copy2(prior/f['path'],fixture/f['path'])
results.append(run());check('modified_sha256')
results.append(run(True));check('original_sha256')
target=fixture/'VolleyballFever_Data/level0';valid=target.read_bytes();target.write_bytes(valid+b'corrupt fixture')
before={f['path']:H(fixture/f['path']) for f in m['files']};results.append(run(expected=1))
assert before=={f['path']:H(fixture/f['path']) for f in m['files']},'incompatible input changed another game file'
target.write_bytes(valid);check('original_sha256')
archive=package.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for file in sorted(package.iterdir()):
  if file.is_file():z.write(file,'Volley-Riot-v16/'+file.name)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 manifest=json.loads(z.read('Volley-Riot-v16/patch.json'))
 assert manifest==m and not any(n.endswith(('.dll','.exe','.assets')) for n in z.namelist())
 for f in m['files']:
  for key in ['forward','reverse','upgrade','previous_reverse']:
   if key in f:assert hashlib.sha256(z.read('Volley-Riot-v16/'+f[key]['name'])).hexdigest()==f[key]['sha256']
digest=H(archive);archive.with_suffix('.zip.sha256').write_text(digest+'  '+archive.name+'\n')
report={'passed':True,'files':len(m['files']),'checks':['original to v16','install repeated','v16 to original','restore repeated','v15 rostos to v16','restore after upgrade','incompatible input aborts before mutation','ZIP CRC and every delta digest'],'zip_bytes':archive.stat().st_size,'sha256':digest,'scope':'Disposable fixture; live Steam install unchanged'}
(R/'analysis/v16-installer-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
