# 🌐 Projeto Final - ASA | Provedor de Serviços de Internet com Microsserviços

> Disciplina: Administração de Sistemas Abertos (ASA)  
> Professor: Sales Filho  
> Duração: 8 semanas  
> Instituição: IFRN - Campus Currais Novos

## 👥 Equipe

- [@eduardobezerraz](https://github.com/eduardobezerraz) - José Eduardo Bezerra de Medeiros  
- [@joao-victor212](https://github.com/joao-victor212) - João Victor  
- [@joaommcjm](https://github.com/joaommcjm) - João Marcos Medeiros Costa  
- [@Luigibalacoder](https://github.com/Luigibalacoder) - Luigi V. Pini  

---

## 📌 Descrição

Este projeto tem como objetivo a implementação de uma **infraestrutura para Provedor de Serviços de Internet (ISP)** utilizando **microsserviços e Docker**, aplicando os princípios de *Infrastructure as Code (IaC)* e *DevOps*. O sistema é modular, seguro e escalável, contemplando serviços como:

- DNS (com Bind9)  
- Correio Eletrônico (com Postfix e Dovecot)  
- Proxy reverso com SSL/TLS (via Nginx, HAProxy, Apache ou Traefik)  

---

## 🎯 Objetivos SMART

- [x] Desenvolver uma infraestrutura baseada em Docker para ISPs  
- [x] Isolar serviços por cliente usando Docker Networks e ACLs  
- [x] Aplicar criptografia com HTTPS e STARTTLS  
- [x] Criar testes automatizados e documentação em vídeo  
- [x] Validar desempenho com métricas (latência, disponibilidade)  
- [x] Cumprir entregas parciais em 4 sprints (8 semanas)  

---

## 🧱 Arquitetura

Abaixo, a representação da arquitetura da rede do ISP implementada no projeto:

![Arquitetura da Rede do ISP](./docs/arquitetura-isp.png)

---

## 📂 Estrutura de Diretórios

---

## 🛠️ Tecnologias Utilizadas

- Docker & Docker Compose  
- Bind9  
- Postfix + Dovecot  
- Nginx  
- Let's Encrypt (Certbot)    
- GitHub Projects (Kanban + Planejamento)  