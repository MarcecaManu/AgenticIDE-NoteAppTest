# Script per eseguire SonarQube scan su tutte le cartelle con sonar-project.properties
# Usage: .\run_sonar_scan.ps1 [directory]
# Se non specificata, usa la directory corrente

param(
    [string]$TargetDir = "."
)

$startLocation = Get-Location
$targetPath = Resolve-Path $TargetDir

Write-Host "=== Inizio scansione SonarQube ===" -ForegroundColor Cyan
Write-Host "Directory target: $targetPath" -ForegroundColor Yellow
Write-Host ""

# Ottieni tutte le sottocartelle
$folders = Get-ChildItem -Path $targetPath -Directory -Depth 0

$scannedCount = 0
$skippedCount = 0

foreach ($folder in $folders) {
    Write-Host "Checking: $($folder.Name)" -ForegroundColor Gray
    
    # Vai nella cartella
    Set-Location $folder.FullName
    
    # Verifica se esiste sonar-project.properties
    $sonarFile = "sonar-project.properties"
    
    if (Test-Path $sonarFile) {
        Write-Host "  [OK] Trovato $sonarFile" -ForegroundColor Green
        
        # Leggi il file linea per linea e sostituisci
        $lines = Get-Content $sonarFile
        $modified = $false
        
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -eq "sonar.sources=.") {
                $lines[$i] = "sonar.sources=backend"
                $modified = $true
            }
            # Rimuovi frontend dalle exclusions se presente
            if ($lines[$i] -match "frontend") {
                $lines[$i] = $lines[$i] -replace ",\*\*/frontend/\*\*", ""
                $lines[$i] = $lines[$i] -replace "\*\*/frontend/\*\*,", ""
            }
        }
        
        if ($modified) {
            $lines | Set-Content -Path $sonarFile
            Write-Host "  [OK] Aggiornato sonar.sources=backend" -ForegroundColor Green
        } else {
            Write-Host "  [i] sonar.sources gia configurato" -ForegroundColor Yellow
        }
        
        # Esegui il comando docker
        Write-Host "  [>] Esecuzione SonarQube scan..." -ForegroundColor Cyan
        
        $dockerCmd = 'docker run --rm -e SONAR_HOST_URL="http://host.docker.internal:9000/" -e SONAR_TOKEN="sqa_d3ca70f0a85dbe9a57103432ae1d26307cd42d6b" -v "' + (Get-Location).Path + ':/usr/src" sonarsource/sonar-scanner-cli'
        
        Invoke-Expression $dockerCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Scan completato per $($folder.Name)" -ForegroundColor Green
            $scannedCount++
        } else {
            Write-Host "  [ERR] Errore scan di $($folder.Name)" -ForegroundColor Red
        }
        
        Write-Host ""
    } else {
        Write-Host "  [-] Nessun $sonarFile trovato, skip" -ForegroundColor DarkGray
        $skippedCount++
    }
    
    # Torna alla directory iniziale
    Set-Location $startLocation
}

Write-Host "=== Scansione completata ===" -ForegroundColor Cyan
Write-Host "Progetti scansionati: $scannedCount" -ForegroundColor Green
Write-Host "Progetti saltati: $skippedCount" -ForegroundColor Yellow
