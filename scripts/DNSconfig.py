import subprocess
import re
import sys

def get_active_interface(ignored_pattern):
    """Obtém a primeira interface Ethernet ativa não ignorada"""
    try:
        result = subprocess.run(
            ['netsh', 'interface', 'show', 'interface'], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            check=True
        )
        
        for line in result.stdout.split('\n'):
            if "Conectado" in line and ("Ethernet" in line or "Wi-Fi" in line):
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 4:
                    interface_name = parts[-1]
                    interface_desc = parts[-2]
                    if not re.search(ignored_pattern, interface_desc, re.IGNORECASE):
                        return interface_name
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao listar interfaces: {e}", file=sys.stderr)
        return None

def get_interface_ip(interface_name):
    """Obtém o endereço IPv4 da interface especificada"""
    try:
        result = subprocess.run(
            ['netsh', 'interface', 'ipv4', 'show', 'addresses', f'name="{interface_name}"'],
            capture_output=True,
            text=True,
            encoding='latin-1',
            check=True
        )
        
        # Padrões alternativos para capturar o IP
        patterns = [
            r'IP Address[^\w]\s+([\d\.]+)',
            r'Endere[^\w]o IP:\s+([\d\.]+)',
            r'^\s*IPv4 Address[^\w]\s+([\d\.]+)'
        ]
        
        for pattern in patterns:
            ip_match = re.search(pattern, result.stdout)
            if ip_match:
                return ip_match.group(1)
        
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao obter IP: {e}", file=sys.stderr)
        return None

def configure_dns(interface_name, primary_dns, secondary_dns="8.8.8.8"):
    """Configura os servidores DNS mantendo DHCP para IP"""
    try:
        # 1. Verificar configurações DNS atuais
        current_dns = subprocess.run(
            ['netsh', 'interface', 'ipv4', 'show', 'dns', f'name="{interface_name}"'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 2. Verificar se o DNS primário já está configurado corretamente
        if primary_dns in current_dns.stdout:
            print(f"DNS primário já está configurado como {primary_dns}")
            return True
            
        # 3. Limpar DNS existentes se necessário
        if "Nenhum servidor DNS configurado" not in current_dns.stdout:
            subprocess.run(
                ['netsh', 'interface', 'ipv4', 'delete', 'dns',
                 f'name="{interface_name}"', 'all'],
                check=True
            )
        
        # 4. Adicionar DNS primário
        subprocess.run(
            ['netsh', 'interface', 'ipv4', 'add', 'dns',
             f'name="{interface_name}"', primary_dns, 'index=1', 'validate=no'],
            check=True
        )
        
        # 5. Adicionar DNS secundário
        subprocess.run(
            ['netsh', 'interface', 'ipv4', 'add', 'dns',
             f'name="{interface_name}"', secondary_dns, 'index=2', 'validate=no'],
            check=True
        )
        
        print("DNS configurado com sucesso (mantendo DHCP)!")
        print(f" - Primário: {primary_dns}")
        print(f" - Secundário: {secondary_dns}")
        
        # 6. Verificar novamente para confirmar
        verify_dns_config(interface_name, primary_dns, secondary_dns)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao configurar DNS: {e}", file=sys.stderr)
        return False

def verify_dns_config(interface_name, expected_primary, expected_secondary):
    """Verifica se o DNS foi configurado corretamente"""
    try:
        result = subprocess.run(
            ['netsh', 'interface', 'ipv4', 'show', 'dns', f'name="{interface_name}"'],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("\nVerificação de configuração DNS:")
        print(result.stdout)
        
        if expected_primary in result.stdout and expected_secondary in result.stdout:
            print("✓ Configuração DNS verificada com sucesso")
            return True
        else:
            print("✗ A configuração DNS não corresponde ao esperado")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Erro ao verificar DNS: {e}", file=sys.stderr)
        return False

def disable_ipv6(interface_name):
    """Desativa o IPv6 na interface especificada via PowerShell"""
    try:
        print(f"Desativando IPv6 na interface '{interface_name}'...")

        # Comando PowerShell
        comando = f'Disable-NetAdapterBinding -Name "{interface_name}" -ComponentID ms_tcpip6'

        resultado = subprocess.run(
            ["powershell", "-Command", comando],
            capture_output=True,
            text=True,
            shell=True
        )

        if resultado.returncode == 0:
            print("IPv6 desativado com sucesso!")
            return True
        else:
            print(f"Erro ao desativar IPv6:\n{resultado.stderr}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"AVISO: Exceção ao tentar desativar IPv6 ({e})", file=sys.stderr)
        return False


def main():
    # Interfaces a ignorar
    ignored = ["virtualbox", "vmware", "hyper-v", "loopback", "vpn", "bluetooth", "tunneling"]
    ignore_pattern = "|".join(ignored)
    
    # 1. Obter interface ativa
    interface_name = get_active_interface(ignore_pattern)
    if not interface_name:
        print("ERRO: Nenhuma interface real ativa foi encontrada.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Interface selecionada: {interface_name}")
    
    # 2. Obter endereço IP
    ip_address = get_interface_ip(interface_name)
    if not ip_address:
        print(f"ERRO: IP não pôde ser obtido da interface {interface_name}.", file=sys.stderr)
        sys.exit(1)
    
    print(f"IP encontrado: {ip_address}")
    
    # 3. Configurar DNS
    if not configure_dns(interface_name, ip_address):
        sys.exit(1)

    # 4. Desativar IPv6 (opcional)
    if not disable_ipv6(interface_name):
        print("AVISO: Continuando sem desativar IPv6...", file=sys.stderr)

    print("\nConfiguração concluída com sucesso!")

if __name__ == "__main__":
    try:
        # Verificar se está sendo executado como administrador
        try:
            subprocess.run(['net', 'session'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("ERRO: Este script deve ser executado como Administrador", file=sys.stderr)
            sys.exit(1)
        
        main()
    except KeyboardInterrupt:
        print("\nScript interrompido pelo usuário")
        sys.exit(0)