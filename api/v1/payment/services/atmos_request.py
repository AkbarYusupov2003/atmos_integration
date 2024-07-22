import base64
import requests
from django.conf import settings


def get_token():
    base64_token_bytes = base64.b64encode(
        f"{settings.ATMOS_CONSUMER_KEY}:{settings.ATMOS_CONSUMER_SECRET}".encode("utf-8")
    )
    base64_token_string = base64_token_bytes.decode("utf-8")
    response = requests.post(
        url="https://partner.atmos.uz/token",
        headers={
            "Authorization": f"Basic {base64_token_string}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "29",
            "Host": "partner.atmos.uz2",
        },
        data={"grant_type": "client_credentials"}
    ).json()
    if "access_token" in response.keys():
        return response["access_token"]
    else:
        return None


def get_headers(token):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "Host": "partner.atmos.uz",
        "Content-Length": "57",
    }


def post(url, data):
    token = get_token()
    if token:
        response = requests.post(
            url=url, headers=get_headers(token), json=data,
        )
        print("response: ", response.json())
        return response.json()
    else:
        return {"error": "failed to obtain token"}


def get(url, data):
    pass
