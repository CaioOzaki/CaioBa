param(
    [ValidateSet('Full','SkinOnly','Restore')][string]$Mode='Full',
    [string]$GameDirectory='C:\APPS\STEAM\steamapps\common\Volleyball'
)
$ErrorActionPreference='Stop'
$packageRoot=$PSScriptRoot
$expectedGameDirectory='C:\APPS\STEAM\steamapps\common\Volleyball'
$resolvedGameDirectory=(Resolve-Path -LiteralPath $GameDirectory).Path.TrimEnd('\')
if($resolvedGameDirectory -ne $expectedGameDirectory){throw 'Este pacote foi preparado apenas para a instalação de Volleyball Fever indicada.'}
if(Get-Process -Name VolleyballFever -ErrorAction SilentlyContinue){throw 'Feche Volleyball Fever antes de instalar ou restaurar.'}
$manifest=Get-Content -LiteralPath (Join-Path $packageRoot 'analysis\native-patch-manifest.json') -Raw | ConvertFrom-Json
$textureManifest=Get-Content -LiteralPath (Join-Path $packageRoot 'analysis\texture-patch-manifest.json') -Raw | ConvertFrom-Json
$items=@(
    @{Relative='GameAssembly.dll';Backup='backup\GameAssembly.dll';Modified=$manifest.modified_sha256},
    @{Relative='VolleyballFever_Data\resources.assets';Backup='backup\resources.assets';Modified=$textureManifest.sha256}
)
foreach($item in $items){
    $item.Target=Join-Path $resolvedGameDirectory $item.Relative
    $item.Original=Join-Path $packageRoot $item.Backup
    $item.OriginalHash=(Get-FileHash -LiteralPath $item.Original -Algorithm SHA256).Hash
    $currentHash=(Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash
    $knownPrevious=($item.Relative -eq 'GameAssembly.dll' -and $currentHash -in @('b3a0e92b6409faf2697d439ff99c8578ce18c0eb75d0bb35480968107e59b875','0be21d448ab8b0cbef18e7ce9781b7d6c958247061e0494204206b8d0bef0930','7d22efcb0b59ae49ae3bf676e721488a44f19077f64d0397737c204256b78551','d754fea0bb42e2820b944f5c7d48e39bb79af39bd167997970ea7e792dc63706','cc2f6898b03d27534d7b904452d79d5b333df281ff266d4508f5303880530ecc','9869d7e673e893e3887fdae4fc44956f32a25838bf66a4ceb374cec0a7299826','9ee0d8fb9e6e7851fe46266006d96b4de5e8d528e21f32b33f478ca88eb5862c','727b2aabfc1658b295bf38b35611a272305b5e189a0e3773429c9024589dfa60'))
    if($currentHash -ne $item.OriginalHash -and $currentHash -ne $item.Modified -and -not $knownPrevious){throw "Arquivo diferente da versão examinada: $($item.Relative). Nada foi instalado."}
    $useMod=($Mode -eq 'Full' -or ($Mode -eq 'SkinOnly' -and $item.Relative -ne 'GameAssembly.dll'))
    $item.Source=if($useMod){Join-Path $packageRoot (Join-Path 'working' $item.Relative)}else{$item.Original}
    $item.Expected=if($useMod){$item.Modified}else{$item.OriginalHash}
    if((Get-FileHash -LiteralPath $item.Source -Algorithm SHA256).Hash -ne $item.Expected){throw 'O pacote foi alterado; instalação interrompida.'}
}
$touched=@()
$rollbackDirectory=Join-Path $packageRoot ('backups\install-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
New-Item -ItemType Directory -Path $rollbackDirectory | Out-Null
foreach($item in $items){
    $item.Rollback=Join-Path $rollbackDirectory ([IO.Path]::GetFileName($item.Target))
    Copy-Item -LiteralPath $item.Target -Destination $item.Rollback
    if((Get-FileHash -LiteralPath $item.Rollback -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash){throw 'Falha ao preparar a cópia de segurança da instalação.'}
}
try{
    foreach($item in $items){
        Copy-Item -LiteralPath $item.Source -Destination ($item.Target+'.vfmod-new')
    }
    foreach($item in $items){
        Move-Item -LiteralPath ($item.Target+'.vfmod-new') -Destination $item.Target -Force
        $touched+=$item
        if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash -ne $item.Expected){throw 'Falha na conferência do arquivo instalado.'}
    }
}catch{
    foreach($item in $touched){Copy-Item -LiteralPath $item.Rollback -Destination $item.Target -Force}
    throw
}finally{
    foreach($item in $items){if(Test-Path -LiteralPath ($item.Target+'.vfmod-new')){Remove-Item -LiteralPath ($item.Target+'.vfmod-new')}}
}
$record=[ordered]@{mode=$Mode;time=(Get-Date).ToString('o');game=$resolvedGameDirectory;files=@($items|ForEach-Object{@{file=$_.Relative;sha256=$_.Expected}});runtimeTested=$false}
$record|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $packageRoot 'installation-status.json')
Write-Output "Concluído: $Mode. Os dois arquivos foram conferidos por SHA-256. Originais preservados em $packageRoot\backup."




