FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive

# 1) Instala pacotes necessários
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
      postfix \
      dovecot-core dovecot-imapd dovecot-pop3d \
      syslog-ng && \
    rm -rf /var/lib/apt/lists/*

# 2) Copia configurações
COPY conf.d/10-auth.conf.ext    /etc/dovecot/conf.d/10-auth.conf.ext
COPY conf.d/10-mail.conf        /etc/dovecot/conf.d/10-mail.conf
COPY conf.d/10-master.conf      /etc/dovecot/conf.d/10-master.conf
COPY dovecolt/dovecot.conf /etc/dovecot/dovecot.conf

COPY postfix/main.cf            /etc/postfix/main.cf

# 3) Copia e torna executável o init
COPY scripts/init.sh /init.sh
RUN chmod +x /init.sh

# 4) Declara volumes para certificados e dados
VOLUME ["/etc/ssl/certs", "/etc/ssl/private", "/maildata"]

ENTRYPOINT ["/init.sh"]