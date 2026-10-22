import pathlib,json,struct,hashlib,zipfile,shutil
R=pathlib.Path(__file__).resolve().parent
out=R/'distribution'/'CaioBa-2v2-v10';out.mkdir(parents=True,exist_ok=True)
original=(R/'backup/GameAssembly.dll').read_bytes();updated=(R/'working/GameAssembly.dll').read_bytes()
chunks=[]
for offset in range(0,len(updated),4096):
 data=updated[offset:offset+4096]
 if data!=original[offset:offset+len(data)]:chunks.append((offset,data))
patch=struct.pack('<qi',len(updated),len(chunks))+b''.join(struct.pack('<qi',offset,len(data))+data for offset,data in chunks)
(out/'changes.bin').write_bytes(patch)
h=lambda b:hashlib.sha256(b).hexdigest()
config={'version':'CaioBa-2v2-v10','steam_build':9216628,'original_sha256':h(original),'modified_sha256':h(updated),'patch_sha256':h(patch)}
(out/'patch.json').write_text(json.dumps(config,indent=2))
shutil.copyfile(R/'Apply-Friend-Mod.ps1',out/'Aplicar-mod.ps1')
for name,flag in [('Instalar.cmd',''),('Restaurar.cmd',' -Restore')]:
 (out/name).write_text('@echo off\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Aplicar-mod.ps1"'+flag+'\npause\n')
(out/'LEIA-ME.txt').write_text('''CaioBa 2v2 online - v10 experimental

Este pacote contem apenas alteracoes. Cada pessoa precisa de sua propria
instalacao do Volleyball Fever na Steam, build 9216628. Nao inclui o jogo.

1. Feche o jogo e extraia todo o ZIP para uma pasta.
2. Execute Instalar.cmd. Ele encontra a pasta Steam ou pergunta o caminho.
3. Todos devem instalar este mesmo pacote e abrir o jogo pela Steam.
4. Nas configuracoes do jogo, escolham a mesma regiao online.
5. Em Online, todos escolhem o mesmo formato: 4v4 ou 2v2.
   Uma pessoa usa Criar sala; as outras usam Entrar na sala.
6. Escolham os times (no maximo dois humanos por lado) e fiquem prontos.

No 2v2 ha quatro vagas totais: dois por time. Com 2 ou 3 humanos, bots completam
as vagas livres. Dois amigos podem jogar juntos contra dois bots, ou um
de cada lado com um bot por time. Com 4 humanos, nao ha bots.

Velocidade humana no 2v2: +60%, tanto Solo quanto Online.
O 4v4 Solo em cruz permanece. O Online tambem oferece o 4v4 original,
com bots completando os times e o limite original de quatro humanos.
As salas usam versoes Photon separadas: CaioBa-2v2-v10 e CaioBa-4v4-v10.
Os formatos nao se misturam e as salas nao aparecem para o jogo
sem mod nem para outras versoes. Isso nao e uma senha privada: outra
pessoa com o mesmo pacote e regiao tambem pode encontrar a sala.
Nao precisa de Hamachi. O servico Photon original continua sendo usado.

A recepcao assistida vale no primeiro toque do saque adversario, para os
dois times. Os bots aliados seguem a tatica de tres toques e sem bloqueio.
O saque na mao funciona segurando o gatilho de qualquer uma das maos.
As alteracoes experimentais de spin continuam limitadas ao Solo.
Este pacote nao troca texturas e nao remove verificacoes da Steam.

Validacao: testes automatizados de codigo compilado com servicos Photon
e Unity simulados. Ainda NAO validado em uma partida real entre dois PCs
com headsets. Testem primeiro uma sala com dois amigos antes de quatro.

Para remover: feche o jogo e execute Restaurar.cmd. O instalador guarda
GameAssembly.dll.antes-CaioBa-v10 na pasta do jogo.
''',encoding='utf-8')
# Verify reconstruction independently of the installer before packaging.
reconstructed=bytearray(original);reconstructed.extend(b'\0'*max(0,len(updated)-len(reconstructed)))
del reconstructed[len(updated):]
for offset,data in chunks:reconstructed[offset:offset+len(data)]=data
assert bytes(reconstructed)==updated
archive=R/'distribution'/'CaioBa-2v2-online-v10.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for file in sorted(out.iterdir()):z.write(file,'CaioBa-2v2-v10/'+file.name)
print(json.dumps({'zip':str(archive),'bytes':archive.stat().st_size,'blocks':len(chunks),'target_sha256':h(updated),'reconstruction_verified':True},indent=2))
