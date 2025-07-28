#!/usr/bin/env bash
set -e

# Montagem de certificados e dhparam via volumes

# 1) Lista de usuários e senhas iniciais
declare -A USERS=(
  [redes1]="Senha123"
  [redes2]="Senha123"
)

# 2) Para cada usuário:
for user in "${!USERS[@]}"; do
  # Cria usuário se não existir
  if ! id "$user" &>/dev/null; then
    useradd -m -s /sbin/nologin "$user"
    echo "${user}:${USERS[$user]}" | chpasswd
  fi

  # Maildir: copia do backup ou cria do zero
  if [ ! -d "/home/$user/Maildir" ]; then
    if [ -d "/maildata/$user/Maildir" ]; then
      cp -a /maildata/$user /home/
    else
      maildirmake.dovecot /home/$user/Maildir
      maildirmake.dovecot /home/$user/Maildir/.Sent
      maildirmake.dovecot /home/$user/Maildir/.Trash
      maildirmake.dovecot /home/$user/Maildir/.Drafts
    fi
  fi

  chown -R $user:$user /home/$user
done
chmod -R 700 /home/*/Maildir

# 3) Inicia serviços em foreground
service syslog-ng start
service postfix start
service dovecot start

# 4) Mantém logs ativos
tail -F /var/log/mail.log /var/log/mail.err