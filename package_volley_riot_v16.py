"""Build an owned-game delta installer from a verified v15 baseline.
No Steam executables or whole game DLLs are placed in the ZIP.
"""
import argparse,hashlib,json,re,shutil,struct,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--v15-package',type=Path,required=True);p.add_argument('--output',type=Path,default=R/'distribution/Volley-Riot-v16');a=p.parse_args()
H=lambda b:hashlib.sha256(b).hexdigest()
def prior_file(name):
 if a.v15_package.is_dir():return (a.v15_package/name).read_bytes()
 with zipfile.ZipFile(a.v15_package) as z:
  prefix=next(n[:-len('patch.json')] for n in z.namelist() if n.endswith('patch.json'))
  return z.read(prefix+name)
prior=json.loads(prior_file('patch.json').decode('utf-8-sig'));previous={f['path']:f for f in prior['files']}
candidate=json.loads((a.candidate/'manifest.json').read_text())
names=sorted(set(previous)|{f['path'] for f in candidate})
allowed={'GameAssembly.dll','VolleyballFever_Data/globalgamemanagers.assets','VolleyballFever_Data/il2cpp_data/Metadata/global-metadata.dat'}|{'VolleyballFever_Data/'+f for f in ['resources.assets','level0','level1','level2','level3','sharedassets0.assets','sharedassets1.assets','sharedassets3.assets']}
assert set(names)==allowed and len(names)==11
def apply(src,patch):
 n,count=struct.unpack_from('<qi',patch);assert 0<n<200*1024*1024 and 0<=count<=60000
 out=bytearray(src[:n]);out.extend(bytes(max(0,n-len(out))));at=12
 for _ in range(count):
  offset,size=struct.unpack_from('<qi',patch,at);at+=12
  assert 0<size<=4096 and 0<=offset<=n-size
  out[offset:offset+size]=patch[at:at+size];at+=size
 assert at==len(patch)
 return bytes(out)
def delta(src,dst):
 blocks=[(i,dst[i:i+4096]) for i in range(0,len(dst),4096) if src[i:i+4096]!=dst[i:i+4096]]
 patch=struct.pack('<qi',len(dst),len(blocks))+b''.join(struct.pack('<qi',i,len(b))+b for i,b in blocks)
 assert apply(src,patch)==dst
 return patch
a.output.mkdir(parents=True,exist_ok=True)
manifest={'version':'Volley-Riot-v16','steam_build':9216628,'network_versions':['VolleyRiot-2v2-v16','VolleyRiot-4v4-v16'],'validation':'Automated native logic and installer tests; live VR and two-PC session pending','files':[]}
fixture=R/'tools/v16-installer-fixture';fixture.mkdir(parents=True,exist_ok=True);(fixture/'VolleyballFever.exe').write_bytes(b'installer fixture, not executable')
fixture_v15=R/'tools/v16-fixture-v15';fixture_v15.mkdir(parents=True,exist_ok=True)
index=0
for path in names:
 baseline=(a.game/path).read_bytes();record=previous.get(path)
 if record:
  assert H(baseline)==record['modified_sha256'],('v15 baseline mismatch',path)
  reverse=prior_file(record['reverse']['name']);assert H(reverse)==record['reverse']['sha256']
  original=apply(baseline,reverse);assert H(original)==record['original_sha256']
 else:original=baseline
 dest=a.candidate/path;modified=dest.read_bytes() if dest.exists() else baseline
 item={'path':path,'original_sha256':H(original),'modified_sha256':H(modified)}
 operations=[('forward',original,modified),('reverse',modified,original)]
 if H(baseline)!=H(original):
  item['previous_sha256']=H(baseline);operations += [('upgrade',baseline,modified),('previous_reverse',baseline,original)]
 for key,src,dst in operations:
  direction='reverse' if key in ['reverse','previous_reverse'] else 'forward'
  name=f'{index}-{direction}.bin';index+=1;data=delta(src,dst);(a.output/name).write_bytes(data);item[key]={'name':name,'sha256':H(data)}
 manifest['files'].append(item)
 for root,data in [(fixture,original),(fixture_v15,baseline)]:
  target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 print('verified delta',path,flush=True)
(a.output/'patch.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
installer=(R/'Apply-Complete-Mod.ps1').read_text(encoding='utf-8-sig')
start=installer.index('    $allowed=@(');end=installer.index('\n    $seen=',start)
installer=installer[:start]+"    $allowed=@("+','.join("'"+x+"'" for x in names)+")\n    if($config.files.Count -ne 11){throw 'Manifesto incompleto.'}"+installer[end:]
installer=installer.replace('Caioba-backup-','VolleyRiot-backup-').replace('Os nove arquivos originais foram restaurados.','Os onze arquivos originais foram restaurados.').replace('Caioba completo v15 checkpoint instalado. Abra o jogo pela Steam.','Volley Riot v16 instalado. Abra o jogo pela Steam.')
(a.output/'Aplicar-mod.ps1').write_text(installer,encoding='utf-8-sig')
for name,flag in [('Instalar.cmd',''),('Restaurar.cmd',' -Restore')]:
 (a.output/name).write_bytes(('@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Aplicar-mod.ps1"'+flag+'\r\npause\r\n').encode('ascii'))
readme='''VOLLEY RIOT v16 — mod para Volleyball Fever, Steam build 9216628

1. Cada amigo precisa ter sua própria instalação compatível do jogo.
2. Extraia o ZIP inteiro em uma pasta. Feche o jogo e execute Instalar.cmd.
3. O instalador aceita o original compatível ou Caioba v15 rostos e faz backup.
4. Abra pela Steam. Todos devem usar este mesmo ZIP, modo, região e sala.
5. Para desfazer, feche o jogo e execute Restaurar.cmd.

Inclui identidade Volley Riot, quadra vermelha/azul, fonte cartoon, antenas,
luvas novas, bots mais altos e correção do cabelo comprido. Ajusta limite
na rede, levantamentos próximos da rede e recepção em todo primeiro toque.
O ginásio tem dois placares de parede. O menu online permite percorrer
quatro skins de emoji/terno e solicitar Change Teams para o próximo ponto.
Time cheio recusa a troca. High five funciona também durante o rally.
As salas v16 ficam separadas das salas v15 e do jogo sem mod.

Código compilado, decisões e instalador verificados automaticamente.
Validação com headset e partida real entre dois PCs ainda pendentes.
Se o Windows negar gravação na pasta Steam, execute Instalar.cmd como administrador.

Fonte Lilita One sob SIL Open Font License; veja OFL-LilitaOne.txt.
Fontes e design: https://github.com/CaioOzaki/CaioBa
'''
(a.output/'LEIA-ME.txt').write_text(readme,encoding='utf-8-sig')
font_license=R/'assets/volley-riot-v16/OFL-LilitaOne.txt'
if font_license.exists():shutil.copy2(font_license,a.output/font_license.name)
report={'files':len(names),'delta_files':index,'manifest_sha256':H((a.output/'patch.json').read_bytes()),'installer_validation':'run test_v16_installer.py before distributing'}
(R/'analysis/v16-package-build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
