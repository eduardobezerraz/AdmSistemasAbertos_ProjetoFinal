FROM nginx:latest

# Copia a configuração do servidor (vai para /etc/nginx/conf.d/default.conf)
#COPY default.conf /etc/nginx/conf.d/

# Copia a página inicial personalizada
#COPY index.html /usr/share/nginx/html/index.html

# Cria diretório de logs e ajusta permissões
RUN mkdir -p /var/log/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chmod -R 755 /var/log/nginx

# Mantém o Nginx em primeiro plano
CMD ["sh", "-c", "nginx -t && nginx -g 'daemon off;'"]