from celery import Celery
from caddy_api import settings

# Configuração do Celery com Redis
REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

app = Celery(
    "caddy_manager",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Configuração Celery (opcional: para controlar retries, timeouts, etc.)
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.worker_max_tasks_per_child = 100
app.conf.task_annotations = {
    "*": {"rate_limit": "1/s"}
}  # Rate limit de 1 tarefa por segundo
app.conf.result_expires = 3600  # Resultados são apagados 1 hora após a conclusão


# Descobrir e registrar tarefas nos módulos especificados
app.autodiscover_tasks(["caddy_api.manager"])
