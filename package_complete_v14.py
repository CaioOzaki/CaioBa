import hashlib,json,pathlib,struct,zipfile,subprocess,shutil
R=pathlib.Path(__file__).resolve().parent
OUT=R/'distribution/Caioba-completo-v14-checkpoint'
OUT.mkdir(parents=True,exist_ok=True)
H=lambda data: hashlib.sha256(data).hexdigest()
names=['GameAssembly.dll']+['VolleyballFever_Data/'+n for n in ['resources.assets','level1','level2','level3','sharedassets1.assets','sharedassets3.assets','sharedassets0.assets','level0']]
def original_path(name):
    basename=pathlib.Path(name).name
    return R/('backup' if basename in ['GameAssembly.dll','resources.assets'] else 'versions/v13-antes-personagens' if basename in ['sharedassets0.assets','level0'] else 'versions/v10-antes-mapas')/basename
def delta(src,dst):
    blocks=[(i,dst[i:i+4096]) for i in range(0,len(dst),4096) if src[i:i+4096]!=dst[i:i+4096]]
    result=bytearray(src[:len(dst)]);result.extend(bytes(max(0,len(dst)-len(result))))
    for offset,data in blocks:result[offset:offset+len(data)]=data
    assert result==dst
    return struct.pack('<qi',len(dst),len(blocks))+b''.join(struct.pack('<qi',i,len(data))+data for i,data in blocks)
manifest={'version':'Caioba-completo-v14-checkpoint','steam_build':9216628,'files':[]}
for i,name in enumerate(names):
    src=original_path(name).read_bytes();dst=(R/'working'/name).read_bytes()
    record={'path':name,'original_sha256':H(src),'modified_sha256':H(dst)}
    for direction,a,b in [('forward',src,dst),('reverse',dst,src)]:
        patch=delta(a,b);filename=f'{i}-{direction}.bin'
        (OUT/filename).write_bytes(patch)
        record[direction]={'name':filename,'sha256':H(patch)}
    prior=(R/'versions/v13-antes-personagens'/pathlib.Path(name).name).read_bytes()
    if H(prior) not in [H(src),H(dst)]:
        record['previous_sha256']=H(prior)
        for key,direction,a,b in [('upgrade','forward',prior,dst),('previous_reverse','reverse',prior,src)]:
            filename=f'{20+i}-{direction}.bin';data=delta(a,b);(OUT/filename).write_bytes(data);record[key]={'name':filename,'sha256':H(data)}
    manifest['files'].append(record)
(OUT/'patch.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(OUT/'Aplicar-mod.ps1').write_text((R/'Apply-Complete-Mod.ps1').read_text(encoding='utf-8'),encoding='utf-8-sig')
for name,flag in [('Instalar.cmd',''),('Restaurar.cmd',' -Restore')]:
    (OUT/name).write_text('@echo off\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Aplicar-mod.ps1"'+flag+'\npause\n',encoding='ascii')
(OUT/'LEIA-ME.txt').write_text("""CAIOBA v14 CHECKPOINT - Volleyball Fever Steam build 9216628

Extraia o ZIP inteiro. Feche o jogo e execute Instalar.cmd.
Cada amigo precisa ter o jogo original e instalar este mesmo ZIP.
Aceita a versao original ou o checkpoint v13. Abra pela Steam.
Para jogar juntos, escolham mesma regiao, mesmo modo e mesma sala.

Inclui sete bots arredondados, quatro avatares de terno/emoji,
rede com textura propria e 40 cm mais alta, retirada do Daily Challenge.
4v4 solo/online usa velocidades e levantamentos do 2v2;
bots aliados evitam bloqueio e priorizam tres toques.
No segundo toque do time, segure os DOIS GRABs para levantar com assistencia.
Soltar um GRAB desativa a ajuda. Os dedos se abrem enquanto ativa.
Em online os quatro emojis sao atribuidos pela ordem dos jogadores na sala.
Preserva as correcoes v13 de fisica online e saque na mao do jogador correto.

Checkpoint testado em simulacao do codigo nativo e na inicializacao do jogo.
Ainda precisa de partida em VR para validar animacoes, conforto da rede mais
alta, feedback das maos e dois PCs conectados. Nao representa playtest VR.

Restaurar.cmd volta os nove arquivos ao original. Nao apaga saves.
O instalador guarda uma copia dos arquivos anteriores na pasta do jogo.
O ZIP v13 anterior foi preservado separadamente para voltar ao checkpoint.
""",encoding='utf-8-sig')

# Exercise the shipped PowerShell installer on a separate copy, never the live game.
fixture=R/'tools/complete-installer-test';fixture.mkdir(parents=True,exist_ok=True)
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
# Upgrade from complete v13 checkpoint.
for name in names:shutil.copyfile(R/'versions/v13-antes-personagens'/pathlib.Path(name).name,fixture/name)
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
archive=R/'distribution/Caioba-completo-v14-checkpoint.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in sorted(OUT.iterdir()):z.write(file,'Caioba-completo-v14-checkpoint/'+file.name)
    for file in sorted((R/'assets/caioba-v14').glob('*.png')):z.write(file,'Caioba-completo-v14-checkpoint/Previa-texturas/'+file.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
report={'zip':str(archive),'bytes':archive.stat().st_size,'sha256':H(archive.read_bytes()),'files':len(names),'checks':results}
(R/'analysis/complete-package-v14-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
