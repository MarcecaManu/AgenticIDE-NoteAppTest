# Script per generare report Lighthouse per tutti i frontend
# Uso: .\generate_lighthouse_reports.ps1

$ErrorActionPreference = "Continue"
$startDir = Get-Location

Write-Host "=== Lighthouse Batch Report Generator ===" -ForegroundColor Cyan
Write-Host "Directory iniziale: $startDir" -ForegroundColor Yellow
Write-Host ""

# Trova tutte le cartelle nella directory corrente
$folders = Get-ChildItem -Directory

foreach ($folder in $folders) {
    $frontendPath = Join-Path $folder.FullName "frontend"
    
    # Verifica se esiste la cartella frontend
    if (Test-Path $frontendPath) {
        Write-Host "=== Processando: $($folder.Name) ===" -ForegroundColor Green
        
        # Entra nella cartella frontend
        Set-Location $frontendPath
        Write-Host "  Directory: $frontendPath" -ForegroundColor Gray
        
        # Avvia il server Python in background
        Write-Host "  Avvio server HTTP su porta 3000..." -ForegroundColor Yellow
        $serverJob = Start-Job -ScriptBlock {
            param($path)
            Set-Location $path
            python -m http.server 3000
        } -ArgumentList $frontendPath
        
        # Aspetta che il server sia pronto (5 secondi dovrebbero bastare)
        Write-Host "  Attendo avvio server..." -ForegroundColor Gray
        Start-Sleep -Seconds 5
        
        # Verifica che il server sia raggiungibile
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
            Write-Host "  Server online!" -ForegroundColor Green
            
            # Esegue Lighthouse
            Write-Host "  Esecuzione Lighthouse..." -ForegroundColor Yellow
            lighthouse http://localhost:3000 --output html --output-path ../lighthouse-report.html --quiet
            
            if (Test-Path "../lighthouse-report.html") {
                Write-Host "  Report generato: lighthouse-report.html" -ForegroundColor Green
            } else {
                Write-Host "  Errore: report non generato" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "  Errore: server non raggiungibile" -ForegroundColor Red
        }
        
        # Ferma il server
        Write-Host "  Arresto server..." -ForegroundColor Gray
        Stop-Job -Job $serverJob
        Remove-Job -Job $serverJob
        
        # Torna alla directory iniziale
        Set-Location $startDir
        Write-Host ""
    } else {
        Write-Host "Saltato: $($folder.Name) (cartella frontend non trovata)" -ForegroundColor DarkGray
    }
}

Write-Host "=== Completato! ===" -ForegroundColor Cyan
Write-Host "Torno alla directory iniziale: $startDir" -ForegroundColor Yellow
Set-Location $startDir
