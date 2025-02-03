import boto3
from dns_api import settings


class Route53Client:

    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

    def list_hosted_zones(self):
        return self.session.client("route53").list_hosted_zones()