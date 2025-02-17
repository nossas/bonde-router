# Use uma imagem base com Python
FROM python:3.12-slim

# Defina o diretório de trabalho no container
WORKDIR /app

# Instalar as dependências do Poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Copiar o arquivo pyproject.toml e poetry.lock (se existir) para o container
COPY pyproject.toml poetry.lock* /app/

# Instalar as dependências do projeto com Poetry
RUN poetry install

# Copiar o restante do código da aplicação para o container
COPY . /app/

# Não utilizamos EXPOSE e nem CMD pois essa imagem possui diversos serviços
# que podem ser executados diretamente pelo container
ENTRYPOINT ["poetry", "run"]

# Iniciar a API
# uvicorn caddy_api.api:app --reload

# Iniciar o Celery
# celery -A caddy_api.manager.celery_app.app worker --loglevel=info
