# !/bin/bash

# usado para subir os containers do docker sem reutilizar as builds anteriores
docker-compose -f ./docker-compose.yaml -f ./clientes/docker-compose.yaml up --build --force-recreate --remove-orphans