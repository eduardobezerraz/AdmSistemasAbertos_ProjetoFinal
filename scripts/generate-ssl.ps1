<#
.SYNOPSIS
  Gera certificado SSL autoassinado para o projeto ASAPF
#>

param(
    [string]$certName = "sonserina",
    [string]$domain = "proxy.sonserina.br",
    [switch]$SkipInstall
)

# Verifica se é admin
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Execute como Administrador!" -ForegroundColor Red
    exit 1
}

# Configurações
$sslFolder = "$PWD\..\proxy\ssl"
$daysValid = 365
$keySize = 2048

# 1. Cria pasta SSL
if (-NOT (Test-Path $sslFolder)) {
    New-Item -ItemType Directory -Path $sslFolder -Force | Out-Null
}

# 2. Gera certificado
Write-Host "Gerando certificado SSL para $domain..."
openssl req -x509 -nodes -days $daysValid -newkey rsa:$keySize `
    -keyout "$sslFolder\$certName.key" -out "$sslFolder\$certName.crt" `
    -subj "/CN=$domain/O=ASAPF/C=BR"

if (-NOT (Test-Path "$sslFolder\$certName.crt")) {
    Write-Host "Falha ao gerar certificado!" -ForegroundColor Red
    exit 1
}

# 3. Instala certificado (opcional)
if (-NOT $SkipInstall) {
    try {
        Write-Host "Instalando certificado no repositório de autoridades confiáveis..."
        $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
        $cert.Import("$sslFolder\$certName.crt")
        
        $store = New-Object System.Security.Cryptography.X509Certificates.X509Store `
            ([System.Security.Cryptography.X509Certificates.StoreName]::Root, "LocalMachine")
        $store.Open("ReadWrite")
        $store.Add($cert)
        $store.Close()
        Write-Host "Certificado instalado com sucesso!" -ForegroundColor Green
    } catch {
        Write-Host "AVISO: Não foi possível instalar o certificado automaticamente" -ForegroundColor Yellow
        Write-Host "Instale manualmente clicando 2x em $sslFolder\$certName.crt" -ForegroundColor Yellow
    }
}

# 4. Mostra informações
Write-Host "`nResumo do certificado:" -ForegroundColor Cyan
openssl x509 -in "$sslFolder\$certName.crt" -noout -text | Select-String -Pattern "Subject:|Not Before:|Not After :"

Write-Host "`nCertificado gerado em:" -ForegroundColor Green
Write-Host "- Certificado: $sslFolder\$certName.crt"
Write-Host "- Chave privada: $sslFolder\$certName.key"
