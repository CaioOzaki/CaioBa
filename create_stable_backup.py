from pathlib import Path
import hashlib, json, zipfile, datetime
from zoneinfo import ZoneInfo

root=Path(__file__).resolve().parent
game=Path(r'C:\APPS\STEAM\steamapps\common\Volleyball')
out=root/'backups';out.mkdir(exist_ok=True)
now=datetime.datetime.now(ZoneInfo('America/Sao_Paulo'))
name='VolleyballFever_BACKUP_estavel_antes_2v2_'+now.strftime('%Y-%m-%d_%H-%M-%S')
archive=out/(name+'.zip')
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
files=sorted(p for p in game.rglob('*') if p.is_file())
assert files and (game/'GameAssembly.dll').is_file()
entries=[{'path':p.relative_to(game).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
installed=json.loads((root/'installation-status.json').read_text(encoding='utf-8-sig'))
for item in installed['files']:
    assert sha(game/item['file'])==item['sha256'],f"Installed version differs: {item['file']}"
manifest={'created':now.isoformat(),'description':'Estado atual aprovado pelo usuário, antes de qualquer alteração 2v2. Aparência Mikasa e física otimizada v2.','source':str(game),'files':entries,'file_count':len(entries),'total_bytes':sum(e['bytes'] for e in entries)}
restore=r'''$ErrorActionPreference='Stop'
$gameDirectory='C:\APPS\STEAM\steamapps\common\Volleyball'
$backupDirectory=Join-Path $PSScriptRoot 'Jogo'
if(Get-Process -Name VolleyballFever -ErrorAction SilentlyContinue){throw 'Feche o jogo antes de restaurar.'}
if(-not(Test-Path -LiteralPath (Join-Path $backupDirectory 'VolleyballFever.exe'))){throw 'Extraia o ZIP inteiro antes de executar este arquivo.'}
$manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifesto.json') -Raw|ConvertFrom-Json
$sourceRoot=(Resolve-Path -LiteralPath $backupDirectory).Path
foreach($entry in $manifest.files){
    $sourceFile=[IO.Path]::GetFullPath((Join-Path $sourceRoot $entry.path))
    if(-not $sourceFile.StartsWith($sourceRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Caminho inválido no manifesto.'}
    if((Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash -ne $entry.sha256){throw "Backup inválido: $($entry.path)"}
}
$parentDirectory=[IO.Path]::GetFullPath('C:\APPS\STEAM\steamapps\common')
$targetDirectory=[IO.Path]::GetFullPath($gameDirectory)
if($targetDirectory -ne (Join-Path $parentDirectory 'Volleyball')){throw 'Destino inesperado.'}
$savedDirectory=Join-Path $parentDirectory ('Volleyball_antes_da_restauracao_'+(Get-Date -Format 'yyyyMMdd_HHmmss'))
if(Test-Path -LiteralPath $savedDirectory){throw 'Já existe uma pasta de preservação com esse nome.'}
if(Test-Path -LiteralPath $targetDirectory){
    if((Resolve-Path -LiteralPath $targetDirectory).Path -ne $targetDirectory){throw 'Destino não corresponde à pasta esperada.'}
    Move-Item -LiteralPath $targetDirectory -Destination $savedDirectory
    Write-Output "Instalação anterior preservada em: $savedDirectory"
}
Copy-Item -LiteralPath $sourceRoot -Destination $targetDirectory -Recurse
foreach($entry in $manifest.files){
    $targetFile=Join-Path $targetDirectory $entry.path
    if((Get-FileHash -LiteralPath $targetFile -Algorithm SHA256).Hash -ne $entry.sha256){throw "Falha na restauração: $($entry.path). A instalação anterior continua preservada."}
}
Write-Output 'Restaurado o estado estável com Mikasa e física otimizada. Abra pela Steam normalmente.'
'''
readme='''BACKUP ESTÁVEL — VOLLEYBALL FEVER — ANTES DO 2v2

Este arquivo contém a instalação COMPLETA do jogo no estado aprovado pelo usuário,
com aparência Mikasa Beach Pro adaptada e física otimizada v2.
Não contém alterações para o modo 2v2.

RESTAURAÇÃO
1. Feche o jogo.
2. Extraia TODO o ZIP para uma pasta.
3. Dê dois cliques em RESTAURAR.cmd na pasta extraída.
4. Abra o jogo pela Steam normalmente.

O restaurador confere todos os arquivos e preserva a instalação que estiver no
computador em uma pasta vizinha antes de colocar este estado no lugar.
Se surgir erro de acesso, execute RESTAURAR.cmd como administrador.
Não é necessário recompilar nem editar arquivos do jogo.

CONTEÚDO
Jogo/ — instalação completa pronta para restauração.
manifesto.json — lista de arquivos, tamanhos e hashes SHA-256.
Fontes-do-mod/ — fontes e documentação das alterações, para referência.

Este backup cobre os arquivos da instalação. Configurações externas do Windows,
Steam, Quest Link e saves fora da instalação não são incluídos nem alterados
pelo restaurador. Uso pessoal; contém arquivos proprietários do jogo.
'''
sources=['spin_mod.c','build_patch.py','make_texture.py','apply_texture.py','render_preview.py','test_physics.py','test_hooks.py','LEIA-ME.md','installation-status.json','analysis/native-patch-manifest.json','analysis/texture-patch-manifest.json','analysis/physics-test-results.json','analysis/hook-test-results.json','assets/Mikasa-BV550C-atlas.svg','assets/Mikasa-BV550C-atlas.png']
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for p,e in zip(files,entries):z.write(p,'Jogo/'+e['path'])
    z.writestr('manifesto.json',json.dumps(manifest,ensure_ascii=False,indent=2))
    z.writestr('LEIA-ME.txt',readme)
    z.writestr('RESTAURAR.ps1',restore.encode('utf-8-sig'))
    z.writestr('RESTAURAR.cmd','@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0RESTAURAR.ps1"\r\npause\r\n')
    for f in sources:
        p=root/f
        if p.is_file():z.write(p,'Fontes-do-mod/'+f)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for p,e in zip(files,entries):
        with z.open('Jogo/'+e['path']) as f:
            h=hashlib.sha256()
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        assert h.hexdigest()==e['sha256']
        assert sha(p)==e['sha256'],f'Source changed during backup: {p}'
result={'archive':str(archive),'sha256':sha(archive),'bytes':archive.stat().st_size,'game_files':len(entries),'source_bytes':manifest['total_bytes'],'verified':'All archived game files match source SHA-256; ZIP CRC verified.'}
(out/'latest-backup.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2),flush=True)
