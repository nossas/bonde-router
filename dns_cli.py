import click

from dns_api.route53 import Route53Client
from dns_api.db import HostedZone

# with click.progressbar(range(total), label="Processando", file=None) as bar:
#         for i in bar:
#             time.sleep(0.1)  # Simulando um processo que demora 0.1 segundos por item
#             bar.update(1)


@click.command()
def sync_hosted_zones():
    """Sincroniza as Zonas de Hospedagem do Route 53 para o TinyDB."""
    hosted_zone_db = HostedZone()
    route53 = Route53Client().route53

    # Lista todas as zonas hospedagas
    paginator = route53.get_paginator("list_hosted_zones")

    for pos, page in enumerate(paginator.paginate()):
        with click.progressbar(
            range(len(page["HostedZones"])),
            label=f"Sincronizando página {pos + 1}",
            file=None,
        ) as bar:
            for zone in page["HostedZones"]:
                # Extrai o ID da zona hospedada
                zone_id = zone["Id"].split("/")[-1]

                # Obtém as tags associadas à zona hospedada
                response = route53.list_tags_for_resource(
                    ResourceType="hostedzone", ResourceId=zone_id
                )

                # Verifica se a tag desejada está presente
                tags = []
                for tag in response["ResourceTagSet"]["Tags"]:
                    tags.append({tag["Key"]: tag["Value"]})

                hosted_zone_db.upsert(
                    zone_id=zone_id,
                    **{
                        "id": zone_id,
                        "name": zone["Name"],
                        "caller_reference": zone["CallerReference"],
                        "tags": tags,
                    },
                )
                bar.update(1)


# Agrupando todos os comandos com um grupo principal
@click.group()
def cli():
    pass


# Registrando os comandos no grupo
cli.add_command(sync_hosted_zones)

# Rodando a aplicação de linha de comando
if __name__ == "__main__":
    cli()
