#!/usr/bin/env python3
"""
Script para reverter configurações de rede no Windows
"""

import subprocess
import re
import sys
import platform

def get_active_interface(ignored_pattern):
    """Obtém a primeira interface ativa (Ethernet ou Wi-Fi) não ignorada"""
    try:
        result = subprocess.run(
            ['netsh', 'interface', 'show', 'interface'], 
            capture_output=True, 
            text=True,
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

def enable_dhcp(interface_name):
    """Verifica e habilita DHCP se necessário"""
    try:
        result = subprocess.run(
            ['netsh', 'interface', 'ipv4', 'show', 'config', f'name="{interface_name}"'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if "DHCP habilitado" in result.stdout:
            print("DHCP já está habilitado")
            return True
        else:
            subprocess.run(
                ['netsh', 'interface', 'ipv4', 'set', 'address', 
                 f'name="{interface_name}"', 'source=dhcp'],
                check=True
            )
            print("DHCP habilitado com sucesso")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"Erro ao verificar DHCP: {e.stderr if e.stderr else e}", file=sys.stderr)
        return False

def reset_dns(interface_name):
    """Configura DNS para obter automaticamente"""
    try:
        # Primeiro remove quaisquer servidores DNS configurados
        subprocess.run(
            ['netsh', 'interface', 'ipv4', 'delete', 'dns', 
             f'name="{interface_name}"', 'all'],
            check=True
        )
        
        # Depois configura para obter automaticamente
        subprocess.run(
            ['netsh', 'interface', 'ipv4', 'set', 'dns', 
             f'name="{interface_name}"', 'source=dhcp'],
            check=True
        )
        print("DNS configurado para obtenção automática")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao configurar DNS automático: {e.stderr if e.stderr else e}", file=sys.stderr)
        return False

def enable_ipv6(interface_name):
    """Reativa o IPv6 na interface especificada via PowerShell"""
    try:
        print(f"Reativando IPv6 na interface '{interface_name}'...")

        # Comando PowerShell para habilitar IPv6
        comando = f'Enable-NetAdapterBinding -Name "{interface_name}" -ComponentID ms_tcpip6'

        resultado = subprocess.run(
            ["powershell", "-Command", comando],
            capture_output=True,
            text=True,
            shell=True
        )

        if resultado.returncode == 0:
            print("IPv6 reativado com sucesso!")
            return True
        else:
            print(f"Erro ao reativar IPv6:\n{resultado.stderr}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"AVISO: Erro ao tentar reativar IPv6: {e}", file=sys.stderr)
        return False

def verify_config(interface_name):
    """Verifica as configurações atuais"""
    try:
        print("\nVerificação final:")
        
        # Verifica DHCP
        result = subprocess.run(
            ['netsh', 'interface', 'ipv4', 'show', 'config', f'name="{interface_name}"'],
            capture_output=True,
            text=True,
            check=True
        )
        dhcp_status = "DHCP habilitado" in result.stdout
        print(f"- DHCP: {'Sim' if dhcp_status else 'Nao'}")
        
        # Verifica DNS
        result = subprocess.run(
            ['netsh', 'interface', 'ipv4', 'show', 'dns', f'name="{interface_name}"'],
            capture_output=True,
            text=True,
            check=True
        )
        dns_status = "DHCP habilitado" in result.stdout
        print(f"- DNS automático: {'Sim' if dns_status else 'Nao'}")
        
        # Verifica IPv6
        result = subprocess.run(
            ['netsh', 'interface', 'ipv6', 'show', 'interface', interface_name],
            capture_output=True,
            text=True,
            check=False
        )
        ipv6_status = result.returncode == 0 and "enabled" in result.stdout.lower()
        print(f"- IPv6 habilitado: {'Sim' if ipv6_status else 'Nao'}")
        
        return dhcp_status and dns_status and ipv6_status
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao verificar configurações: {e}", file=sys.stderr)
        return False

def main():
    # Interfaces a ignorar
    ignored = ["virtualbox", "vmware", "hyper-v", "loopback", "vpn", "bluetooth", "tunneling"]
    ignore_pattern = "|".join(ignored)
    
    # Obter interface ativa
    interface_name = get_active_interface(ignore_pattern)
    
    if not interface_name:
        print("Erro: Nenhuma interface de rede ativa foi encontrada.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Interface selecionada: {interface_name}")

    # 1. Verificar e configurar DHCP
    print("\n1. Configurando DHCP...")
    enable_dhcp(interface_name)
    
    # 2. Configurar DNS automático
    print("\n2. Configurando DNS automático...")
    reset_dns(interface_name)
    
    # 3. Tentar habilitar IPv6
    print("\n3. Verificando IPv6...")
    enable_ipv6(interface_name)
    
    # Verificação final
    verify_config(interface_name)
    
    print("\nProcesso concluído. Verifique as configurações acima.")

if __name__ == "__main__":
    # Verificar se é Windows
    if platform.system().lower() != 'windows':
        print("Este script é apenas para Windows", file=sys.stderr)
        sys.exit(1)
    
    # Verificar se está sendo executado como administrador
    try:
        subprocess.run(['net', 'session'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Erro: Este script deve ser executado como Administrador", file=sys.stderr)
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrompido pelo usuário", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Erro inesperado: {str(e)}", file=sys.stderr)
        sys.exit(1)