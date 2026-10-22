param([switch]$Restore)
$ErrorActionPreference='Stop'
if(Get-Process VolleyballFever -ErrorAction SilentlyContinue){throw 'Feche o jogo antes de instalar.'}
$game='C:\APPS\STEAM\steamapps\common\Volleyball\VolleyballFever_Data'
$manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'maps-v12\manifest.json') -Raw | ConvertFrom-Json
$items=@()
foreach($f in $manifest.files){
 $target=Join-Path $game $f.name
 $source=Join-Path $PSScriptRoot ($(if($Restore){'versions\v11-praia-estavel\'}else{'maps-v12\'})+$f.name)
 $expected=if($Restore){$f.before_sha256}else{$f.sha256}
 if((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -notin @($f.sha256,$f.before_sha256)){throw "Arquivo inesperado: $($f.name)"}
 if((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $expected){throw 'Pacote alterado.'}
 $items+=@{Target=$target;Source=$source;Expected=$expected;Name=$f.name}
}
$backup=Join-Path $PSScriptRoot ('backups\praia-v12-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
New-Item -ItemType Directory -Path $backup | Out-Null
foreach($i in $items){Copy-Item -LiteralPath $i.Target -Destination (Join-Path $backup $i.Name)}
$done=@()
try{
 foreach($i in $items){
  Copy-Item -LiteralPath $i.Source -Destination ($i.Target+'.caioba-new')
  Move-Item -LiteralPath ($i.Target+'.caioba-new') -Destination $i.Target -Force
  $done+=$i
  if((Get-FileHash -LiteralPath $i.Target -Algorithm SHA256).Hash -ne $i.Expected){throw 'Falha na verificacao do arquivo instalado.'}
 }
}catch{
 foreach($i in $done){Copy-Item -LiteralPath (Join-Path $backup $i.Name) -Destination $i.Target -Force}
 throw
}
foreach($i in $items){Copy-Item -LiteralPath $i.Source -Destination (Join-Path $PSScriptRoot ('working\VolleyballFever_Data\'+$i.Name)) -Force}
@{installed=(-not $Restore);backup=$backup;time=(Get-Date).ToString('o');smokeTested=$true;vrMatchTested=$false}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $PSScriptRoot 'maps-v12\installation.json')
Write-Output 'Praia v12 instalada e arquivos conferidos. Backup preservado.'
