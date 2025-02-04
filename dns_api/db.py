from dns_api import settings
from tinydb import TinyDB, Query


class Database:

    def __init__(self, name: str):
        self.db = TinyDB(settings.BASE_DIR / f"db/{name}.json")
    

class HostedZone(Database):

    def __init__(self):
        super().__init__(name="route53_hosted_zones")
    
    def upsert(self, zone_id: str, **values):
        """Insere ou Atualiza a Zona de Hospedagem no banco de dados"""
        self.db.upsert({
            'id': zone_id,
            **values
            # 'name': zone_name,
            # 'caller_reference': caller_reference,
            # 'tags': tags,
            # 'last_updated': datetime.utcnow().isoformat()
        }, Query().id == zone_id)
    
    def get_all(self, tag_value):
        """Busca Zonas de Hospedagem por tag no TinyDB"""
        HostedZone = Query()
        return self.db.search(
            (HostedZone.tags.any({"ExternalGroupId": tag_value}))
        )