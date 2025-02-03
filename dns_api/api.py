from dns_api.route53 import Route53Client
from fastapi import FastAPI


app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.get("/hosted-zones")
async def hosted_zones(external_group_id: str | None = None):
    hosted_zones = Route53Client().list_hosted_zones(external_group_id=external_group_id)
    return {"hosted_zones": hosted_zones}
