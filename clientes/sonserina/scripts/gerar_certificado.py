#!/usr/bin/env python3
"""Script para gerar certificado do cliente - Versão Corrigida com verificação de certificado existente"""

import os
import subprocess
from pathlib import Path

def obter_nome_cliente():
    caminho_script = Path(__file__).resolve()
    pasta_cliente = caminho_script.parent.parent
    return pasta_cliente.name

def certificado_existe_e_valido(cert_path, key_path):
    if not cert_path.exists() or not key_path.exists():
        return False
    try:
        subprocess.run(
            ["openssl", "x509", "-in", str(cert_path), "-noout"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    nome_cliente = obter_nome_cliente()
    dominio = f"{nome_cliente}.br"
    
    pasta_saida = Path(__file__).resolve().parent.parent / "proxy" / "ssl"
    
    cert_path = pasta_saida / f"{dominio}.crt"
    key_path = pasta_saida / f"{dominio}.key"
    
    print(f"Gerando certificado para {dominio}...")

    # Verifica se o certificado já existe e é válido
    if certificado_existe_e_valido(cert_path, key_path):
        print(f"[INFO] Certificado já existe e é válido: {cert_path}")
        return

    try:
        pasta_saida.mkdir(parents=True, exist_ok=True)
        
        # Gera chave privada
        subprocess.run([
            "openssl", "genrsa", "-out", 
            str(key_path), "2048"
        ], check=True)
        
        # Cria CSR
        subprocess.run([
            "openssl", "req", "-new", "-key", str(key_path),
            "-out", str(pasta_saida / f"{dominio}.csr"),
            "-subj", f"/CN={dominio}/O={nome_cliente}"
        ], check=True)
        
        # Gera certificado autoassinado
        subprocess.run([
            "openssl", "x509", "-req", "-days", "365",
            "-in", str(pasta_saida / f"{dominio}.csr"),
            "-signkey", str(key_path),
            "-out", str(cert_path)
        ], check=True)
        
        print("Certificado gerado com sucesso!")
        print(f"Certificado: {cert_path}")
        print(f"Chave privada: {key_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar openssl: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()
