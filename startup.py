#!/usr/bin/env python3
"""
Script de inicialização para infraestrutura ASAPF

Funcionalidades:
1. Executa script de certificados SSL (que verifica se precisa gerar)
2. Atualiza arquivo de zona com IP da interface real
3. Inicia containers principais com docker-compose
4. Inicia docker-compose de todos os clientes dinamicamente
5. Configura DNS após containers estarem prontos

Execute como Administrador
"""

import os
import subprocess
import sys
from pathlib import Path
import glob

DOCKER_PROJECT_NAME = "hogwarts"  # Nome do projeto principal
BASE_DIR = Path(__file__).parent.resolve()
MAIN_COMPOSE_DIR = BASE_DIR / "hogwarts"
MAIN_COMPOSE_FILE = MAIN_COMPOSE_DIR / "docker-compose.yml"

def check_admin():
    """Verifica privilégios de administrador no Windows"""
    try:
        result = subprocess.run(
            ['net', 'session'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            print("ERRO: Execute como Administrador!")
            sys.exit(1)
    except FileNotFoundError:
        print("ERRO: Este script só pode ser executado no Windows")
        sys.exit(1)

def run_certificate_script():
    """Executa o script de geração de certificados SSL"""
    script_path = Path("scripts") / "gerar_certificado.py"
    
    if not script_path.exists():
        print("ERRO CRÍTICO: Script de certificados não encontrado")
        sys.exit(1)
    
    print("\nVerificando/gerando certificados SSL...")
    try:
        subprocess.run(['python', str(script_path)], check=True)
        print("Certificados SSL verificados com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"ERRO CRÍTICO: Falha nos certificados SSL (Código: {e.returncode})")
        sys.exit(1)

def run_zone_script():
    """Executa o script de atualização de zona DNS"""
    script_path = Path("scripts") / "atualizar_zona.py"
    
    if not script_path.exists():
        print("AVISO: Script de zona DNS não encontrado")
        return False
    
    print("\nAtualizando zona DNS...")
    try:
        subprocess.run(['python', str(script_path)], check=True)
        print("Zona DNS atualizada com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"AVISO: Falha ao atualizar zona DNS (Código: {e.returncode})")
        return False

def run_dns_config():
    """Executa o script de configuração DNS"""
    script_path = Path("scripts") / "DNSconfig.py"
    
    if not script_path.exists():
        print("AVISO: Script de configuração DNS não encontrado")
        return False
    
    print("\nConfigurando DNS...")
    try:
        subprocess.run(['python', str(script_path)], check=True)
        print("DNS configurado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"AVISO: Falha na configuração DNS (Código: {e.returncode})")
        return False

def start_main_compose():
    """Inicia containers principais do ISP Hogwarts"""
    if not MAIN_COMPOSE_FILE.exists():
        print(f"ERRO CRÍTICO: {MAIN_COMPOSE_FILE} não encontrado")
        sys.exit(1)

    print(f"\nIniciando containers principais com projeto '{DOCKER_PROJECT_NAME}'...")
    try:
        subprocess.run([
            'docker-compose',
            '-p', DOCKER_PROJECT_NAME,
            '-f', str(MAIN_COMPOSE_FILE.resolve()),  # caminho absoluto
            'up', '-d', '--force-recreate', '--remove-orphans'
        ], cwd=str(MAIN_COMPOSE_DIR), check=True)
        print("Containers principais iniciados com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"ERRO CRÍTICO: Falha ao iniciar containers principais\n{e}")
        sys.exit(1)

def start_client_compose():
    """Busca e executa todos os docker-compose_*.yaml dentro de clientes/*"""
    print("\nIniciando containers dos clientes...")
    compose_files = glob.glob("clientes/**/docker-compose_*.yaml", recursive=True)

    if not compose_files:
        print("Nenhum arquivo docker-compose de cliente encontrado.")
        return

    for file in compose_files:
        compose_path = Path(file).resolve()
        client_dir = compose_path.parent
        project_name = client_dir.name

        print(f"\nIniciando cliente: {client_dir.name} (projeto '{project_name}')")

        try:
            subprocess.run([
                'docker-compose',
                '-p', project_name,
                '-f', str(compose_path),
                'up', '-d', '--force-recreate', '--remove-orphans'
            ], cwd=client_dir, check=True)
            print(f"Cliente '{client_dir.name}' iniciado com sucesso")
        except subprocess.CalledProcessError as e:
            print(f"Falha ao iniciar cliente '{client_dir.name}' (Código: {e.returncode})")

def show_status():
    """Mostra status dos containers"""
    print("\nStatus dos containers:")
    subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'])

def main():
    check_admin()
    run_certificate_script()
    run_zone_script()
    start_main_compose()
    start_client_compose()
    run_dns_config()
    show_status()

    print("\nInicialização concluída com sucesso!")
    print("Use './shutdown.py' para encerrar.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
