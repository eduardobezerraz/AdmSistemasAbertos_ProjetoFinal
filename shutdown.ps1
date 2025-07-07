<#
.SYNOPSIS
  Script de desligamento para infraestrutura ASAPF
.DESCRIPTION
  1. Para os containers via docker-compose
  2. Reativa configurações DHCP
.NOTES
  Execute como Administrador
#>

# Requer execução como Admin
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERRO: Execute como Administrador!" -ForegroundColor Red
    exit 1
}

# 1. Parar containers
try {
    Write-Host "Desligando containers..." -ForegroundColor Magenta
    docker-compose down
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "AVISO: docker-compose down retornou erro ($LASTEXITCODE)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "ERRO ao desligar containers`n$_" -ForegroundColor Red
}

# 2. Reativar DHCP
$dhcpScript = Join-Path -Path $PSScriptRoot -ChildPath "scripts\EnableDHCP_Ipv6.ps1"
if (Test-Path $dhcpScript) {
    try {
        Write-Host "Reativando DHCP..." -ForegroundColor Cyan
        & $dhcpScript
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "AVISO: EnableDHCP_Ipv6.ps1 retornou erro ($LASTEXITCODE)" -ForegroundColor Yellow
        }
        else {
            Write-Host "DHCP reativado com sucesso!" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "ERRO na execução do EnableDHCP_Ipv6.ps1`n$_" -ForegroundColor Red
    }
}
else {
    Write-Host "AVISO: Script DHCP não encontrado em $dhcpScript" -ForegroundColor Yellow
}

Write-Host "Todos os serviços foram desligados." -ForegroundColor Red