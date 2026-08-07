import ipaddress
import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class IpLookupError(RuntimeError):
    pass


def lookup_ip(value):
    try:
        ip = str(ipaddress.ip_address(value.strip()))
    except ValueError as error:
        raise IpLookupError("Adresa IP este invalidă.") from error

    request = Request(
        f"https://ipwho.is/{quote(ip)}",
        headers={
            "Accept": "application/json",
            "User-Agent": "NetCenter/4.6.0",
        },
    )

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except HTTPError as error:
        raise IpLookupError(
            f"Serviciul IP a răspuns cu eroarea HTTP {error.code}."
        ) from error
    except URLError as error:
        raise IpLookupError(
            f"Serviciul de informații IP nu este disponibil: {error.reason}"
        ) from error
    except (TimeoutError, json.JSONDecodeError) as error:
        raise IpLookupError(
            "Răspuns invalid sau expirat de la serviciul IP."
        ) from error

    if not payload.get("success", True):
        raise IpLookupError(
            payload.get("message") or "Nu există informații pentru acest IP."
        )

    connection = payload.get("connection") or {}
    security = payload.get("security") or {}
    timezone = payload.get("timezone") or {}

    return {
        "ip": ip,
        "type": payload.get("type", ""),
        "continent": payload.get("continent", ""),
        "country": payload.get("country", ""),
        "country_code": payload.get("country_code", ""),
        "region": payload.get("region", ""),
        "city": payload.get("city", ""),
        "postal": payload.get("postal", ""),
        "latitude": payload.get("latitude"),
        "longitude": payload.get("longitude"),
        "asn": connection.get("asn", ""),
        "organization": connection.get("org", ""),
        "isp": connection.get("isp", ""),
        "domain": connection.get("domain", ""),
        "timezone": timezone.get("id", ""),
        "utc": timezone.get("utc", ""),
        "proxy": security.get("proxy", False),
        "vpn": security.get("vpn", False),
        "tor": security.get("tor", False),
        "hosting": security.get("hosting", False),
    }
