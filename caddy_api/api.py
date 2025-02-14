import asyncio
from celery.result import AsyncResult
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from pydantic import BaseModel

from caddy_api.manager.tasks import add_pending_operation, process_caddy_update


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)

MAX_RETRIES = 5  # Número máximo de tentativas
RETRY_DELAY = 2  # Delay entre as tentativas em segundos


# Modelo para as requisições de operações
class OperationRequest(BaseModel):
    operation: str  # Pode ser "append" ou "remove"
    domains: list  # Lista de domínios


# Endpoint para adicionar operações pendentes
@app.post("/add-operation")
async def add_operation(request: OperationRequest, background_tasks: BackgroundTasks):
    if request.operation not in ["append", "remove"]:
        raise HTTPException(
            status_code=400, detail="Operação inválida. Use 'append' ou 'remove'."
        )

    background_tasks.add_task(
        lambda: asyncio.run(
            add_pending_operation(
                request.operation,
                request.domains,
                max_retries=MAX_RETRIES,
                retry_delay=RETRY_DELAY,
            )
        )
    )
    return {"message": "Operação adicionada à fila."}


# Endpoint para processar o update no Caddy com rate limiting
@app.post("/process-update")
async def process_update(background_tasks: BackgroundTasks):
    """
    Dispara a task para processar a atualização do Caddy.
    """

    # Usar apply_async para agendar a execução da task e obter o task_id
    task = process_caddy_update.apply_async()
    return {"message": "Task de atualização processada.", "task_id": task.id}


# Endpoint para verificar o status de uma task
@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    if task_result.state == "PENDING":
        return {"status": "PENDING"}
    elif task_result.state == "SUCCESS":
        return {"status": "SUCCESS", "result": task_result.result}
    elif task_result.state == "FAILURE":
        return {"status": "FAILURE", "error": str(task_result.info)}
    return {"status": "UNKNOWN"}
