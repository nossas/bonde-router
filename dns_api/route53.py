import boto3
from dns_api import settings


class Route53Client:

    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        self.route53 = self.session.client("route53")

    def list_hosted_zones(self, external_group_id: str | None):
        if external_group_id:
            # Lista todas as zonas hospedagas
            paginator = self.route53.get_paginator("list_hosted_zones")
            filtered_zones = []

            for page in paginator.paginate():
                for zone in page["HostedZones"]:
                    # Extrai o ID da zona hospedada
                    zone_id = zone["Id"].split("/")[-1]

                    # Obtém as tags associadas à zona hospedada
                    response = self.route53.list_tags_for_resource(
                        ResourceType="hostedzone", ResourceId=zone_id
                    )

                    # Verifica se a tag desejada está presente
                    for tag in response["ResourceTagSet"]["Tags"]:
                        if tag["Key"] == "ExternalGroupId" and tag["Value"] == str(
                            external_group_id
                        ):
                            filtered_zones.append(zone)
                            break

            return filtered_zones

        return []
