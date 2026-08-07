import ipaddress
import json
import socket

SOCKET_PATH = "/run/netcenter-crowdsec/api.sock"
MAX_RESPONSE_SIZE = 10 * 1024 * 1024


class CrowdSecError(RuntimeError):
    pass


def _request(payload):
    raw_request = json.dumps(payload).encode("utf-8") + b"\n"
    response_data = b""

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(20)
            client.connect(SOCKET_PATH)
            client.sendall(raw_request)

            while not response_data.endswith(b"\n"):
                chunk = client.recv(65536)

                if not chunk:
                    break

                response_data += chunk

                if len(response_data) > MAX_RESPONSE_SIZE:
                    raise CrowdSecError("Răspunsul CrowdSec este prea mare.")

    except OSError as error:
        raise CrowdSecError(
            f"Serviciul CrowdSec nu este disponibil: {error}"
        ) from error

    if not response_data:
        raise CrowdSecError("Serviciul CrowdSec nu a returnat niciun răspuns.")

    try:
        response = json.loads(response_data)
    except json.JSONDecodeError as error:
        raise CrowdSecError("Răspuns CrowdSec invalid.") from error

    if not response.get("ok"):
        raise CrowdSecError(
            response.get("error") or "Operația CrowdSec a eșuat."
        )

    return response


def get_banned_ips():
    response = _request({"action": "list"})
    alerts = response.get("data") or []
    decisions = []

    for alert in alerts:
        source = alert.get("source") or {}
        country = source.get("cn", "")
        as_name = source.get("as_name", "")

        for decision in alert.get("decisions") or []:
            if decision.get("type") != "ban":
                continue

            decisions.append({
                "id": decision.get("id"),
                "ip": decision.get("value", ""),
                "scope": decision.get("scope", ""),
                "type": decision.get("type", ""),
                "origin": decision.get("origin", ""),
                "scenario": decision.get("scenario")
                            or alert.get("scenario", ""),
                "duration": decision.get("duration", ""),
                "created_at": alert.get("created_at", ""),
                "country": country,
                "as_name": as_name,
            })

    decisions.sort(
        key=lambda item: (
            item["country"],
            item["ip"],
            item["scenario"],
        )
    )

    return decisions


def unblock_ip(value):
    try:
        ip = str(ipaddress.ip_address(value.strip()))
    except ValueError as error:
        raise CrowdSecError("Adresa IP este invalidă.") from error

    response = _request({
        "action": "delete",
        "ip": ip,
    })

    return response.get(
        "message",
        f"IP-ul {ip} a fost deblocat.",
    )


def block_ip(value, duration="24h", reason="Blocare manuală din NetCenter"):
    try:
        ip = str(ipaddress.ip_address(value.strip()))
    except ValueError as error:
        raise CrowdSecError("Adresa IP este invalidă.") from error

    allowed_durations = {
        "1h",
        "4h",
        "12h",
        "24h",
        "72h",
        "168h",
        "720h",
    }

    if duration not in allowed_durations:
        raise CrowdSecError("Durata selectată nu este permisă.")

    reason = reason.strip()[:120]

    if not reason:
        reason = "Blocare manuală din NetCenter"

    response = _request({
        "action": "add",
        "ip": ip,
        "duration": duration,
        "reason": reason,
    })

    return response.get(
        "message",
        f"IP-ul {ip} a fost blocat pentru {duration}.",
    )
