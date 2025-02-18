# Bonde Router

Este projeto fornece um conjunto de APIs para gerenciar roteamentos na plataforma BONDE, integrando Caddy, Let's Encrypt/ZeroSSL e Route53. Ele automatiza a criação e manutenção de domínios, certificados SSL e regras de tráfego, garantindo escalabilidade e segurança para aplicações distribuídas.

## Instalação e Configuração

### Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Python 3.12+
- Poetry

### Instalando as Dependências

```sh
poetry install
```

### Configuração do Ambiente

#### Configurando o Docker Compose para Desenvolvimento

1. Copie o arquivo `.env.example` e configure as variáveis de ambiente conforme necessário:

```sh
cp .env.example .env
```

2. Crie uma pasta `data/caddy/` na raiz do repositório e copie a configuração inicial do Caddy:

```sh
mkdir -p data/caddy
cp caddy.json data/caddy/
```

#### Configurando a API Caddy

Copie o arquivo `caddy_api/.env.example` e configure as variáveis de ambiente conforme necessário:

```sh
cp caddy_api/.env.example caddy_api/.env
```

#### Configurando a API DNS

Copie o arquivo `dns_api/.env.example` e configure as variáveis de ambiente conforme necessário:

```sh
cp dns_api/.env.example dns_api/.env
```

### Executando o Projeto

#### Estrutura de Desenvolvimento com Docker Compose

```sh
docker compose up -d --build
```

Para executar a validação dos seus certificados localmente, siga a documentação do Caddy (https://caddyserver.com/docs/running#local-https-with-docker).

#### Iniciando a API Caddy

```sh
poetry run uvicorn caddy_api.api:app --reload
```

#### Iniciando o Celery

```sh
poetry run celery -A caddy_api.manager.celery_app.app worker --loglevel=info
```

#### Iniciando a API DNS

```sh
poetry run uvicorn --reload dns_api.api:app
```

### Testes

Execute os testes utilizando o comando:

```sh
poetry run pytest
```

## Estrutura do Projeto

```plaintext
bonde-router/
├── caddy_api/              # Código-fonte principal da API Caddy
│   ├── manager/            # Código-fonte do gerenciador Caddy
│   │   ├── caddy_utils.py  # Funções para atualizar configurações do Caddy e persistir no arquivo JSON
│   │   ├── tasks.py        # Tarefas para gerenciar disponibilidade de operações no Caddy com Redis e Celery
│   │   └── ...
|   ├── .env.example        # Exemplo de variáveis de ambiente
│   ├── api.py              # API principal exposta para realizar operações no Caddy
│   ├── settings.py
│   └── ...
├── dns_api/                # Código-fonte principal da API de DNS
│   ├── api.py
│   ├── route53.py
│   ├── settings.py
│   └── ...
├── tests_dns/              # Testes unitários
│   ├── test_api_healthcheck.py
│   └── ...
├── .env.example            # Exemplo de variáveis de ambiente
├── dns_cli.py              # Comandos para sincronização de dados
├── check_domains.py        # Script para verificar configurações do domínio
├── pyproject.toml          # Configuração do Poetry
├── README.md               # Documentação do projeto
└── ...
```

## CLI

Este projeto utiliza a biblioteca [Click](https://click.palletsprojects.com/en/stable/) para criação de uma CLI. Você pode sempre chamar utilizando `python dns_cli.py [COMMAND]`. Abaixo está a lista de comandos:

### `sync-hosted-zones`

Sincroniza as Zonas de Hospedagem do Route 53 para o TinyDB (base de dados local).

### `update-hosted-zones`

Atualiza o Route53 com a tag `ExternalGroupId` de acordo com o CSV (`--csvfile`) fornecido.

**Exemplo de Arquivo CSV**

```csv
zone_id,name,external_group_id
/hostedzone/Z03535501MSN9R17CEXFD,meudomain.com.,659
```

### `python check_domains_cli.py`

Confere configurações de domínios passados por um arquivo, que pode ser chamado opcionalmente de `input.csv`. O resultado é salvo em um arquivo de saída, como `output.csv`. Lembre-se de configurar a variável de ambiente `SERVER_IP` em sua linha de comando: `export SERVER_IP='0.0.0.0'`.

**Comando para checar os domínios**

```bash
python check_domains.py check-domains --csvfile input.csv --output output.csv --statefile progress.json
```

**Comando para checar os certificados SSL**

```bash
python check_domains.py check-ssl --csvfile input.csv --output ssl_output.csv
```

**Exemplo de Arquivo input.csv**

```csv
id,name,slug,custom_domain,root_domain
1357,Dónde están los 200 mil millones de pesos?,200milmillones,www.200milmillones.com,200milmillones.com
714,#AconteceuNoCarnaval,aconteceunocarnaval,www.aconteceunocarnaval.org,aconteceunocarnaval.org
```

Considere montar o arquivo de input de forma ordenada por `root_domain`. Abaixo um exemplo de SQL para gerar o arquivo:

```sql
SELECT *
FROM (
    SELECT
        m.id,
        m.name,
        m.slug,
        m.custom_domain,
        REGEXP_REPLACE(
            m.custom_domain,
            '^(?:.*?\.)?([^\.]+\.(?:org\.br|org|com\.br|com|com\.mx|org\.mx|biz|tk|net|me|co|site|tec.br|online))$',
            '\1'
        ) AS root_domain
    FROM mobilizations m
    WHERE m.status = 'active'
      AND m.custom_domain IS NOT NULL
    ORDER BY m.id
) AS sq
ORDER BY sq.root_domain;
```

## Endpoints DNS API

### `/healthcheck`

Verifica a saúde do sistema.

### `/hosted-zones`

Recupera uma lista de Zonas de Hospedagem de acordo com o `ExternalGroupId` configurado em suas Tags. Caso o parâmetro não seja passado, retorna uma lista vazia.

**Método:** GET

**Parâmetros:** `external_group_id` (opcional)

**Exemplo de Resposta:**

```json
{
    "hosted_zones": []
}
```

## Endpoints Caddy API

### Informações Gerais

Todos os endpoints requerem autenticação. A autenticação pode ser feita utilizando o cabeçalho `Authorization` com um token de acesso válido, ou enviando um `Cookie` contendo as credenciais de autenticação.

**Exemplo de Cabeçalho:**
```http
Authorization: Bearer <seu_token_aqui>
```

**Exemplo de Cooke:**
```http
Cookie: session=<seu_token_aqui>
```

Você pode integrar sua API com o BONDE utilizando o Hasura Actions (`/add-operation` e `/task-status`) e Hasura Events (`/process-update`).

---

### `/add-operation`

Enfilera uma operação de adicionar ou remover domínio das configurações do Caddy. Funciona de maneira assíncrona.

**Método:** POST

**Parâmetros:**
- `domains`: Lista de domínios.
- `operation`: Operação a ser realizada (`append` ou `remove`).

**Exemplo de Resposta:**

```json
{
    "message": "Operação adicionada à fila"
}
```

### `/process-update`

Dispara a task para processar a atualização das configurações da fila no Caddy. Funciona de maneira assíncrona.

**Método:** POST

**Exemplo de Resposta:**

```json
{
    "message": "",
    "task_id": ""
}
```

### `/task-status/{task_id}`

Consulta o resultado da tarefa enviada para o processamento no Celery.

**Método:** GET

**Exemplo de Resposta:**

```json
{
    "status": "PENDING" | "SUCCESS" | "FAILURE" | "UNKNOWN",
    "result": {},
    "error": ""
}
```

## Informações úteis

Primeira saída do comando de atualização das tags Bonde > Route53 (2025-02-04 11:18)

```
Atualizando  [##----------------------------------]    7%  00:01:11HostedZone temgentecomfome.com.br não encontrado: An error occurred (NoSuchHostedZone) when calling the ChangeTagsForResource operation: No hosted zone found with ID: Z08299121AAPDD5RD7VTZ
Atualizando  [##################------------------]   51%  00:00:23HostedZone nossas.tec.br não encontrado: An error occurred (NoSuchHostedZone) when calling the ChangeTagsForResource operation: No hosted zone found with ID: Z06477672SR3T7T45E29C
Atualizando  [#####################---------------]   58%  00:00:20HostedZone mapadoacolhimento.org.br não encontrado: An error occurred (NoSuchHostedZone) when calling the ChangeTagsForResource operation: No hosted zone found with ID: Z20DVY8WSZQG1E
Atualizando  [#########################-----------]   72%  00:00:13HostedZone bonde.datad.at não encontrado: An error occurred (NoSuchHostedZone) when calling the ChangeTagsForResource operation: No hosted zone found with ID: Z0450040OQL7IUSSQXTY
Atualizando  [################################----]   89%  00:00:05HostedZone virada.amazoniadepe.org.br não encontrado: An error occurred (NoSuchHostedZone) when calling the ChangeTagsForResource operation: No hosted zone found with ID: Z07920232OV5GQFPMKYK7
Atualizando  [##################################--]   96%  00:00:01HostedZone votepeloclima.org não encontrado: An error occurred (NoSuchHostedZone) when calling the ChangeTagsForResource operation: No hosted zone found with ID: Z03535501MSN9R17CEXFD
Atualizando  [####################################]  100%       
```

## O que será desenvolvido?

Será desenvolvido uma aplicação capaz de fazer chamadas no Route53 para listar, alterar, adicionar e remover Zonas de Hospedagem e Registros, com uma camada de de cachê para evitar chamadas excessivas na API do Route53.

Este sistema deve seguir as seguintes regras:

- Deve apresentar uma interface que possa ser consumida tanto por um website, quanto por um aplicativo para dispositivos móveis
- Deve prover um endpoint que indique a saúde do sistema
- Dado uma Comunidade, retornar suas Zonas de Hospedagem
- Dado uma Zona de Hospedagem, retornar seus Registros
- Deve apresentar boa documentação
- O sistema deve apresentar testes
- O sistema deve possuir uma rotina de atualização da base de dados local