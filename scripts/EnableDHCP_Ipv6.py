#!/usr/bin/env python3
"""
Script para reverter configurações de rede no Windows:
1. Reabilita DHCP para endereço IP
2. Remove DNS estático e volta para DHCP
3. Reabilita IPv6
"""

import subprocess
import re
import sys

def get_active_ethernet_interface(ignored_pattern):
    """Obtém a primeira interface Ethernet ativa que não está na lista de ignorados"""
    try:
        result = subprocess.run(
            ['netsh', 'interface', 'show', 'interface'], 
            capture_output=True, 
            text=True,
            check=True
        )
        
        for line in result.stdout.split('\n'):
            if "Conectado" in line and "Ethernet" in line:
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 4:
                    interface_name = parts[-1]
                    interface_desc = parts[-2]
                    if not re.search(ignored_pattern, interface_desc, re.IGNORECASE):
                        return interface_name
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao listar interfaces: {e}")
        return None

def enable_dhcp(interface_name):
    """Habilita DHCP para o endereço IP"""
    try:
        subprocess.run(
            ['netsh', 'interface', 'ipv4', 'set', 'address', 
             f'name="{interface_name}"', 'source=dhcp'],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao habilitar DHCP: {e}")
        return False

def reset_dns(interface_name):
    """Remove DNS estático e volta para DHCP"""
    try:
        subprocess.run(
            ['netsh', 'interface', 'ipv4', 'set', 'dns', 
             f'name="{interface_name}"', 'source=dhcp'],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao redefinir DNS: {e}")
        return False

def enable_ipv6(interface_name):
    """Reabilita o IPv6 na interface"""
    try:
        subprocess.run(
            ['netsh', 'interface', 'ipv6', 'set', 'interface', 
             f'interface="{interface_name}"', 'admin=enabled'],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao habilitar IPv6: {e}")
        return False

def main():
    # Interfaces a ignorar
    ignored = ["virtualbox", "vmware", "hyper-v", "loopback", "vpn", "bluetooth", "tunneling"]
    ignore_pattern = "|".join(ignored)
    
    # Obter interface ativa
    interface_name = get_active_ethernet_interface(ignore_pattern)
    
    if not interface_name:
        print("Erro: Nenhuma interface de rede cabeada real ativa foi encontrada.")
        sys.exit(1)
        
    print(f"Interface selecionada: {interface_name}")

    # 1. Habilitar DHCP para IP
    print(f"Habilitando DHCP para IP na interface {interface_name}...")
    if not enable_dhcp(interface_name):
        print("Aviso: Falha ao habilitar DHCP para IP")
    
    # 2. Configurar DNS para obter automaticamente
    print(f"Configurando DNS para obter automaticamente na interface {interface_name}...")
    if not reset_dns(interface_name):
        print("Aviso: Falha ao redefinir configurações de DNS")
    
    # 3. Reabilitar IPv6
    print(f"Reabilitando IPv6 na interface {interface_name}...")
    if not enable_ipv6(interface_name):
        print("Aviso: Falha ao reabilitar IPv6")
    
    print("Reversão concluída com sucesso.")

if __name__ == "__main__":
    # Verificar se é Windows
    import platform
    if platform.system().lower() != 'windows':
        print("Este script é apenas para Windows")
        sys.exit(1)
    
    # Verificar se está sendo executado como administrador
    try:
        subprocess.run(['net', 'session'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Erro: Este script deve ser executado como Administrador")
        sys.exit(1)
    
    main()