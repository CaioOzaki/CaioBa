param([string]$SceneFile,[string]$Label='beach',[string]$TerrainAssets)
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$work=Join-Path $root 'working'
$scene=Join-Path $work 'VolleyballFever_Data\level0'
$saved=Join-Path $root 'analysis\level0-smoke-backup'
if(Test-Path -LiteralPath $saved){throw 'Backup de teste ja existe; verificar antes de prosseguir.'}
$log=Join-Path $root ('analysis\smoke-'+$Label+'.log')
Copy-Item -LiteralPath $scene -Destination $saved
$process=$null
$terrainTarget=Join-Path $work 'VolleyballFever_Data\sharedassets1.assets'
$terrainSaved=Join-Path $root 'analysis\terrain-smoke-backup'
try{
 if($TerrainAssets){
  if(Test-Path -LiteralPath $terrainSaved){throw 'Backup de terreno de teste ja existe.'}
  Copy-Item -LiteralPath $terrainTarget -Destination $terrainSaved
  Copy-Item -LiteralPath $TerrainAssets -Destination $terrainTarget -Force
 }
 Copy-Item -LiteralPath $SceneFile -Destination $scene -Force
 $process=Start-Process -FilePath (Join-Path $work 'VolleyballFever.exe') -WorkingDirectory $work -WindowStyle Hidden -PassThru -ArgumentList @('-batchmode','-force-d3d11','-vrmode','none','-screen-fullscreen','0','-logFile',('"'+$log+'"'))
 $exited=$process.WaitForExit(15000)
 if($exited){Write-Output "Saiu: $($process.ExitCode)"}else{Write-Output 'Processo permaneceu ativo por 15 segundos.'}
}finally{
 if($process -and -not $process.HasExited){Stop-Process -Id $process.Id -Force;$process.WaitForExit()}
 Copy-Item -LiteralPath $saved -Destination $scene -Force
 Remove-Item -LiteralPath $saved
 if($TerrainAssets -and (Test-Path -LiteralPath $terrainSaved)){Copy-Item -LiteralPath $terrainSaved -Destination $terrainTarget -Force;Remove-Item -LiteralPath $terrainSaved}
}
if(Test-Path -LiteralPath $log){Get-Content -LiteralPath $log -Tail 40}
