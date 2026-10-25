import hashlib,json,pathlib,struct,zipfile,subprocess,shutil
R=pathlib.Path(__file__).resolve().parent
OUT=R/'distribution/Cloudcourt-v17-revisao'
OUT.mkdir(parents=True,exist_ok=True)
H=lambda data: hashlib.sha256(data).hexdigest()
names=['GameAssembly.dll']+['VolleyballFever_Data/'+n for n in ['resources.assets','level1','level2','level3','sharedassets1.assets','sharedassets3.assets','sharedassets0.assets','level0','globalgamemanagers.assets']]
def original_path(name):
    basename=pathlib.Path(name).name
    if basename=='globalgamemanagers.assets':return R/'versions/cloudcourt-v16-antes-menu-fix'/basename
    return R/('backup' if basename in ['GameAssembly.dll','resources.assets'] else 'versions/v13-antes-personagens' if basename in ['sharedassets0.assets','level0','globalgamemanagers.assets'] else 'versions/v10-antes-mapas')/basename
def delta(src,dst):
    blocks=[(i,dst[i:i+4096]) for i in range(0,len(dst),4096) if src[i:i+4096]!=dst[i:i+4096]]
    result=bytearray(src[:len(dst)]);result.extend(bytes(max(0,len(dst)-len(result))))
    for offset,data in blocks:result[offset:offset+len(data)]=data
    assert result==dst
    return struct.pack('<qi',len(dst),len(blocks))+b''.join(struct.pack('<qi',i,len(data))+data for i,data in blocks)
manifest={'version':'Cloudcourt-v17-revisao','steam_build':9216628,'files':[]}
for i,name in enumerate(names):
    src=original_path(name).read_bytes();dst=(R/'working'/name).read_bytes()
    record={'path':name,'original_sha256':H(src),'modified_sha256':H(dst)}
    for direction,a,b in [('forward',src,dst),('reverse',dst,src)]:
        patch=delta(a,b);filename=f'{i}-{direction}.bin'
        (OUT/filename).write_bytes(patch)
        record[direction]={'name':filename,'sha256':H(patch)}
    prior=(R/'versions/cloudcourt-v16-antes-revisao'/pathlib.Path(name).name).read_bytes()
    if H(prior) not in [H(src),H(dst)]:
        record['previous_sha256']=H(prior)
        for key,direction,a,b in [('upgrade','forward',prior,dst),('previous_reverse','reverse',prior,src)]:
            filename=f'{20+i}-{direction}.bin';data=delta(a,b);(OUT/filename).write_bytes(data);record[key]={'name':filename,'sha256':H(data)}
    manifest['files'].append(record)
(OUT/'patch.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(OUT/'Aplicar-mod.ps1').write_text((R/'Apply-Complete-Mod.ps1').read_text(encoding='utf-8'),encoding='utf-8-sig')
for name,flag in [('Instalar.cmd',''),('Restaurar.cmd',' -Restore')]:
    (OUT/name).write_text('@echo off\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Aplicar-mod.ps1"'+flag+'\npause\n',encoding='ascii')
(OUT/'LEIA-ME.txt').write_text("""CLOUDCOURT VR v17 - REVISAO - Steam build 9216628

Extraia todo o ZIP e feche o jogo antes de executar Instalar.cmd.
Instala sobre o jogo original compativel ou Cloudcourt-v16-menu-corrigido.
Abra pela Steam. Todos na sala precisam instalar esta v17.
Salas v17 ficam separadas das versoes anteriores. Escolham a mesma regiao e modo.

Correcoes desta revisao:
- Maos esquerda e direita com modelos proprios, poses aberta e fechada.
- Estimativa de velocidade de rastreamento usa tempo real durante a pausa,
  evitando divisao por zero e velocidades NaN ao retomar uma partida solo.
- Frames de bola com posicao/velocidade invalidas sao rejeitados nos hooks.
- Placares de parede ativos, visiveis e com a fonte Cloudcourt.
- Skin nao altera indevidamente o time depois de uma troca.
- Atualizacoes de aparencia nao acumulam eventos antigos no cache da sala.

Mantidos: cabelo preto e roupa vinho da senhora, fisica, modos 2v2/4v4,
assistencias de recepcao e levantamento, rede elevada, antenas visuais,
menu corrigido, novo logo de carregamento e controles A/trigger.

Testes de codigo nativo, reproducoes de falhas e leitura dos assets
foram realizados. Teste fisico no Quest 3 e partida real entre dois PCs
continuam necessarios para confirmar a experiencia completa em VR.

Restaurar.cmd retorna os dez arquivos ao original compativel.
Backups anteriores e ZIPs anteriores foram preservados.
Fonte Baloo 2: licenca Baloo2-OFL.txt incluida.
""",encoding='utf-8-sig')

# Exercise the shipped PowerShell installer on a separate copy, never the live game.
fixture=R/'tools/v17-installer-test';fixture.mkdir(parents=True,exist_ok=True)
(fixture/'VolleyballFever.exe').write_bytes(b'fixture, not executable')
for name in names:
    dest=fixture/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original_path(name),dest)
def run(restore=False,expected=0):
    result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(OUT/'Aplicar-mod.ps1'),'-GameDirectory',str(fixture)]+(['-Restore'] if restore else []),capture_output=True,text=True)
    assert result.returncode==expected,(result.stdout,result.stderr)
    return result.stdout.strip()
def check(key):
    for f in manifest['files']:assert H((fixture/f['path']).read_bytes())==f[key],f['path']
results=[]
results.append(run());check('modified_sha256')
results.append(run());check('modified_sha256')
results.append(run(True));check('original_sha256')
results.append(run(True));check('original_sha256')
# Upgrade from the immediately preceding v16 checkpoint.
for name in names:shutil.copyfile(R/'versions/cloudcourt-v16-antes-revisao'/pathlib.Path(name).name,fixture/name)
results.append(run());check('modified_sha256')
results.append(run(True));check('original_sha256')
# Reject unknown files before modifying any other game file.
bad=fixture/names[-1];bad.write_bytes(bad.read_bytes()+b'incompatible')
before={n:H((fixture/n).read_bytes()) for n in names}
results.append(run(expected=1))
assert before=={n:H((fixture/n).read_bytes()) for n in names}
shutil.copyfile(original_path(names[-1]),bad)
# Reject damaged delta before modifying files, and restore package afterward.
patch=OUT/manifest['files'][-1]['forward']['name'];saved=patch.read_bytes()
try:
    patch.write_bytes(saved+b'corrupted')
    results.append(run(expected=1));check('original_sha256')
finally:patch.write_bytes(saved)
shutil.copyfile(R/'CHECKPOINT-V17-REVISAO.md',OUT/'CHECKPOINT-V17-REVISAO.md')
shutil.copyfile(R/'assets/cloudcourt-v16/Baloo2-OFL.txt',OUT/'Baloo2-OFL.txt')
shutil.copyfile(R/'CLOUDCOURT-GAME-DESIGN.md',OUT/'CLOUDCOURT-GAME-DESIGN.md')
archive=R/'distribution/Cloudcourt-v17-revisao.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in sorted(OUT.iterdir()):z.write(file,'Cloudcourt-v17-revisao/'+file.name)
    for file in sorted((R/'assets/cloudcourt-v16').glob('*.png')):z.write(file,'Cloudcourt-v17-revisao/Previa-texturas/'+file.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
report={'zip':str(archive),'bytes':archive.stat().st_size,'sha256':H(archive.read_bytes()),'files':len(names),'checks':results}
(R/'analysis/complete-package-v17-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
