param([string]$GameDirectory='', [switch]$Restore)
$ErrorActionPreference='Stop'
function Hash($path) {
    $stream=[IO.File]::OpenRead($path); $sha=[Security.Cryptography.SHA256]::Create()
    try { ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','').ToLowerInvariant() }
    finally {$stream.Dispose();$sha.Dispose()}
}
function ApplyDelta($source,$patch,$destination) {
    $reader=[IO.BinaryReader]::new([IO.File]::OpenRead($patch))
    $output=[IO.MemoryStream]::new()
    try {
        $length=$reader.ReadInt64(); $count=$reader.ReadInt32()
        if($length -lt 1 -or $length -gt 200MB -or $count -lt 0 -or $count -gt 60000){throw 'Patch invalido.'}
        $bytes=[IO.File]::ReadAllBytes($source)
        $output.Write($bytes,0,$bytes.Length); $output.SetLength($length)
        for($i=0;$i -lt $count;$i++){
            $offset=$reader.ReadInt64(); $size=$reader.ReadInt32()
            if($offset -lt 0 -or $size -lt 1 -or $size -gt 4096 -or $offset+$size -gt $length){throw 'Bloco invalido.'}
            $block=$reader.ReadBytes($size)
            if($block.Length -ne $size){throw 'Patch incompleto.'}
            $output.Position=$offset; $output.Write($block,0,$size)
        }
        if($reader.BaseStream.Position -ne $reader.BaseStream.Length){throw 'Patch com dados extras.'}
        [IO.File]::WriteAllBytes($destination,$output.ToArray())
    } finally { $reader.Dispose(); $output.Dispose() }
}
$stage=$null
try {
    if(Get-Process -Name VolleyballFever -ErrorAction SilentlyContinue){throw 'Feche o jogo antes de continuar.'}
    $config=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'patch.json') -Raw | ConvertFrom-Json
    if(-not $GameDirectory){
        $libraries=@('C:\APPS\STEAM','C:\Program Files (x86)\Steam')
        $steam=(Get-ItemProperty -LiteralPath 'HKCU:\Software\Valve\Steam' -ErrorAction SilentlyContinue).SteamPath
        if($steam){$libraries+=$steam}
        foreach($library in @($libraries)){
            $vdf=Join-Path $library 'steamapps\libraryfolders.vdf'
            if(Test-Path -LiteralPath $vdf){
                foreach($m in [regex]::Matches([IO.File]::ReadAllText($vdf),'"path"\s+"([^"]+)"')){$libraries+=$m.Groups[1].Value.Replace('\\','\')}
            }
        }
        foreach($library in ($libraries | Select-Object -Unique)){
            $candidate=Join-Path $library 'steamapps\common\Volleyball'
            if(Test-Path -LiteralPath (Join-Path $candidate 'VolleyballFever.exe')){$GameDirectory=$candidate;break}
        }
        if(-not $GameDirectory){$GameDirectory=Read-Host 'Cole a pasta do jogo (Steam > Gerenciar > Explorar arquivos locais)'}
    }
    $game=(Resolve-Path -LiteralPath $GameDirectory).Path
    if(-not (Test-Path -LiteralPath (Join-Path $game 'VolleyballFever.exe'))){throw 'Pasta do jogo incorreta.'}
    $required=@('GameAssembly.dll','VolleyballFever_Data/resources.assets','VolleyballFever_Data/level1','VolleyballFever_Data/level2','VolleyballFever_Data/level3','VolleyballFever_Data/sharedassets1.assets','VolleyballFever_Data/sharedassets3.assets','VolleyballFever_Data/sharedassets0.assets','VolleyballFever_Data/level0')
    $allowed=$required+@('VolleyballFever_Data/globalgamemanagers.assets')
    if($config.version -in @('Cloudcourt-v18-praia-lobby','Cloudcourt-v19-customizacao','Cloudcourt-v20-personagens-menu','Cloudcourt-v20-1-middle-part','Cloudcourt-v21-orla-gestos','Cloudcourt-v22-correcoes','Cloudcourt-v23-maos-audio','Cloudcourt-v24-celebracao-graficos','Cloudcourt-v25-trigger-fix','Cloudcourt-v26-session-repair','Cloudcourt-v27-avatar-elbow','Cloudcourt-v28-extras-customization')){
        $required+=@('VolleyballFever_Data/globalgamemanagers.assets','VolleyballFever_Data/sharedassets2.assets','VolleyballFever_Data/sharedassets4.assets','VolleyballFever_Data/resources.resource','VolleyballFever_Data/sharedassets0.resource','VolleyballFever_Data/sharedassets1.resource','VolleyballFever_Data/sharedassets2.resource','VolleyballFever_Data/sharedassets4.resource')
        $allowed=$required
        if($config.files.Count -ne 17){throw 'Manifesto de 17 arquivos incompleto.'}
    } elseif($config.files.Count -notin @(9,10)){throw 'Manifesto incompleto.'}
    $seen=@{}; $jobs=@()
    foreach($f in $config.files){
        if($f.path -notin $allowed -or $seen.ContainsKey($f.path)){throw 'Caminho invalido no manifesto.'}
        $seen[$f.path]=$true
        $target=Join-Path $game $f.path
        $current=Hash $target
        if($current -ne $f.original_sha256 -and $current -ne $f.modified_sha256 -and $current -ne $f.previous_sha256){throw "Arquivo incompatível: $($f.path). Use a versao original Steam build 9216628. Nenhum arquivo do jogo foi alterado."}
        $desired=$f.modified_sha256; $delta=$f.forward
        if($Restore){$desired=$f.original_sha256; $delta=$f.reverse}
        if($f.previous_sha256 -and $current -eq $f.previous_sha256){
            $delta=$f.upgrade
            if($Restore){$delta=$f.previous_reverse}
        }
        if($current -eq $desired){continue}
        if($delta.name -notmatch '^\d+-(forward|reverse)\.bin$'){throw 'Nome de patch invalido.'}
        $patch=Join-Path $PSScriptRoot $delta.name
        if((Hash $patch) -ne $delta.sha256){throw 'Pacote corrompido. Extraia novamente o ZIP.'}
        $jobs+=@{target=$target;patch=$patch;desired=$desired;prior=$current;relative=$f.path}
    }
    foreach($path in $required){if(-not $seen.ContainsKey($path)){throw 'Manifesto incompleto.'}}
    if($jobs.Count -eq 0){Write-Host 'Os arquivos ja estao na versao solicitada.';exit 0}
    $stage=Join-Path $game ('Caioba-backup-'+[Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $stage | Out-Null
    $index=0
    foreach($job in $jobs){
        $job.new=Join-Path $stage "$index.new"; $job.backup=Join-Path $stage "$index.before"
        Copy-Item -LiteralPath $job.target -Destination $job.backup
        ApplyDelta $job.backup $job.patch $job.new
        if((Hash $job.new) -ne $job.desired -or (Hash $job.backup) -ne $job.prior){throw 'Falha ao preparar arquivos. O jogo permanece intacto.'}
        $index++
    }
    $jobs | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $stage 'recovery.json') -Encoding UTF8
    $changed=@()
    try {
        foreach($job in $jobs){
            if((Hash $job.target) -ne $job.prior){throw 'Arquivo alterado durante a instalacao.'}
            $changed+=,$job
            Copy-Item -LiteralPath $job.new -Destination $job.target -Force
            if((Hash $job.target) -ne $job.desired){throw 'Falha na verificacao da copia.'}
        }
    } catch {
        $cause=$_; $failed=@()
        foreach($job in $changed){
            try { Copy-Item -LiteralPath $job.backup -Destination $job.target -Force; if((Hash $job.target) -ne $job.prior){throw 'hash'} }
            catch {$failed+=$job.relative}
        }
        if($failed.Count){throw "Falha ao recuperar: $failed. Backups preservados em $stage"}
        throw "Instalacao cancelada; estado anterior recuperado. $cause"
    }
    foreach($job in $jobs){Remove-Item -LiteralPath $job.new}
    if($Restore){Write-Host 'Os arquivos originais do pacote foram restaurados.'}
    else {Write-Host "Cloudcourt VR: $($config.version) instalado. Abra o jogo pela Steam."}
    Write-Host "Backup da operacao: $stage"
} catch {Write-Host $_.Exception.Message; exit 1}
