FROM nginx:latest


RUN apt-get update && apt-get install -y iputils-ping

COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80