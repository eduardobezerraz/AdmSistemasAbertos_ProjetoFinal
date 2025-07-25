#!/usr/bin/env python3
"""Script para gerar certificado do cliente"""

import os
import subprocess
from pathlib import Path

# Obtém nome do cliente a partir da estrutura de pastas
def obter_nome_cliente():
    caminho_script = Path(__file__).resolve()
    pasta_cliente = caminho_script.parent.parent
    return pasta_cliente.name

def main():
    nome_cliente = obter_nome_cliente()
    
    # Configurações fixas
    dominio = f"{nome_cliente}.br"
    pasta_saida = "../proxy/ssl"
    
    print(f"Gerando certificado para {nome_cliente}...")
    
    try:
        # Cria pasta se não existir
        os.makedirs(pasta_saida, exist_ok=True)
        
        # Gera chave privada
        subprocess.run([
            "openssl", "genrsa", "-out", 
            f"{pasta_saida}/{dominio}.key", "2048"
        ], check=True)
        
        # Cria solicitação de certificado
        subprocess.run([
            "openssl", "req", "-new", "-key", f"{pasta_saida}/{dominio}.key",
            "-out", f"{pasta_saida}/{dominio}.csr",
            "-subj", f"/CN={dominio}/O={nome_cliente}"
        ], check=True)
        
        # Assina o certificado (1 ano)
        subprocess.run([
            "openssl", "x509", "-req", "-days", "365",
            "-in", f"{pasta_saida}/{dominio}.csr",
            "-signkey", f"{pasta_saida}/{dominio}.key",
            "-out", f"{pasta_saida}/{dominio}.crt"
        ], check=True)
        
        print("Sucesso!")
    except subprocess.CalledProcessError:
        print("Falha ao gerar certificado")

if __name__ == "__main__":
    main()