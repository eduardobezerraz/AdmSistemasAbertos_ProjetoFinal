RUN for user in "joao_marcos" "joao_victor" "jose_eduardo" "redes"; do \
    mkdir -p /home/$user/Maildir/{cur,new,tmp} && \
    chown -R $user:$user /home/$user/Maildir; \
done
