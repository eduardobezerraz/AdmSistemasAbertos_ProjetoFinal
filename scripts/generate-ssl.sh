#!/bin/bash

# generate-ssl.sh
# Script para gerar certificado SSL autoassinado para o projeto ASAPF

# Para executar o script no windows 
# chmod +x generate-ssl.sh
# sudo ./generate-ssl.sh

# Configurações
CERT_NAME="sonserina"
DOMAIN="proxy.sonserina.br"
SSL_DIR="../proxy/ssl"  # Caminho atualizado para ../proxy/ssl
DAYS_VALID=365
KEY_SIZE=2048

# Verifica se é root
if [ "$EUID" -ne 0 ]; then
  echo "Este script precisa ser executado como root/sudo" >&2
  exit 1
fi

# 1. Verifica dependências
echo "Verificando dependências..."
if ! command -v openssl &> /dev/null; then
  echo "OpenSSL não encontrado. Instalando..."
  apt-get update && apt-get install -y openssl
fi

# 2. Cria diretório SSL
echo "Criando diretório SSL..."
mkdir -p "$SSL_DIR"
chmod 700 "$SSL_DIR"

# 3. Gera certificado autoassinado
echo "Gerando certificado SSL para $DOMAIN..."
openssl req -x509 -nodes -days $DAYS_VALID -newkey rsa:$KEY_SIZE \
  -keyout "$SSL_DIR/$CERT_NAME.key" -out "$SSL_DIR/$CERT_NAME.crt" \
  -subj "/CN=$DOMAIN/O=ASAPF/C=BR"

# 4. Ajusta permissões
chmod 600 "$SSL_DIR/$CERT_NAME.key"
chmod 644 "$SSL_DIR/$CERT_NAME.crt"

# 5. Instala certificado como confiável (Ubuntu/Debian)
echo "Instalando certificado como confiável no sistema..."
cp "$SSL_DIR/$CERT_NAME.crt" /usr/local/share/ca-certificates/
update-ca-certificates

# 6. Verifica instalação
echo -e "\nResumo do certificado:"
openssl x509 -in "$SSL_DIR/$CERT_NAME.crt" -noout -text | grep -E "Subject:|Not Before:|Not After :"

echo -e "\nCertificado gerado com sucesso!"
echo "Arquivos criados:"
echo "- $SSL_DIR/$CERT_NAME.crt"
echo "- $SSL_DIR/$CERT_NAME.key"