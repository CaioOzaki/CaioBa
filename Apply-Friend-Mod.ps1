param([string]$GameDirectory='', [switch]$Restore)
$ErrorActionPreference='Stop'
try {
    if(Get-Process -Name VolleyballFever -ErrorAction SilentlyContinue){throw 'Feche o Volleyball Fever antes de continuar.'}
    $config=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'patch.json') -Raw | ConvertFrom-Json
    if(-not $GameDirectory){
        $libraries=@('C:\APPS\STEAM','C:\Program Files (x86)\Steam')
        $steam=(Get-ItemProperty -LiteralPath 'HKCU:\Software\Valve\Steam' -ErrorAction SilentlyContinue).SteamPath
        if($steam){
            $libraries+= $steam
            $vdf=Join-Path $steam 'steamapps\libraryfolders.vdf'
            if(Test-Path -LiteralPath $vdf){
                $matchesFound=[regex]::Matches([IO.File]::ReadAllText($vdf),'"path"\s+"([^"]+)"')
                foreach($match in $matchesFound){$libraries+=$match.Groups[1].Value.Replace('\\','\')}
            }
        }
        foreach($library in ($libraries | Select-Object -Unique)){
            $candidate=Join-Path $library 'steamapps\common\Volleyball'
            if(Test-Path -LiteralPath (Join-Path $candidate 'VolleyballFever.exe')){$GameDirectory=$candidate;break}
        }
        if(-not $GameDirectory){$GameDirectory=Read-Host 'Cole o caminho da pasta do jogo (Steam > Gerenciar > Explorar arquivos locais)'}
    }
    $game=(Resolve-Path -LiteralPath $GameDirectory).Path
    if(-not (Test-Path -LiteralPath (Join-Path $game 'VolleyballFever.exe'))){throw 'Esta pasta nao contem VolleyballFever.exe.'}
    $target=Join-Path $game 'GameAssembly.dll'
    $backup=Join-Path $game 'GameAssembly.dll.antes-CaioBa-v10'
    $current=(Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
    if($Restore){
        if(-not (Test-Path -LiteralPath $backup)){throw 'Backup anterior ao mod nao encontrado.'}
        if((Get-FileHash -LiteralPath $backup -Algorithm SHA256).Hash.ToLowerInvariant() -ne $config.original_sha256){throw 'O backup nao corresponde ao original esperado.'}
        if($current -ne $config.modified_sha256 -and $current -ne $config.original_sha256){throw 'O jogo foi alterado depois deste mod. Restauracao interrompida.'}
        Copy-Item -LiteralPath $backup -Destination $target -Force
        Write-Host 'Jogo original restaurado.'
        exit 0
    }
    if($current -eq $config.modified_sha256){Write-Host 'Esta versao do mod ja esta instalada.';exit 0}
    if($current -ne $config.original_sha256){throw 'Versao diferente da esperada. Este pacote exige o jogo original da Steam, build 9216628, sem outro mod de codigo. Nenhum arquivo foi alterado.'}
    $patch=Join-Path $PSScriptRoot 'changes.bin'
    if((Get-FileHash -LiteralPath $patch -Algorithm SHA256).Hash.ToLowerInvariant() -ne $config.patch_sha256){throw 'Pacote incompleto ou alterado. Extraia novamente o ZIP.'}
    $bytes=[IO.File]::ReadAllBytes($target)
    $stream=[IO.File]::OpenRead($patch)
    $reader=New-Object IO.BinaryReader($stream)
    $out=New-Object IO.MemoryStream
    try {
        $length=$reader.ReadInt64();$count=$reader.ReadInt32()
        if($length -lt 1 -or $length -gt 100MB -or $count -lt 1 -or $count -gt 10000){throw 'Cabecalho de patch invalido.'}
        $out.Write($bytes,0,$bytes.Length);$out.SetLength($length)
        for($i=0;$i -lt $count;$i++){
            $offset=$reader.ReadInt64();$size=$reader.ReadInt32()
            if($offset -lt 0 -or $size -lt 0 -or $offset+$size -gt $length){throw 'Bloco de patch invalido.'}
            $block=$reader.ReadBytes($size);if($block.Length -ne $size){throw 'Patch truncado.'}
            $out.Position=$offset;$out.Write($block,0,$size)
        }
        if($stream.Position -ne $stream.Length){throw 'Dados inesperados no patch.'}
        $updated=$out.ToArray()
    } finally {$reader.Dispose();$out.Dispose()}
    $sha=[Security.Cryptography.SHA256]::Create()
    try {$hash=([BitConverter]::ToString($sha.ComputeHash($updated))).Replace('-','').ToLowerInvariant()} finally {$sha.Dispose()}
    if($hash -ne $config.modified_sha256){throw 'Falha na verificacao do resultado. Nenhum arquivo foi instalado.'}
    if(Test-Path -LiteralPath $backup){
        if((Get-FileHash -LiteralPath $backup -Algorithm SHA256).Hash.ToLowerInvariant() -ne $config.original_sha256){throw 'Ja existe um backup diferente. Nao sera sobrescrito.'}
    }else{Copy-Item -LiteralPath $target -Destination $backup}
    $staged=Join-Path $game 'GameAssembly.dll.CaioBa-v10-novo'
    [IO.File]::WriteAllBytes($staged,$updated)
    try {
        Move-Item -LiteralPath $staged -Destination $target -Force
        if((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $config.modified_sha256){throw 'Falha na verificacao da instalacao.'}
    } catch {Copy-Item -LiteralPath $backup -Destination $target -Force;throw}
    Write-Host 'Mod 2v2 online instalado. Todos precisam da mesma versao. Abra pela Steam.'
} catch {Write-Host $_.Exception.Message;exit 1}
