import datetime

from dns_api import settings


class Database:
    __filename__ = None

    def __init__(self):
        # Use import this to make mocker in pytest
        from tinydb import TinyDB, Query

        self.db = TinyDB(settings.BASE_DIR / f"db/{self.__filename__}.json")
        self.query = Query()


class HostedZone(Database):
    __filename__ = "route53_hosted_zones"

    def upsert(self, zone_id: str, **values):
        """Insere ou Atualiza a Zona de Hospedagem no banco de dados"""
        self.db.upsert(
            {
                "id": zone_id,
                **values,
                # 'name': zone_name,
                # 'caller_reference': caller_reference,
                # 'tags': tags,
                # 'last_updated': datetime.utcnow().isoformat()
            },
            self.query.id == zone_id,
        )

    def get_all(self, tag_value):
        """Busca Zonas de Hospedagem por tag no TinyDB"""
        return self.db.search((self.query.tags.any({"ExternalGroupId": tag_value})))


class Healthcheck(Database):
    __filename__ = "healthcheck"

    def sync_updated_on(self, sync_name: str):
        self.db.upsert(
            {"updated_on": datetime.datetime.now().isoformat(), "sync_name": sync_name},
            self.query.sync_name == sync_name,
        )
