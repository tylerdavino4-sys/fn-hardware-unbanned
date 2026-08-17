# REBOOTEDSPOOFER - ONE CLICK CRACK LAUNCHER
# Run as Administrator, sit back, enjoy.

param([switch]$NoSpoofer)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"

# Check admin
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    $wshell = New-Object -ComObject WScript.Shell
    $wshell.Popup("Run as Administrator!", 0, "REBOOTED Crack", 0x10)
    exit
}

Write-Host "=============================================" -ForegroundColor Green
Write-Host "   REBOOTEDSPOOFER - One Click Crack" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# --- AUTO-FIND THE SPOOFER ---
$SpooferPath = ""

# Search priority list:
$searchPaths = @(
    "C:\Users\Kanye West Junior\Downloads\REBOOTEDSPOOFER.exe",
    "$env:USERPROFILE\Downloads\REBOOTEDSPOOFER.exe",
    "$env:USERPROFILE\Desktop\REBOOTEDSPOOFER.exe",
    "$env:USERPROFILE\Documents\REBOOTEDSPOOFER.exe",
    ".\REBOOTEDSPOOFER.exe",
    "$PSScriptRoot\REBOOTEDSPOOFER.exe"
)

foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        $SpooferPath = $path
        break
    }
}

# If not found, ask user
if (-not $SpooferPath -or -not (Test-Path $SpooferPath)) {
    Write-Host "[!] REBOOTEDSPOOFER.exe not found automatically." -ForegroundColor Yellow
    Write-Host ""
    Write-Host " Drag & drop REBOOTEDSPOOFER.exe here, then press Enter:" -ForegroundColor Cyan
    Write-Host " (or type the full path)" -ForegroundColor Gray
    $input = Read-Host
    $input = $input.Trim('"'' ')  # Clean quotes/spaces from drag-drop
    if (Test-Path $input) {
        $SpooferPath = $input
    } else {
        Write-Host "[!] Invalid path. Launch the spoofer manually after setup." -ForegroundColor Red
    }
}

Write-Host "[+] Spoofer: $SpooferPath" -ForegroundColor Green
Write-Host ""

# 1. Install SSL cert
Write-Host "[1/5] Installing SSL certificate..." -NoNewline
try {
    Import-Certificate -FilePath "$ScriptDir\server.crt" -CertStoreLocation Cert:\LocalMachine\Root -ErrorAction SilentlyContinue | Out-Null
    Write-Host " OK" -ForegroundColor Green
} catch { Write-Host " (already trusted)" -ForegroundColor Yellow }

# 2. Add hosts entry
Write-Host "[2/5] Adding hosts redirect..." -NoNewline
if (-not (Select-String -Path $HostsPath -Pattern "keyauth.win" -SimpleMatch -Quiet)) {
    Add-Content -Path $HostsPath -Value "`r`n127.0.0.1 keyauth.win" -Force
    Write-Host " OK" -ForegroundColor Green
} else { Write-Host " (already exists)" -ForegroundColor Yellow }

# 3. Flush DNS
Write-Host "[3/5] Flushing DNS..." -NoNewline
ipconfig /flushdns 2>$null | Out-Null
Write-Host " OK" -ForegroundColor Green

# 4. Setup port forward
Write-Host "[4/5] Setting up port forward..." -NoNewline
netsh interface portproxy delete v4tov4 listenport=443 listenaddress=127.0.0.1 2>$null | Out-Null
netsh interface portproxy add v4tov4 listenport=443 listenaddress=127.0.0.1 connectport=4443 connectaddress=127.0.0.1
Write-Host " OK" -ForegroundColor Green

# 5. Start emulator
Write-Host "[5/5] Starting KeyAuth emulator..." -NoNewline
$emulatorJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    py keyauth_emulator.py 4443
} -ArgumentList $ScriptDir
Start-Sleep -Seconds 2
Write-Host " OK (PID: $($emulatorJob.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   [+] All systems GO!" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Launch the spoofer
if (-not $NoSpoofer -and $SpooferPath -and (Test-Path $SpooferPath)) {
    Write-Host "[*] Launching $SpooferPath ..." -ForegroundColor Yellow
    Start-Process $SpooferPath
    Write-Host "[*] Spoofer window should open shortly." -ForegroundColor Yellow
} elseif (-not $NoSpoofer) {
    Write-Host "[*] Spoofer not found/path invalid." -ForegroundColor Yellow
    Write-Host "[*] Launch it manually after the bypass is ready." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[*] Register with ANY username/password/key" -ForegroundColor White
Write-Host "[*] Close this window to stop the emulator" -ForegroundColor Gray
Write-Host ""

# Keep alive
while ($true) {
    Start-Sleep -Seconds 10
    $j = Get-Job -Id $emulatorJob.Id -ErrorAction SilentlyContinue
    if (-not $j -or $j.State -eq "Failed" -or $j.State -eq "Stopped") {
        Write-Host "[!] Emulator stopped. Restarting..." -ForegroundColor Yellow
        $emulatorJob = Start-Job -ScriptBlock {
            param($dir)
            Set-Location $dir
            py keyauth_emulator.py 4443
        } -ArgumentList $ScriptDir
    }
}