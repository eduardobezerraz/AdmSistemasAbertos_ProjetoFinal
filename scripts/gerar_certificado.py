#!/usr/bin/env python3
"""
Script aprimorado para gerenciamento de certificados SSL:
1. Padroniza caminhos de certificados
2. Melhora a estrutura de diretórios
3. Adiciona validações de paths
"""

import os
import subprocess
import sys
from pathlib import Path

# Diretórios base padronizados
BASE_DIR = Path(__file__).parent.parent
SSL_DIR_ISP = BASE_DIR / "hogwarts" / "proxy" / "ssl"  # Certificados do ISP corrigido para o caminho certo
CLIENTES_DIR = BASE_DIR / "clientes"

def verificar_certificado_existente(dominio, ssl_dir):
    """Verifica se o certificado já existe e é válido"""
    cert_path = ssl_dir / f"{dominio}.crt"
    key_path = ssl_dir / f"{dominio}.key"
    
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

def gerar_certificado(nome, dominio, ssl_dir):
    """
    Gera certificado SSL autoassinado com estrutura padronizada
    """
    # Cria o diretório se não existir (com permissões seguras)
    ssl_dir.mkdir(parents=True, exist_ok=True, mode=0o750)
    
    if verificar_certificado_existente(dominio, ssl_dir):
        print(f"[INFO] Certificado para {dominio} já existe em {ssl_dir}")
        return True
    
    print(f"[GERANDO] Certificado para {nome} ({dominio}) em {ssl_dir}")
    
    try:
        # Gera chave privada com permissões restritas
        subprocess.run([
            "openssl", "genrsa", "-out", 
            str(ssl_dir / f"{dominio}.key"), "2048"
        ], check=True)
        os.chmod(ssl_dir / f"{dominio}.key", 0o640)

        # Gera CSR
        subprocess.run([
            "openssl", "req", "-new", 
            "-key", str(ssl_dir / f"{dominio}.key"),
            "-out", str(ssl_dir / f"{dominio}.csr"),
            "-subj", f"/CN={dominio}/O={nome}"
        ], check=True)

        # Gera certificado
        subprocess.run([
            "openssl", "x509", "-req", "-days", "365",
            "-in", str(ssl_dir / f"{dominio}.csr"),
            "-signkey", str(ssl_dir / f"{dominio}.key"),
            "-out", str(ssl_dir / f"{dominio}.crt")
        ], check=True)

        print(f"[SUCESSO] Certificado gerado em {ssl_dir}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha ao gerar certificado: {e}", file=sys.stderr)
        return False

def processar_clientes():
    """Processa clientes com estrutura padronizada"""
    if not CLIENTES_DIR.exists():
        print("[AVISO] Pasta de clientes não encontrada", file=sys.stderr)
        return 0
    
    clientes_processados = 0
    
    for cliente_dir in CLIENTES_DIR.iterdir():
        if not cliente_dir.is_dir():
            continue
            
        # Path padronizado para certificados do cliente
        ssl_dir = cliente_dir / "proxy" / "ssl"
        script_cliente = cliente_dir / "scripts" / "gerar_certificado.py"
        
        if script_cliente.exists():
            print(f"\n[CLIENTE] Processando {cliente_dir.name}...")
            try:
                subprocess.run(
                    ["python3", str(script_cliente)],
                    cwd=cliente_dir,
                    check=True
                )
                clientes_processados += 1
            except subprocess.CalledProcessError as e:
                print(f"[ERRO] Falha no cliente {cliente_dir.name}: {e}", file=sys.stderr)
        elif not ssl_dir.exists():
            print(f"[AVISO] {cliente_dir.name} sem configuração SSL", file=sys.stderr)
    
    return clientes_processados

def verificar_openssl():
    """Valida instalação do OpenSSL"""
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
    if not verificar_openssl():
        print("[ERRO] OpenSSL não encontrado", file=sys.stderr)
        sys.exit(1)
    
    # Certificado do ISP
    if not gerar_certificado(
        nome="Hogwarts ISP",
        dominio="hogwarts.br",
        ssl_dir=SSL_DIR_ISP
    ):
        sys.exit(1)
    
    # Certificados dos clientes
    clientes_processados = processar_clientes()
    print(f"\n[CONCLUSÃO] {clientes_processados} clientes processados")

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    main()