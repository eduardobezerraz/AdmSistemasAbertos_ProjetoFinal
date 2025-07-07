<#
.SYNOPSIS
  Script de inicialização para infraestrutura ASAPF
.DESCRIPTION
  1. Gera certificados SSL se necessário
  2. Inicia containers com docker-compose (forçando recriação)
  3. Executa configuração DNS
.NOTES
  Execute como Administrador
#>

# Requer execução como Admin
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERRO: Execute como Administrador!" -ForegroundColor Red
    exit 1
}

# 0. Gerar certificados SSL se necessário
$sslCertPath = "$PSScriptRoot\proxy\ssl\sonserina.crt"
$sslKeyPath = "$PSScriptRoot\proxy\ssl\sonserina.key"
$genScriptPath = "$PSScriptRoot\scripts\generate-ssl.ps1"

if (-not (Test-Path $sslCertPath) -or -not (Test-Path $sslKeyPath)) {
    Write-Host "Certificados SSL não encontrados. Gerando..." -ForegroundColor Yellow
    
    if (Test-Path $genScriptPath) {
        try {
            Write-Host "Executando script de geração de certificados..." -ForegroundColor Cyan
            & $genScriptPath
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "AVISO: generate-ssl.ps1 retornou erro ($LASTEXITCODE)" -ForegroundColor Yellow
            }
            else {
                Write-Host "Certificados SSL gerados com sucesso!" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "ERRO na geração de certificados SSL`n$_" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host "ERRO CRÍTICO: Script de geração SSL não encontrado" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "Certificados SSL já existem. Pulando geração." -ForegroundColor Green
}

# 1. Inicialização dos containers
try {
    Write-Host "`nIniciando containers com forçamento de recriação..." -ForegroundColor Cyan
    docker-compose up -d --force-recreate
    
    if ($LASTEXITCODE -ne 0) {
        throw "Falha no docker-compose"
    }
}
catch {
    Write-Host "ERRO CRÍTICO: Falha ao iniciar containers`n$_" -ForegroundColor Red
    exit 1
}

# 2. Configuração DNS
$dnsScript = Join-Path -Path $PSScriptRoot -ChildPath "scripts\DNSconfig.ps1"
if (Test-Path $dnsScript) {
    try {
        Write-Host "`nExecutando configuração DNS..." -ForegroundColor Cyan
        & $dnsScript
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "AVISO: DNSconfig.ps1 retornou erro ($LASTEXITCODE)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "ERRO na execução do DNSconfig.ps1`n$_" -ForegroundColor Red
    }
}
else {
    Write-Host "AVISO: Script DNS não encontrado em $dnsScript" -ForegroundColor Yellow
}

# 3. Status final
Write-Host "`nVerificando estado dos containers:" -ForegroundColor Green
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`nProcesso concluído! Use './shutdown.ps1' para desligar corretamente." -ForegroundColor Green