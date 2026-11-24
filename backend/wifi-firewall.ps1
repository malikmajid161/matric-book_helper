# Run as Administrator. Remove the rule after phone testing with -Remove.
param([switch]$Remove)
$ErrorActionPreference = 'Stop'
$ruleName = 'PTBScholarTemporaryWifi'
if ($Remove) {
    Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule
    Write-Host 'Temporary Wi-Fi rule removed.'
    exit
}
if (-not (Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name $ruleName -DisplayName 'PTB Scholar temporary Wi-Fi test' `
        -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8000 `
        -LocalAddress 192.168.1.7 -RemoteAddress LocalSubnet -InterfaceAlias 'Wi-Fi' `
        -Profile Public -Program "$PSScriptRoot\.venv\Scripts\python.exe" | Out-Null
}
Write-Host 'Temporary Wi-Fi rule enabled. Run this script with -Remove after testing.'
