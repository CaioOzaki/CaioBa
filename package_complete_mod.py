import hashlib,json,pathlib,struct,zipfile,subprocess,shutil
R=pathlib.Path(__file__).resolve().parent
OUT=R/'distribution/Caioba-completo-v12'
OUT.mkdir(parents=True,exist_ok=True)
H=lambda data: hashlib.sha256(data).hexdigest()
names=['GameAssembly.dll']+['VolleyballFever_Data/'+n for n in ['resources.assets','level1','level2','level3','sharedassets1.assets','sharedassets3.assets']]
def original_path(name):
    basename=pathlib.Path(name).name
    return R/('backup' if basename in ['GameAssembly.dll','resources.assets'] else 'versions/v10-antes-mapas')/basename
def delta(src,dst):
    blocks=[(i,dst[i:i+4096]) for i in range(0,len(dst),4096) if src[i:i+4096]!=dst[i:i+4096]]
    result=bytearray(src[:len(dst)]);result.extend(bytes(max(0,len(dst)-len(result))))
    for offset,data in blocks:result[offset:offset+len(data)]=data
    assert result==dst
    return struct.pack('<qi',len(dst),len(blocks))+b''.join(struct.pack('<qi',i,len(data))+data for i,data in blocks)
manifest={'version':'Caioba-completo-v12','steam_build':9216628,'files':[]}
for i,name in enumerate(names):
    src=original_path(name).read_bytes();dst=(R/'working'/name).read_bytes()
    installed=(pathlib.Path('C:/APPS/STEAM/steamapps/common/Volleyball')/name).read_bytes()
    assert H(installed)==H(dst),f'Installed mismatch: {name}'
    record={'path':name,'original_sha256':H(src),'modified_sha256':H(dst)}
    for direction,a,b in [('forward',src,dst),('reverse',dst,src)]:
        patch=delta(a,b);filename=f'{i}-{direction}.bin'
        (OUT/filename).write_bytes(patch)
        record[direction]={'name':filename,'sha256':H(patch)}
    manifest['files'].append(record)
(OUT/'patch.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(OUT/'Aplicar-mod.ps1').write_text((R/'Apply-Complete-Mod.ps1').read_text(encoding='utf-8'),encoding='utf-8-sig')
for name,flag in [('Instalar.cmd',''),('Restaurar.cmd',' -Restore')]:
    (OUT/name).write_text('@echo off\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Aplicar-mod.ps1"'+flag+'\npause\n',encoding='ascii')
(OUT/'LEIA-ME.txt').write_text('''CAIOBA COMPLETO v12 - mod para Volleyball Fever

COMO INSTALAR
1. Cada jogador precisa ter o Volleyball Fever instalado pela Steam.
   Este ZIP contem alteracoes, nao inclui o jogo. Build compativel: 9216628.
2. Feche o jogo. Extraia TODO o ZIP para uma pasta e execute Instalar.cmd.
3. O instalador encontra a pasta Steam ou pede o caminho. Se houver outra
   versao ou mod desconhecido, interrompe antes de alterar os arquivos.
4. Abra o jogo pela Steam com seu headset e SteamVR configurados.

COMO JOGAR JUNTOS
Todos devem instalar este mesmo pacote. Nas configuracoes do jogo,
escolham a mesma regiao online. Em Online, escolham o mesmo modo (2v2
ou 4v4). Um cria a sala; os outros entram nela e escolhem os times.
No 2v2 cabem ate quatro humanos, dois por lado; bots completam as vagas.
No 4v4 permanece o limite original de quatro humanos, com bots completando.
O servico Photon do jogo continua sendo utilizado. Nao precisa de Hamachi.
As salas de 2v2 e 4v4 ficam separadas; isto nao equivale a uma senha privada.

CONTEUDO
Modo 2v2 Solo e Online, menus de selecao, ajustes de movimentacao e bots,
recepcao de saque assistida e saque na mao com gatilho; ajustes de regras.
Indoor Caioba, marcacoes de quadra, teto alto, postes quadrados, rede
e bola Mikasa. Praia nova nas versoes dia e noite, com dunas e nova costa.
Este pacote substitui o ZIP antigo que continha apenas o mod de codigo.
Aceita arquivos originais ou os desta versao, inclusive a DLL do v10.

COMO RESTAURAR
Feche o jogo e execute Restaurar.cmd da mesma pasta extraida.
Restaura os sete arquivos modificados ao original compativel, inclusive
as texturas. Nao apaga saves. Cada operacao preserva copias anteriores
em uma pasta Caioba-backup dentro da pasta do jogo.
Nao apague esses backups enquanto estiver testando. Nao misture pacotes.
Uma atualizacao ou verificacao de arquivos da Steam pode remover o mod.

VALIDACAO E LIMITES
Instalacao, repeticao da instalacao e restauracao testadas em copia local.
Integridade dos sete arquivos comparada com o jogo modado atual.
As praias dia/noite abriram em teste de inicializacao do executavel.
Ainda falta validar uma partida VR completa nos mapas e uma sessao
online real entre dois PCs. O multiplayer modado continua experimental.
Se a sala nao aparecer, confiram pacote, modo e regiao iguais.
''',encoding='utf-8-sig')

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
# Upgrade from previous DLL-only package.
shutil.copyfile(R/'working/GameAssembly.dll',fixture/'GameAssembly.dll')
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
archive=R/'distribution/Caioba-completo-v12.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in sorted(OUT.iterdir()):z.write(file,'Caioba-completo-v12/'+file.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
report={'zip':str(archive),'bytes':archive.stat().st_size,'sha256':H(archive.read_bytes()),'files':len(names),'checks':results}
(R/'analysis/complete-package-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
