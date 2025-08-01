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

def check_create_network(network_name):
    """Verifica se uma rede Docker existe, criando se necessário"""
    print(f"\nVerificando rede Docker '{network_name}'...")
    
    # Verifica se a rede já existe
    check_cmd = ['docker', 'network', 'inspect', network_name]
    result = subprocess.run(check_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Rede '{network_name}' já existe")
        return True
    
    # Se não existe, cria a rede
    print(f"Criando rede '{network_name}'...")
    try:
        subprocess.run([
            'docker', 'network', 'create',
            '--driver', 'bridge',
            '--attachable',
            network_name
        ], check=True)
        print(f"Rede '{network_name}' criada com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERRO: Falha ao criar rede '{network_name}' (Código: {e.returncode})")
        return False

def run_certificate_script(base_dir):
    """Executa o script de geração de certificados SSL"""
    script_path = base_dir / "scripts" / "gerar_certificado.py"
    
    if not script_path.exists():
        print(f"ERRO CRÍTICO: Script de certificados não encontrado em {script_path}")
        sys.exit(1)
    
    print("\nVerificando/gerando certificados SSL...")
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
        print("Certificados SSL verificados com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"ERRO CRÍTICO: Falha nos certificados SSL (Código: {e.returncode})")
        sys.exit(1)

def run_zone_script(base_dir):
    """Executa o script de atualização de zona DNS"""
    script_path = base_dir / "scripts" / "atualizar_zona.py"
    
    if not script_path.exists():
        print(f"AVISO: Script de zona DNS não encontrado em {script_path}")
        return False
    
    print("\nAtualizando zona DNS...")
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
        print("Zona DNS atualizada com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"AVISO: Falha ao atualizar zona DNS (Código: {e.returncode})")
        return False

def run_dns_config(base_dir):
    """Executa o script de configuração DNS"""
    script_path = base_dir / "scripts" / "DNSconfig.py"
    
    if not script_path.exists():
        print(f"AVISO: Script de configuração DNS não encontrado em {script_path}")
        return False
    
    print("\nConfigurando DNS...")
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
        print("DNS configurado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"AVISO: Falha na configuração DNS (Código: {e.returncode})")
        return False

def start_main_compose(base_dir):
    """Rebuilda e inicia containers principais do ISP Hogwarts sem cache"""
    main_compose_dir = base_dir / "hogwarts"
    main_compose_file = main_compose_dir / "docker-compose.yml"

    if not main_compose_file.exists():
        print(f"ERRO CRÍTICO: {main_compose_file} não encontrado")
        sys.exit(1)

    print(f"\n(Re)iniciando containers principais com projeto '{DOCKER_PROJECT_NAME}'...")

    try:
        # Derruba containers antigos e remove volumes órfãos
        subprocess.run([
            'docker-compose',
            '-p', DOCKER_PROJECT_NAME,
            '-f', str(main_compose_file.resolve()),
            'down', '-v', '--remove-orphans'
        ], cwd=str(main_compose_dir), check=True)

        # Rebuild sem cache
        subprocess.run([
            'docker-compose',
            '-p', DOCKER_PROJECT_NAME,
            '-f', str(main_compose_file.resolve()),
            'build', '--no-cache'
        ], cwd=str(main_compose_dir), check=True)

        # Sobe containers recriando
        subprocess.run([
            'docker-compose',
            '-p', DOCKER_PROJECT_NAME,
            '-f', str(main_compose_file.resolve()),
            'up', '-d', '--force-recreate', '--remove-orphans'
        ], cwd=str(main_compose_dir), check=True)

        print("Containers principais iniciados com sucesso (build limpo)")
    except subprocess.CalledProcessError as e:
        print(f"ERRO CRÍTICO: Falha ao iniciar containers principais\n{e}")
        sys.exit(1)

def start_client_compose(base_dir):
    """Rebuilda e inicia todos os clientes sem cache"""
    print("\nIniciando containers dos clientes...")
    client_dir = base_dir / "clientes"

    if not client_dir.exists():
        print(f"AVISO: Diretório de clientes não encontrado em {client_dir}")
        return

    compose_files = list(client_dir.glob("**/docker-compose_*.yaml"))

    if not compose_files:
        print("Nenhum arquivo docker-compose de cliente encontrado.")
        return

    for file in compose_files:
        compose_path = file.resolve()
        client_project_dir = compose_path.parent
        project_name = client_project_dir.name

        print(f"\n(Re)iniciando cliente: {project_name} (projeto '{project_name}')")

        try:
            # Derruba containers antigos
            subprocess.run([
                'docker-compose',
                '-p', project_name,
                '-f', str(compose_path),
                'down', '-v', '--remove-orphans'
            ], cwd=str(client_project_dir), check=True)

            # Rebuild sem cache
            subprocess.run([
                'docker-compose',
                '-p', project_name,
                '-f', str(compose_path),
                'build', '--no-cache'
            ], cwd=str(client_project_dir), check=True)

            # Sobe containers recriando
            subprocess.run([
                'docker-compose',
                '-p', project_name,
                '-f', str(compose_path),
                'up', '-d', '--force-recreate', '--remove-orphans'
            ], cwd=str(client_project_dir), check=True)

            print(f"Cliente '{project_name}' iniciado com sucesso (build limpo)")
        except subprocess.CalledProcessError as e:
            print(f"Falha ao iniciar cliente '{project_name}' (Código: {e.returncode})")

def show_status():
    """Mostra status dos containers"""
    print("\nStatus dos containers:")
    subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'])

def check_docker():
    """Verifica se o Docker está instalado e acessível"""
    try:
        subprocess.run(['docker', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERRO: Docker não está instalado ou não está no PATH")
        sys.exit(1)

def fix_line_endings(base_dir):
    """Corrige finais de linha CRLF -> LF em todos os arquivos relevantes"""
    script_path = base_dir / "scripts" / "fix_line_endings.py"

    if not script_path.exists():
        print(f"AVISO: Script de correção de finais de linha não encontrado em {script_path}")
        return

    print("\n🔧 Corrigindo finais de linha (CRLF -> LF)...")
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
        print("Finais de linha corrigidos com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"AVISO: Falha ao corrigir finais de linha (Código: {e.returncode})")


def main(base_dir):
    check_admin()
    check_docker()

    # Corrige CRLF -> LF antes de usar qualquer arquivo
    fix_line_endings(base_dir)
    
    # Verifica/cria redes isoladas 
    check_create_network("hogwartsnet")
    check_create_network("sonserinanet")
    check_create_network("grifinorianet")
    check_create_network("corvinalnet")

    # Cria as redes bridge entre o proxy Hogwarts e as casas
    check_create_network("sonserinabridge")
    check_create_network("grifinoriabridge")
    check_create_network("corvinalbridge")

    # Executado o script para gerar certificados SSL
    run_certificate_script(base_dir)

    # Atualiza os arquivos de zona para o ip da interface utilizada
    run_zone_script(base_dir)

    # Inicia os serviços de todos os clientes
    start_client_compose(base_dir)

    # Inicia os serviços do ISP 
    start_main_compose(base_dir)

    # Configura o DNS da interface de rede
    run_dns_config(base_dir)

    # Verifica status dos containers
    show_status()

    print("\nInicialização concluída com sucesso!")
    print("Use './shutdown.py' para encerrar.")

if __name__ == "__main__":
    # Configura caminhos de forma robusta
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    BASE_DIR = Path(script_dir).resolve()
    
    main(BASE_DIR)