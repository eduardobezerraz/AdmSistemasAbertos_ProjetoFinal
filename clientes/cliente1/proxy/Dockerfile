
FROM nginx:alpine

# Copia a configuração customizada para dentro do container
COPY default.conf /etc/nginx/default.conf
COPY index.html /usr/share/nginx/html/index.html

# Exporta a porta 80 para acesso externo
EXPOSE 80

