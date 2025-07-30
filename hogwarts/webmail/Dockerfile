FROM roundcube/roundcubemail:latest

RUN mkdir -p /var/roundcube/db \
    && touch /var/roundcube/db/sqlite.db \
    && chown -R www-data:www-data /var/roundcube/db \
    && chmod 770 /var/roundcube/db \
    && chmod 660 /var/roundcube/db/sqlite.db
