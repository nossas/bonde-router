import asyncio
import json

from caddy_api.manager.celery_app import app as celery
from caddy_api.manager.redis_client import client as redis_client
from caddy_api.manager.caddy_utils import load_config, save_config, update_caddy_config

CADDY_LOCK_KEY = "caddy_update_lock"
PENDING_OPERATIONS_KEY = "caddy:pending_operations_fifo"  # Fila FIFO


# Função para consolidar operações pendentes
def consolidate_operations():
    # Adquire o lock antes de consolidar as operações
    if redis_client.setnx(CADDY_LOCK_KEY, "locked"):
        # Inicializar listas para append e remove
        domains_to_add = set()
        domains_to_remove = set()

        try:
            domain_operations = dict() # Inicializa a variável fora do loop

            # Processa todas as operações na fila FIFO (lpop) enquanto existirem
            while True:
                operation_data = redis_client.rpop(PENDING_OPERATIONS_KEY)
                if not operation_data:
                    break  # Fim da fila

                # Decodifica a operação (json)
                operation, domains = json.loads(operation_data)

                for domain in domains:
                    # Registra a última operação do domínio
                    domain_operations[domain] = operation

            # Evita erro caso nenhuma operação seja processada
            if domain_operations:
                # Inicializar listas para adicionar e remover com base nas operações finais
                domains_to_add = {
                    domain for domain, op in domain_operations.items() if op == "append"
                }
                domains_to_remove = {
                    domain for domain, op in domain_operations.items() if op == "remove"
                }

        finally:
            # Libera o lock
            redis_client.delete(CADDY_LOCK_KEY)

        return domains_to_add, domains_to_remove
    else:
        raise Exception("Lock já existe. Tentando novamente mais tarde.")


# Task do Celery para processar alterações
@celery.task(
    bind=True, max_retries=3, name="caddy_api.manager.tasks.process_caddy_update"
)
def process_caddy_update(self):
    try:
        # Consolidar operações pendentes
        domains_to_add, domains_to_remove = consolidate_operations()

        if not domains_to_add and not domains_to_remove:
            return {"message": "Nenhuma operação pendente."}

        # Carregar configuração atual
        config = load_config()

        # Atualizar lista de hosts em route.bonde.public
        route = next(
            (
                r
                for r in config["apps"]["http"]["servers"]["srv0"]["routes"]
                if "@id" in r and r["@id"] == "route.bonde.public"
            ),
            None,
        )
        if route:
            hosts = set(route["match"][0].get("host", []))
            hosts.update(domains_to_add)
            hosts.difference_update(domains_to_remove)
            route["match"][0]["host"] = sorted(hosts)

        # Atualizar lista de subjects em policy.bonde.public
        policy = next(
            (
                p
                for p in config["apps"]["tls"]["automation"]["policies"]
                if "@id" in p and p["@id"] == "policy.bonde.ssl"
            ),
            None,
        )
        if policy:
            subjects = set(policy.get("subjects", []))
            subjects.update(domains_to_add)
            subjects.difference_update(domains_to_remove)
            policy["subjects"] = sorted(subjects)

        print(config)
        # Aplicar configuração atualizada no Caddy
        update_caddy_config(config)

        # Persistir configuração no arquivo JSON
        save_config(config)

        return {
            "message": f"Configuração atualizada com {len(domains_to_add)} adições e {len(domains_to_remove)} remoções.",
            "domains_added": len(domains_to_add),
            "domains_removed": len(domains_to_remove),
        }
    except Exception as e:
        # Tentativa de retry em caso de falha
        self.retry(exc=e)


# Função para adicionar operação pendente no Redis
async def add_pending_operation(
    operation: str, domains: list[str], max_retries: int = 5, retry_delay: int = 2
):
    """
    Adiciona uma operação de append ou remove ao Redis com tentativas automáticas se o lock já existir.

    :param operation: "append" ou "remove".
    :param domains: Lista de domínios para adicionar ou remover.
    :param max_retries: Número de tentativas caso operação esteja bloqueada, padrão 5.
    :param retry_delay: Tempo de espera em segundos entre as tentativas, padrão 2.
    """
    retries = 0
    while retries < max_retries:
        if redis_client.setnx(CADDY_LOCK_KEY, "locked"):
            try:
                # Adiciona a operação na fila FIFO com a operação e domínios
                operation_data = json.dumps([operation, domains])
                redis_client.rpush(PENDING_OPERATIONS_KEY, operation_data)

                print(f"Operação '{operation}' adicionada com sucesso à fila FIFO!")
                return  # Operação foi adicionada com sucesso
            finally:
                # Libera o lock
                redis_client.delete(CADDY_LOCK_KEY)
        else:
            # Lock já existe, aguarda e tenta novamente
            retries += 1
            print(
                f"Lock já existe. Tentando novamente em {retry_delay} segundos... ({retries}/{max_retries})"
            )
            await asyncio.sleep(retry_delay)

    # Se o número máximo de tentativas for atingido e não conseguiu adicionar a operação
    print(
        "Não foi possível adquirir o lock após várias tentativas. Operação não adicionada."
    )
