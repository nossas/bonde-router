from dns_api.route53 import Route53Client
from fastapi import FastAPI


app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.get("/hosted-zones")
async def hosted_zones():
    response = Route53Client().list_hosted_zones()
    return {"hosted_zones": response.get("HostedZones")}
