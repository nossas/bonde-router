# Bonde Router

Este projeto fornece um conjunto de APIs para gerenciar roteamentos na plataforma BONDE, integrando Traefik, Let's Encrypt e Route53. Ele automatiza a criação e manutenção de domínios, certificados SSL e regras de tráfego, garantindo escalabilidade e segurança para aplicações distribuídas.

## Instalação e Configuração

### Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Python 3.12+
- Poetry

### Instalando as Dependências

```sh
poetry install
```

### Configuração do ambiente

Copie o arquivo `.env.example` e configure as variáveis de ambiente:

```sh
cp .env.example dns_api/.env
```

Edite o arquivo `.env` conforme necessário.

### Executando o projeto

DNS API

```sh
poetry run uvicorn --reload dns_api.api:app
```

Traefik API

```sh
poetry run uvicorn --reload traefik_api.api:app
```

### Testes

```sh
poetry run pytest
```

### Estrutura do projeto

```
bonde-router/
├── dns_api/  # Código-fonte principal da API de DNS
│   ├── api.py
│   ├── route53.py
│   ├── settings.py
│   └── ...
├── tests_dns/            # Testes unitários
│   ├── test_api_healthcheck.py
│   └── ...
├── tests_traefik/        # Testes unitários
│   ├── test_api_healthcheck.py
│   └── ...
├── traefik_api/  # Código-fonte principal da API pro Traefik
│   ├── api.py
│   ├── models.py
│   └── ...
├── .env.example      # Exemplo de variáveis de ambiente
├── dns_cli.py        # Comandos para sincronização de dados
├── pyproject.toml    # Configuração do Poetry
├── README.md         # Documentação do projeto
└── ...
```

## CLI

Foi utilizado a biblioteca [click](https://click.palletsprojects.com/en/stable/) para criação de uma CLI. Você pode sempre chamar utilizando `python dns_cli.py [COMMAND]`, abaixo a lista de comandos:

- `sync-hosted-zones` Sincroniza as Zonas de Hospedagem do Route 53 para o TinyDB (Base de dados local).
- `update-hosted-zones` Atualiza Route53 com a tag ExternalGroupId de acordo com CSV (`--csvfile`) passado.

    Exemplo de arquivo csv
    ```csv
    zone_id,name,external_group_id
    /hostedzone/Z03535501MSN9R17CEXFD,meudomain.com.,659
    ```

## Endpoints DNS API

- `/healthcheck`

- `/hosted-zones`
    
    Recupera uma lista de Zona de Hospedagem de acordo com o `ExternalGroupId` configurado em suas Tags. Caso parâmetro não seja pasado retorna uma lista vazia.
    
    **Método:** GET

    **Parâmetros:** `external_group_id` (optional)
    
    **Resposta:**
    ```json
    {
        "hosted_zones": []
    }
    ```

## Endpoints Traefik API

- `/healthcheck`

- `/create-router`

    Criar configurações de roteamento no Traefik.

    **Método:** POST

    **Parâmetros:** `router.domain_name` (required), `router.service` (required)

    **Resposta:**
    ```json
    {
        "status": "ok"
    }
    ```

- `/delete-router/{domain_name}`

    Remove configurações de roteamento no Traefik.

    **Método:** DELETE

    **Parâmetros:** `domain_name` (required)

    **Resposta:**
    ```json
    {
        "status": "ok"
    }
    ```

# Informações úteis

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

# O que será desenvolvido?

Será desenvolvido uma aplicação capaz de fazer chamadas no Route53 para listar, alterar, adicionar e remover Zonas de Hospedagem e Registros, com uma camada de de cachê para evitar chamadas excessivas na API do Route53.

Este sistema deve seguir as seguintes regras:

- Deve apresentar uma interface que possa ser consumida tanto por um website, quanto por um aplicativo para dispositivos móveis
- Deve prover um endpoint que indique a saúde do sistema
- Dado uma Comunidade, retornar suas Zonas de Hospedagem
- Dado uma Zona de Hospedagem, retornar seus Registros
- Deve apresentar boa documentação
- O sistema deve apresentar testes
- O sistema deve possuir uma rotina de atualização da base de dados local