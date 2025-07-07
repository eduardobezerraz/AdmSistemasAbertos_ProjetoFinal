# Script para reverter a configuração do DNS estático e reabilitar DHCP e IPv6

$ignoradas = @("virtualbox", "vmware", "hyper-v", "loopback", "vpn", "bluetooth", "tunneling")

$interface = Get-NetAdapter |
    Where-Object {
        $_.Status -eq 'Up' -and
        $_.InterfaceDescription -notmatch ($ignoradas -join "|") -and
        $_.Name -match "Ethernet"
    } |
    Sort-Object -Property InterfaceMetric |
    Select-Object -First 1

if (-not $interface) {
    Write-Host "Erro: Nenhuma interface de rede cabeada real ativa foi encontrada."
    exit 1
}

$interfaceName = $interface.Name

# Reabilitar DHCP para IP
Write-Host "Habilitando DHCP para IP na interface $interfaceName..."
Set-NetIPInterface -InterfaceAlias $interfaceName -Dhcp Enabled

# Limpar o DNS estático e voltar para DHCP
Write-Host "Configurando DNS para obter automaticamente na interface $interfaceName..."
Set-DnsClientServerAddress -InterfaceAlias $interfaceName -ResetServerAddresses

# Reabilitar IPv6
Write-Host "Reabilitando IPv6 na interface $interfaceName..."
Enable-NetAdapterBinding -Name $interfaceName -ComponentID ms_tcpip6

Write-Host "Reversão concluída com sucesso."
