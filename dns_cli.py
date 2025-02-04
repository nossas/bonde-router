import click
import csv

from dns_api.route53 import Route53Client
from dns_api.db import HostedZone


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


@click.command()
@click.option(
    "--csvfile",
    help="Caminho para o arquivo CSV utilizado na atualização. Formato: zone_id,name,external_group_id",
)
def update_hosted_zones(csvfile):
    """Atualiza Route53 com a tag ExternalGroupId"""
    route53 = Route53Client().route53
    total = 0
    with open(csvfile, mode="r", encoding="utf-8") as file:
        # Ler o arquivo CSV como dicionário
        total = sum(1 for _ in csv.DictReader(file)) - 1

    with open(csvfile, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        with click.progressbar(
            range(total),
            label=f"Atualizando",
            file=None,
        ) as bar:
            for row in reader:
                try:
                    # Atualiza a Zona de Hospedagem com Tag no Route53
                    route53.change_tags_for_resource(
                        ResourceType="hostedzone",
                        ResourceId=row["zone_id"].split("/")[-1],
                        AddTags=[
                            {
                                "Key": "ExternalGroupId",
                                "Value": row["external_group_id"],
                            }
                        ],
                    )
                except route53.exceptions.NoSuchHostedZone as err:
                    click.echo(f"HostedZone {row['name']} não encontrado: {err}")

                bar.update(1)


# Agrupando todos os comandos com um grupo principal
@click.group()
def cli():
    pass


# Registrando os comandos no grupo
cli.add_command(sync_hosted_zones)
cli.add_command(update_hosted_zones)

# Rodando a aplicação de linha de comando
if __name__ == "__main__":
    cli()
