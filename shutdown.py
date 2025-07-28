#!/usr/bin/env python3
"""
Script de desligamento para infraestrutura ASAPF

Funcionalidades:
1. Para containers principais via docker-compose
2. Para containers de todos os clientes (docker-compose em clientes/*)
3. Reativa configurações DHCP (IPv4 e IPv6)

Execute como Administrador
"""

import subprocess
import os
import sys
import platform
from pathlib import Path
import glob

def is_admin():
    """Verifica se está em modo administrador"""
    try:
        subprocess.run(['net', 'session'], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def stop_main_compose():
    """Para containers principais com docker-compose"""
    print("Desligando containers principais...")
    try:
        compose_dir = Path(__file__).parent.resolve()
        result = subprocess.run(["docker-compose", "down"], cwd=compose_dir, check=False)
        if result.returncode != 0:
            print(f"AVISO: docker-compose down retornou erro ({result.returncode})")
    except Exception as e:
        print(f"ERRO ao desligar containers principais:\n{e}", file=sys.stderr)

def stop_client_containers():
    """Para containers dos clientes (clientes/**/docker-compose_*.yaml)"""
    print("Desligando containers dos clientes...")
    compose_files = glob.glob("clientes/**/docker-compose_*.yaml", recursive=True)

    if not compose_files:
        print("Nenhum arquivo docker-compose de cliente encontrado.")
        return

    for file in compose_files:
        compose_path = Path(file).resolve()
        client_dir = compose_path.parent
        print(f"\nDesligando cliente: {client_dir.name}")

        try:
            subprocess.run(
                ['docker-compose', '-f', str(compose_path), 'down'],
                cwd=client_dir,
                check=False
            )
            print(f"Cliente '{client_dir.name}' desligado com sucesso")
        except Exception as e:
            print(f"ERRO ao desligar cliente '{client_dir.name}':\n{e}", file=sys.stderr)

def run_dhcp_script():
    """Executa o script EnableDHCP_Ipv6.py se existir"""
    dhcp_script = Path("scripts/EnableDHCP_Ipv6.py").resolve()
    if dhcp_script.exists():
        print("\nReativando DHCP...")
        try:
            result = subprocess.run(["python", str(dhcp_script)], check=False)
            if result.returncode != 0:
                print(f"AVISO: EnableDHCP_Ipv6.py retornou erro ({result.returncode})")
            else:
                print("DHCP reativado com sucesso!")
        except Exception as e:
            print(f"ERRO na execução de EnableDHCP_Ipv6.py:\n{e}", file=sys.stderr)
    else:
        print(f"AVISO: Script DHCP não encontrado em {dhcp_script}")

def main():
    if platform.system().lower() != "windows":
        print("Este script só funciona no Windows.", file=sys.stderr)
        sys.exit(1)

    if not is_admin():
        print("ERRO: Execute este script como Administrador!", file=sys.stderr)
        sys.exit(1)

    stop_main_compose()
    stop_client_containers()
    run_dhcp_script()

    print("\nTodos os serviços foram desligados.")

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrompido pelo usuário.", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Erro inesperado: {str(e)}", file=sys.stderr)
        sys.exit(1)
