# 🌐 Projeto Final - ASA | Provedor de Serviços de Internet com Microsserviços

> Disciplina: Administração de Sistemas Abertos (ASA)  
> Professor: Sales Filho  
> Duração: 8 semanas  
> Instituição: IFRN - Campus Natal Central

## 👥 Equipe
<div align="center">
  
| Foto | Nome | GitHub |
|------|------|--------|
| <img src="https://github.com/eduardobezerraz.png" width="50"> | José Eduardo Bezerra de Medeiros | [@eduardobezerraz](https://github.com/eduardobezerraz) |
| <img src="https://github.com/joao-victor212.png" width="50"> | João Victor | [@joao-victor212](https://github.com/joao-victor212) |
| <img src="https://github.com/joaommcjm.png" width="50"> | João Marcos Medeiros Costa | [@joaommcjm](https://github.com/joaommcjm) |
| <img src="https://github.com/heysonsilva.png" width="50"> | Heyson Silva | [@heysonsilva](https://github.com/heysonsilva) |
</div>

## 📌 Descrição

Este projeto tem como objetivo a implementação de uma **infraestrutura para Provedor de Serviços de Internet (ISP)** utilizando **microsserviços e Docker**, aplicando os princípios de *Infrastructure as Code (IaC)* e *DevOps*. O sistema é modular, seguro e escalável, contemplando serviços como:

- **DNS**: Bind9 com zonas configuráveis  
- **E-mail**: Postfix (SMTP) + Dovecot (IMAP) + Roundcube  
- **Proxy**: Nginx com SSL/TLS automático  
- **Portais**: Hotsites e área do cliente  

**Destaques técnicos**:  
- Automação via scripts PowerShell e ShellScript
- Certificados SSL auto-gerados  
- Isolamento por cliente  
- Configuração IaC com Docker Compose
  
<div align="center">
  
## 🎯 Objetivos do projeto:

| Objetivo | Status |
|----------|:--------:|
| Desenvolver uma infraestrutura baseada em Docker para ISPs | [![Concluído](https://img.shields.io/badge/-Concluído-success)] |
| Isolar serviços por cliente usando Docker Networks e ACLs | [![Em Andamento](https://img.shields.io/badge/-Em_Andamento-yellow)] |
| Aplicar criptografia com HTTPS e STARTTLS | [![Bug](https://img.shields.io/badge/-Bug-critical)] |
| Criar testes automatizados e documentação em vídeo | [![Em Andamento](https://img.shields.io/badge/-Em_Andamento-yellow)] |
| Validar desempenho com métricas (latência, disponibilidade) | [![Não Iniciado](https://img.shields.io/badge/-Não_Iniciado-lightgrey)] |
| Cumprir entregas parciais em 4 sprints (8 semanas) | [![Em Andamento](https://img.shields.io/badge/-Em_Andamento-yellow)] |

</div>


## 🧱 Arquitetura

Abaixo, a representação da arquitetura da rede do ISP implementada no projeto:

![Arquitetura da Rede do ISP](./docs/arquitetura-isp.png)

---
## 📂 Explicação dos Diretórios do Projeto

### **[📁 clientes/](./clientes)**
Diretório que contém configurações específicas para cada cliente do provedor. Cada cliente possui:
- `hotsite/`: Site institucional básico
- `portal/`: Área de autoatendimento
- `proxy/`: Configurações de proxy dedicado

Arquivo principal:
- `docker-compose-clientes.yaml`: Configuração Docker para serviços dos clientes

### **[📁 DNS/](./DNS)**
Configurações do servidor DNS (Bind9) contendo:
- `Dockerfile`: Configuração do container
- `named.conf.local`: Definição das zonas DNS
- `sonserina.br`: Arquivo de zona DNS principal

### **[📁 docs/](./docs)**
Armazena toda a documentação do projeto:
- Diagramas de arquitetura
- Fluxogramas dos scripts
- Documentação complementar

### **[📁 email/](./email)**
Implementação completa de serviço de e-mail com:
- `Dockerfile`: Configuração principal
- `conf.d/`: Configurações adicionais
- `dovecot/`: Autenticação IMAP/POP3
- `postfix/`: Servidor SMTP
- `scripts/`: Scripts auxiliares

### **[📁 Portal/](./Portal)**
Portal institucional do provedor contendo:
- `Dockerfile`: Configuração do container
- `index.html`: Página web principal

### **[📁 proxy/](./proxy)**
Configurações do proxy reverso (Nginx) com:
- Arquivos de configuração principal
- Páginas de erro
- `ssl/`: Certificados digitais
  - Certificados raiz
  - Certificados por cliente

### **[📁 scripts/](./scripts)**
Scripts de automação para:
- Configuração de DNS
- Gerenciamento de rede
- Geração de certificados SSL
- Ativação/desativação de serviços

### **[📁 webmail/](./webmail)**
Interface web para e-mails (Roundcube) com:
- `config/`: Configurações de conexão
  - `config.inc.php`: Configuração principal

### **Arquivos Raiz Principais**
- `docker-compose.yml`: Orquestração central
- `startup.ps1`/`shutdown.ps1`: Scripts de controle
- `README.md`: Documentação principal

## 📂 Estrutura Completa do Projeto em fluxograma
```mermaid
flowchart LR
    root["📁 / (root)"] --> gitignore[".gitignore"]
    root --> compose["docker-compose.yml"]
    root --> estrutura["estrutura.txt"]
    root --> readme["README.md"]
    root --> shutdown["shutdown.ps1"]
    root --> startup["startup.ps1"]
    
    root --> clientes["📁 clientes"]
    clientes --> compose_clientes["docker-compose-clientes.yaml"]
    clientes --> cliente1["📁 cliente1"]
    cliente1 --> hotsite["📁 hotsite"]
    hotsite --> hotsite_dockerfile["Dockerfile"]
    hotsite --> hotsite_index["index.html"]
    cliente1 --> portal["📁 portal"]
    portal --> portal_dockerfile["Dockerfile"]
    portal --> portal_index["index.html"]
    cliente1 --> proxy["📁 proxy"]
    proxy --> proxy_conf["default.conf"]
    proxy --> proxy_dockerfile["Dockerfile"]
    
    root --> dns["📁 DNS"]
    dns --> dns_dockerfile["Dockerfile"]
    dns --> named_conf["named.conf.local"]
    dns --> sonserina_br["sonserina.br"]
    
    root --> docs["📁 docs"]
    docs --> arquitetura["arquitetura-isp.png"]
    docs --> shutdown_diag["fluxo_shutdown.png"]
    docs --> startup_diag["fluxo_startup.png"]
    
    root --> email["📁 email"]
    email --> email_dockerfile["Dockerfile"]
    email --> confd["📁 conf.d"]
    confd --> master_conf["10-master.conf"]
    email --> dovecot["📁 dovecot"]
    dovecot --> dovecot_conf["dovecot.conf"]
    email --> postfix["📁 postfix"]
    postfix --> postfix_conf["main.cf"]
    email --> scripts["📁 scripts"]
    scripts --> init_script["init.sh"]
    
    root --> portal_dir["📁 Portal"]
    portal_dir --> portal_dockerfile2["Dockerfile"]
    portal_dir --> portal_index2["index.html"]
    
    root --> proxy_dir["📁 proxy"]
    proxy_dir --> error_page["404.html"]
    proxy_dir --> proxy_conf2["default.conf"]
    proxy_dir --> proxy_dockerfile2["Dockerfile"]
    proxy_dir --> proxy_index["index.html"]
    proxy_dir --> ssl["📁 ssl"]
    ssl --> portal_crt["portal.cliente1.crt"]
    ssl --> portal_key["portal.cliente1.key"]
    ssl --> sonserina_crt["sonserina.crt"]
    ssl --> sonserina_key["sonserina.key"]
    
    root --> scripts_dir["📁 scripts"]
    scripts_dir --> dns_config["DNSconfig.ps1"]
    scripts_dir --> dhcp_config["EnableDHCP_Ipv6.ps1"]
    scripts_dir --> ssl_ps1["generate-ssl.ps1"]
    scripts_dir --> ssl_sh["generate-ssl.sh"]
    
    root --> webmail["📁 webmail"]
    webmail --> config["📁 config"]
    config --> config_inc["config.inc.php"]
```
---

## Pré-requisitos

- Docker e Docker Compose instalados
  - [Instruções para Windows](https://docs.docker.com/desktop/install/windows-install/)
  - [Instruções para Linux](https://docs.docker.com/engine/install/)
- PowerShell (Windows) ou PowerShell Core (Linux/Mac)
- Acesso de administrador/root

## Como Executar


1. Abra o PowerShell com privilégios administrativos (Executar como Administrador).

2. Navegue até o diretório onde os scripts estão salvos:

3. Execute o script de inicialização com o comando: 
```powershell
powershell -ExecutionPolicy Bypass -File .\startup.ps1
```

4. Execute o script de finalização com o comando: 
```powershell
powershell -ExecutionPolicy Bypass -File .\shutdown.ps1
```
## Fluxograma da lógica do script de inicialização:
```mermaid
flowchart TD
    A[Início: startup.ps1] --> B{Executando como Admin?}
    B -->|Sim| C[Verificar certificados SSL]
    B -->|Não| Z[ERRO: Encerrar]

    C --> D{Certificados existem?}
    D -->|Não| E[Executar generate-ssl.ps1]
    E --> F[Gerar ceritificados .crt e .key]
    F --> G[Instalar certificado?]
    G -->|Sim| H[Adicionar ao repositório de confiança]
    G -->|Não| I[Pular instalação]
    D -->|Sim| I

    I --> J[Iniciar containers Docker]
    J --> K[docker-compose up --force-recreate]
    K --> L{Sucesso?}
    L -->|Não| M[ERRO: Encerrar]
    L -->|Sim| N[Configurar DNS via DNSconfig.ps1]

    N --> O[Definir IP local como DNS]
    O --> P[Desativar IPv6]
    P --> Q[Exibir status dos containers]
    Q --> R[Finalizado!]
```

## Fluxograma da lógica do script de finalização:
```mermaid
flowchart TD
    A[Início: shutdown.ps1] --> B{Executando como Admin?}
    B -->|Sim| C[Parar containers Docker]
    B -->|Não| Z[ERRO: Encerrar]

    C --> D{docker-compose down\nsucesso?}
    D -->|Sim| E[Executar EnableDHCP_Ipv6.ps1]
    D -->|Não| F[AVISO: Erro ao parar containers]

    E --> G{DHCP/IPv6 reativados?}
    G -->|Sim| H[Exibir mensagem de sucesso]
    G -->|Não| I[AVISO: Erro no script DHCP]

    H --> J[Fim: Todos serviços desligados]
    F --> J
    I --> J
```
