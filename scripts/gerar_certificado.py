#!/usr/bin/env python3
"""
Script para verificar e gerar certificados SSL quando necessário:
1. Verifica se os certificados já existem
2. Gera certificado para o ISP Hogwarts se necessário
3. Gera certificados para todos os clientes encontrados
"""

import os
import subprocess
import sys
from pathlib import Path

def verificar_certificado_existente(dominio, pasta_saida):
    """Verifica se o certificado já existe e é válido"""
    cert_path = Path(f"{pasta_saida}/{dominio}.crt")
    key_path = Path(f"{pasta_saida}/{dominio}.key")
    
    if not cert_path.exists() or not key_path.exists():
        return False
    
    try:
        # Verifica se o certificado é válido
        subprocess.run(
            ["openssl", "x509", "-in", str(cert_path), "-noout"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False

def gerar_certificado(nome, dominio, pasta_saida):
    """
    Gera certificado SSL autoassinado com validade de 1 ano
    se não existir ou for inválido
    """
    if verificar_certificado_existente(dominio, pasta_saida):
        print(f"Certificado para {dominio} já existe e é válido. Pulando geração.")
        return True
    
    print(f"Gerando certificado para {nome} ({dominio})...")
    
    try:
        # Cria pasta se não existir
        Path(pasta_saida).mkdir(parents=True, exist_ok=True)
        
        # Gera chave privada
        subprocess.run([
            "openssl", "genrsa", "-out", 
            f"{pasta_saida}/{dominio}.key", "2048"
        ], check=True)
        
        # Cria solicitação de certificado
        subprocess.run([
            "openssl", "req", "-new", "-key", f"{pasta_saida}/{dominio}.key",
            "-out", f"{pasta_saida}/{dominio}.csr",
            "-subj", f"/CN={dominio}/O={nome}"
        ], check=True)
        
        # Assina o certificado (validade fixa de 1 ano)
        subprocess.run([
            "openssl", "x509", "-req", "-days", "365",
            "-in", f"{pasta_saida}/{dominio}.csr",
            "-signkey", f"{pasta_saida}/{dominio}.key",
            "-out", f"{pasta_saida}/{dominio}.crt"
        ], check=True)
        
        print(f"✓ Certificado gerado em {pasta_saida}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Erro ao gerar certificado para {dominio}: {e}")
        return False

def processar_clientes():
    """Processa todos os clientes encontrados na pasta /clientes"""
    pasta_clientes = Path("clientes")
    
    if not pasta_clientes.exists():
        print("Aviso: Pasta de clientes não encontrada")
        return
    
    clientes_processados = 0
    
    for cliente in pasta_clientes.iterdir():
        if cliente.is_dir():
            script_cliente = cliente / "scripts" / "gerar_certificado.py"
            if script_cliente.exists():
                print(f"\nProcessando cliente {cliente.name}...")
                try:
                    subprocess.run(["python3", str(script_cliente)], check=True)
                    clientes_processados += 1
                except subprocess.CalledProcessError:
                    print(f"Erro ao processar cliente {cliente.name}")
    
    return clientes_processados

def verificar_openssl():
    """Verifica se o OpenSSL está instalado"""
    try:
        subprocess.run(
            ["openssl", "version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    # Verifica se o OpenSSL está instalado
    if not verificar_openssl():
        print("Erro: OpenSSL não está instalado ou não está no PATH")
        sys.exit(1)
    
    # Gera certificado do ISP se necessário
    sucesso_isp = gerar_certificado(
        nome="Hogwarts ISP",
        dominio="hogwarts.br",
        pasta_saida="proxy/ssl"
    )
    
    if not sucesso_isp:
        sys.exit(1)
    
    # Gera certificados para clientes
    clientes_processados = processar_clientes()
    
    print(f"\n✔ Concluído! {clientes_processados} clientes processados.")

if __name__ == "__main__":
    # Muda para o diretório do script para usar caminhos relativos
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()