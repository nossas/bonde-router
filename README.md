# DNS API

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

```sh
poetry run uvicorn --reload dns_api.api:app
```

### Testes

```sh
poetry run pytest
```

### Estrutura do projeto

```
dns_api/
├── dns_api/  # Código-fonte principal
│   ├── api.py
│   ├── route53.py
│   ├── settings.py
│   └── ...
├── tests/            # Testes unitários
│   ├── test_api_healthcheck.py
│   └── ...
├── pyproject.toml    # Configuração do Poetry
├── README.md         # Documentação do projeto
├── .env.example      # Exemplo de variáveis de ambiente
└── ...
```

## Endpoints

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