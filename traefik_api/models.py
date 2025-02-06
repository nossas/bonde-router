from pydantic import BaseModel


class Router(BaseModel):
    # Serviço Docker usado para configurar o destino do Roteador
    service: str
    # Endereço utilizado para configurar o Roteador
    domain_name: str