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

$ipAddress = (Get-NetIPAddress -InterfaceAlias $interfaceName -AddressFamily IPv4 | Select-Object -First 1).IPAddress

if (-not $ipAddress) {
    Write-Host "Erro: Não foi possível obter o IP da interface $interfaceName."
    exit 1
}

# Define o DNS com o IP da interface encontrada
Write-Host "Configurando DNS para $ipAddress na interface $interfaceName..."
Set-DnsClientServerAddress -InterfaceAlias $interfaceName -ServerAddresses $ipAddress

# Desativar IPv6 na interface
Write-Host "Desativando IPv6 na interface $interfaceName..."
Disable-NetAdapterBinding -Name $interfaceName -ComponentID ms_tcpip6 -Confirm:$false

Write-Host "Script finalizado com sucesso."