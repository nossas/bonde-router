from celery import Celery

# Configuração do Celery com Redis
app = Celery(
    "caddy_manager",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

# Configuração Celery (opcional: para controlar retries, timeouts, etc.)
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.worker_max_tasks_per_child = 100
app.conf.task_annotations = {
    "*": {"rate_limit": "1/s"}
}  # Rate limit de 1 tarefa por segundo


# Descobrir e registrar tarefas nos módulos especificados
app.autodiscover_tasks(["caddy_api.manager"])