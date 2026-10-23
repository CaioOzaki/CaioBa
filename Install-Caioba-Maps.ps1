param([switch]$Restore)
$ErrorActionPreference='Stop'
$game='C:\APPS\STEAM\steamapps\common\Volleyball'
if(Get-Process -Name VolleyballFever -ErrorAction SilentlyContinue){throw 'Feche o jogo antes de aplicar os mapas.'}
$manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'maps-v11\manifest.json') -Raw | ConvertFrom-Json
$items=@()
foreach($item in $manifest.files){
 $target=Join-Path $game ('VolleyballFever_Data\'+$item.name)
 $source=if($Restore){Join-Path $PSScriptRoot ('versions\v10-antes-mapas\'+$item.name)}else{Join-Path $PSScriptRoot ('maps-v11\'+$item.name)}
 $expected=if($Restore){$item.before_sha256}else{$item.sha256}
 $current=(Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
 $allowed=@($item.sha256,$item.before_sha256)
 $fixManifest=Join-Path $PSScriptRoot 'versions\v11-antes-correcao\manifest.json'
 if(Test-Path -LiteralPath $fixManifest){$fix=Get-Content -LiteralPath $fixManifest -Raw | ConvertFrom-Json; $allowed+=@($fix.files | Where-Object name -eq $item.name | ForEach-Object sha256)}
 $previousManifest=Join-Path $PSScriptRoot 'versions\v11-antes-linhas-praia\manifest.json'
 if(Test-Path -LiteralPath $previousManifest){
  $previous=Get-Content -LiteralPath $previousManifest -Raw | ConvertFrom-Json
  $allowed+=@($previous.files | Where-Object name -eq $item.name | ForEach-Object sha256)
 }
 if($current -notin $allowed){throw "Arquivo diferente do examinado: $($item.name)."}
 if((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $expected){throw 'Pacote invalido.'}
 $items+=@{Target=$target;Source=$source;Expected=$expected;Name=$item.name}
}
$backup=Join-Path $PSScriptRoot ('backups\maps-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
New-Item -ItemType Directory -Path $backup | Out-Null
foreach($i in $items){Copy-Item -LiteralPath $i.Target -Destination (Join-Path $backup $i.Name)}
$touched=@()
try{
 foreach($i in $items){
  Copy-Item -LiteralPath $i.Source -Destination ($i.Target+'.caioba-new')
  Move-Item -LiteralPath ($i.Target+'.caioba-new') -Destination $i.Target -Force
  $touched+=$i
  if((Get-FileHash -LiteralPath $i.Target -Algorithm SHA256).Hash -ne $i.Expected){throw 'Falha na verificacao.'}
 }
}catch{
 foreach($i in $touched){Copy-Item -LiteralPath (Join-Path $backup $i.Name) -Destination $i.Target -Force}
 throw
}
foreach($i in $items){Copy-Item -LiteralPath $i.Source -Destination (Join-Path $PSScriptRoot ('working\VolleyballFever_Data\'+$i.Name)) -Force}
@{installed=(-not $Restore);time=(Get-Date).ToString('o');backup=$backup;runtimeTested=$false}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $PSScriptRoot 'maps-v11\installation.json')
Write-Output 'Mapas conferidos e aplicados. Backup da versao anterior preservado.'
