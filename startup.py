#!/usr/bin/env python3
"""
Script de inicialização para infraestrutura ASAPF

Funcionalidades:
1. Executa script de certificados SSL (que verifica se precisa gerar)
2. Atualiza arquivo de zona com IP da interface real
3. Inicia containers com docker-compose
4. Configura DNS após containers estarem prontos

Execute como Administrador
"""

import os
import subprocess
import sys
from pathlib import Path

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
        print("✓ Certificados SSL verificados com sucesso")
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
        print("✓ Zona DNS atualizada com sucesso")
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
        print("✓ DNS configurado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"AVISO: Falha na configuração DNS (Código: {e.returncode})")
        return False

def start_containers():
    """Inicia os containers com docker-compose"""
    if not Path("docker-compose.yml").exists():
        print("ERRO CRÍTICO: docker-compose.yml não encontrado")
        sys.exit(1)
    
    print("\nIniciando containers Docker...")
    try:
        subprocess.run(
            ['docker-compose', 'up', '-d', '--force-recreate', '--remove-orphans'],
            check=True
        )
        print("✓ Containers iniciados com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"ERRO CRÍTICO: Falha ao iniciar containers\n{e}")
        sys.exit(1)

def show_status():
    """Mostra status dos containers"""
    print("\nStatus dos containers:")
    subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'])

def main():
    check_admin()
    
    # Fluxo principal de inicialização
    run_certificate_script()
    run_zone_script()
    start_containers()
    run_dns_config()
    
    # Status final
    show_status()
    print("\n✔ Inicialização concluída com sucesso!")
    print("Use './shutdown.py' para encerrar.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()