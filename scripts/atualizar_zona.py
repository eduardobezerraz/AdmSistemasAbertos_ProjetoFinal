#!/usr/bin/env python3
"""
Script para atualizar dinamicamente todos os arquivos de zona DNS (*.br)
com o IP atual da interface de rede principal
"""

import re
import subprocess
import sys
from pathlib import Path

def get_active_interface(ignored_pattern):
    """Obtém a primeira interface ativa (Ethernet ou Wi-Fi) que não está na lista de ignorados"""
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

def get_interface_ip(interface_name):
    """Obtém o endereço IPv4 da interface especificada"""
    try:
        result = subprocess.run(
            ['netsh', 'interface', 'ipv4', 'show', 'addresses', f'name="{interface_name}"'],
            capture_output=True,
            text=True,
            encoding='latin-1',  # Adiciona encoding para tratar caracteres
            check=True
        )
        
        # Regex mais robusta para diferentes codificações
        ip_match = re.search(r'Endere[^\w]o IP:\s+([\d\.]+)', result.stdout)
        if ip_match:
            return ip_match.group(1)
        
        # Fallback para padrão alternativo
        ip_match = re.search(r'IP Address[^\w]\s+([\d\.]+)', result.stdout)
        return ip_match.group(1) if ip_match else None
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao obter IP: {e}", file=sys.stderr)
        return None

def update_zone_file(zone_file, ip_address):
    """
    Atualiza o arquivo de zona DNS com o novo IP
    Retorna tuple: (bool atualizado, bool serial_incrementado)
    """
    try:
        with open(zone_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated = False
        serial_incremented = False
        
        # Incrementa o número serial
        def increment_serial(match):
            nonlocal serial_incremented
            serial_incremented = True
            return f"{int(match.group(1)) + 1}               ; Número serial (incrementado)"
        
        new_content = re.sub(
            r'(\d+)\s*;\s*Número serial',
            increment_serial,
            content,
            count=1
        )
        
        # Atualiza registros A
        def update_a_records(match):
            nonlocal updated
            current_ip = match.group(2)
            if current_ip != ip_address:
                updated = True
                return f"{match.group(1)}{ip_address}"
            return match.group(0)
        
        new_content = re.sub(
            r'^(\s*(?:@|www|ns)?\s+IN\s+A\s+)(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
            update_a_records,
            new_content,
            flags=re.MULTILINE
        )
        
        if updated or serial_incremented:
            with open(zone_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        return (updated, serial_incremented)
        
    except IOError as e:
        print(f"Erro ao manipular arquivo de zona {zone_file}: {e}", file=sys.stderr)
        return (False, False)

def main():
    # Interfaces a ignorar
    ignored = ["virtualbox", "vmware", "hyper-v", "loopback", "vpn", "bluetooth", "tunneling"]
    ignore_pattern = "|".join(ignored)
    
    # 1. Obter interface ativa
    interface_name = get_active_interface(ignore_pattern)
    if not interface_name:
        print("ERRO: Nenhuma interface real ativa (Wi-Fi ou Ethernet) foi encontrada.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Interface selecionada: {interface_name}")
    
    # 2. Obter endereço IP
    ip_address = get_interface_ip(interface_name)
    if not ip_address:
        print(f"ERRO: IP não pôde ser obtido da interface {interface_name}.", file=sys.stderr)
        sys.exit(1)
    
    print(f"IP encontrado: {ip_address}")
    
    # 3. Encontrar e atualizar todos os arquivos .br na pasta DNS
    script_dir = Path(__file__).parent
    dns_dir = script_dir.parent / "hogwarts" / "DNS"
    
    if not dns_dir.exists():
        print(f"ERRO: Pasta DNS não encontrada em {dns_dir}", file=sys.stderr)
        sys.exit(1)
    
    zone_files = list(dns_dir.glob('*.br'))
    
    if not zone_files:
        print("AVISO: Nenhum arquivo de zona (*.br) encontrado na pasta DNS")
        return
    
    print(f"\nEncontrados {len(zone_files)} arquivos de zona:")
    
    for zone_file in zone_files:
        print(f"\nProcessando: {zone_file.name}")
        
        updated, serial_inc = update_zone_file(zone_file, ip_address)

        if serial_inc:
            print("Serial incrementado")
        if updated:
            print(f"IP atualizado para {ip_address}")
        else:
            print("Nenhuma alteração necessária (IPs já estão atualizados)")


if __name__ == "__main__":
    try:
        # Verificar se é Windows
        if sys.platform != 'win32':
            print("Este script é apenas para Windows", file=sys.stderr)
            sys.exit(1)
        
        # Verificar se está sendo executado como administrador
        try:
            subprocess.run(['net', 'session'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("Erro: Este script deve ser executado como Administrador", file=sys.stderr)
            sys.exit(1)
        
        main()
    except KeyboardInterrupt:
        print("\nScript interrompido pelo usuário")
        sys.exit(0)