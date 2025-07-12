FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt upgrade -y \
 && apt install -y postfix dovecot-imapd dovecot-pop3d syslog-ng mailutils \
 && rm -rf /var/lib/apt/lists/*

# Copia configs
COPY postfix/main.cf /etc/postfix/main.cf
COPY dovecolt/dovecot.conf /etc/dovecot/conf.d/10-mail.conf
COPY dovecolt/dovecot.conf /etc/dovecot/dovecot.conf

# Cria usuários e seus Maildirs
RUN for u in joao_marcos joao_victor jose_eduardo redes; do \
      useradd -m -s /usr/sbin/nologin "$u" && \
      echo "$u:redes" | chpasswd && \
      mkdir -p /home/"$u"/Maildir/{cur,new,tmp} && \
      chown -R "$u":"$u" /home/"$u"/Maildir ; \
    done

EXPOSE 25 465 587 993

CMD ["sh", "-c", "service syslog-ng start && service postfix start && service dovecot start && tail -F /var/log/mail.log"]
