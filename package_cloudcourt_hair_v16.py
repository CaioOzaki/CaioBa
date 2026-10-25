import hashlib,json,pathlib,struct,zipfile,subprocess,shutil
R=pathlib.Path(__file__).resolve().parent
OUT=R/'distribution/Cloudcourt-v16-cabelo-preto'
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
manifest={'version':'Cloudcourt-v16-cabelo-preto','steam_build':9216628,'files':[]}
for i,name in enumerate(names):
    src=original_path(name).read_bytes();dst=(R/'working'/name).read_bytes()
    record={'path':name,'original_sha256':H(src),'modified_sha256':H(dst)}
    for direction,a,b in [('forward',src,dst),('reverse',dst,src)]:
        patch=delta(a,b);filename=f'{i}-{direction}.bin'
        (OUT/filename).write_bytes(patch)
        record[direction]={'name':filename,'sha256':H(patch)}
    prior=(R/'versions/cloudcourt-v16-antes-cabelo'/pathlib.Path(name).name).read_bytes()
    if H(prior) not in [H(src),H(dst)]:
        record['previous_sha256']=H(prior)
        for key,direction,a,b in [('upgrade','forward',prior,dst),('previous_reverse','reverse',prior,src)]:
            filename=f'{20+i}-{direction}.bin';data=delta(a,b);(OUT/filename).write_bytes(data);record[key]={'name':filename,'sha256':H(data)}
    manifest['files'].append(record)
(OUT/'patch.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(OUT/'Aplicar-mod.ps1').write_text((R/'Apply-Complete-Mod.ps1').read_text(encoding='utf-8'),encoding='utf-8-sig')
for name,flag in [('Instalar.cmd',''),('Restaurar.cmd',' -Restore')]:
    (OUT/name).write_text('@echo off\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Aplicar-mod.ps1"'+flag+'\npause\n',encoding='ascii')
(OUT/'LEIA-ME.txt').write_text("""CLOUDCOURT VR v16 - CABELO PRETO - Steam build 9216628

Extraia o ZIP inteiro. Feche o jogo e execute Instalar.cmd.
Instala sobre o jogo original compativel ou o checkpoint Cloudcourt v16.
Abra pela Steam. Para ver o cabelo novo, instale este pacote em cada PC.
Escolham a mesma regiao, modo e sala.

Nova identidade Cloudcourt VR, fonte Baloo 2, menus arredondados,
quadra azul/vermelha, antenas visuais e placares de parede no indoor.
Design editavel: https://www.figma.com/design/1sIgjKcMItHmbLIu1dnch0?node-id=2-24

Limites simetricos na rede. Levantamentos para uma janela de ataque
perto da rede; segundo toque do player usa os DOIS GRABs e luvas abertas.
Recepcao assistida no primeiro toque de cada posse do time.
Mais altura no salto e trajetoria de ataque dos bots.
High five online durante toda a partida e lobby, com contato varrido.
A ou trigger interagem com os menus.

No menu da partida online: CHANGE TEAMS e quatro skins.
A troca ocupa a vaga de um bot no outro time; respeita a capacidade.
Durante o rally, aplica ao fim do ponto. Skin escolhida e sincronizada.
As novas maos sao luvas cartoon, com modelo aberto para levantar.
Tela de boas-vindas, convite ao Discord e Daily Challenge removidos.

Alteracao visual validada por leitura dos assets e comparacao das texturas.
Gameplay e protocolo permanecem iguais ao checkpoint v16.
Ainda precisa de playtest real no Quest 3 e entre dois PCs.
menu-figma.png e uma proposta visual editavel exportada; nao e captura VR.

Restaurar.cmd volta os nove arquivos ao original. Nao apaga saves.
Os ZIPs anteriores foram preservados.
Fonte Baloo 2: licenca Baloo2-OFL.txt incluida.
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
# Upgrade from complete v15 checkpoint.
for name in names:shutil.copyfile(R/'versions/cloudcourt-v16-antes-cabelo'/pathlib.Path(name).name,fixture/name)
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
shutil.copyfile(R/'CHECKPOINT-V16-CABELO.md',OUT/'CHECKPOINT-V16-CABELO.md')
shutil.copyfile(R/'assets/cloudcourt-v16/Baloo2-OFL.txt',OUT/'Baloo2-OFL.txt')
shutil.copyfile(R/'CLOUDCOURT-GAME-DESIGN.md',OUT/'CLOUDCOURT-GAME-DESIGN.md')
archive=R/'distribution/Cloudcourt-v16-cabelo-preto.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in sorted(OUT.iterdir()):z.write(file,'Cloudcourt-v16-cabelo-preto/'+file.name)
    for file in sorted((R/'assets/cloudcourt-v16').glob('*.png')):z.write(file,'Cloudcourt-v16-cabelo-preto/Previa-texturas/'+file.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
report={'zip':str(archive),'bytes':archive.stat().st_size,'sha256':H(archive.read_bytes()),'files':len(names),'checks':results}
(R/'analysis/complete-package-v16-hair-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
