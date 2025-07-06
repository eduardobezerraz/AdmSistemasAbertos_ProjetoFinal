FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt upgrade -y

# Instala postfix, dovecot e syslog-ng
RUN apt install -y postfix dovecot-imapd dovecot-pop3d syslog-ng

# Copia arquivos de configuração
COPY main.cf /etc/postfix/
COPY dovecot.conf /etc/dovecot/conf.d/

# Criação de usuários
RUN useradd -m joao_marcos
RUN useradd -m joao_victor
RUN useradd -m jose_eduardo
RUN useradd -m redes

# Definição de senhas
RUN echo "joao_marcos:redes" | chpasswd
RUN echo "joao_victor:redes" | chpasswd
RUN echo "jose_eduardo:redes" | chpasswd
RUN echo "redes:redes" | chpasswd

# Inicialização dos serviços
CMD ["sh", "-c", "service syslog-ng start ; service postfix start ; service dovecot start ; tail -F /var/log/mail.log"]
