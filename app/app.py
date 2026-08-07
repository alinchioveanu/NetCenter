import ipaddress
import json
import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from dnsmasq import DnsmasqManager
from routes.windows import bp as windows_bp
from routes.ipxe import bp as ipxe_bp
from routes.files import bp as files_bp
from routes.wimboot import bp as wimboot_bp
from routes.boot import boot
from database import init_db
from services.library import sync_library
from crowdsec import CrowdSecError, block_ip, get_banned_ips, unblock_ip
from ip_lookup import IpLookupError, lookup_ip

app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "change-this-secret",
)

app.register_blueprint(windows_bp)
app.register_blueprint(ipxe_bp)
app.register_blueprint(files_bp)
app.register_blueprint(wimboot_bp)
app.register_blueprint(boot)

dns = DnsmasqManager()
init_db()
sync_library()

@app.route("/")
def index():
    query = request.args.get("q", "").strip().lower()
    leases = dns.get_leases()
    reservations = dns.get_reservations()
    leases = dns.enrich_device_names(leases, reservations)
    leases = dns.refresh_last_seen(leases)

    reserved_macs = {r["mac"] for r in reservations}
    for lease in leases:
        lease["reserved"] = lease["mac"] in reserved_macs

    leases.sort(
        key=lambda item: (
            not item["reserved"],
            item.get("user_name") or item.get("device_name") or "zzz",
            item["ip"],
        )
    )

    if query:
        leases = [
            lease
            for lease in leases
            if query in " ".join([
                lease.get("device_name", ""),
                lease.get("user_name", ""),
                lease.get("hostname", ""),
                lease.get("ip", ""),
                lease.get("mac", ""),
            ]).lower()
        ]
        reservations = [r for r in reservations if query in " ".join([r.get("hostname", ""), r.get("ip", ""), r.get("mac", "")]).lower()]

    return render_template(
        "index.html",
        leases=leases,
        reservations=reservations,
        query=query,
        stats={
            "leases": len(leases),
            "reservations": len(reservations),
        },
    )

@app.route("/dhcp/device/<ip>")
def dhcp_device(ip):
    try:
        ip = str(ipaddress.IPv4Address(ip))
    except ipaddress.AddressValueError:
        flash("Adresa IP nu este validă.", "danger")
        return redirect(url_for("index"))

    leases = dns.get_leases()
    lease = next(
        (
            item
            for item in leases
            if item["ip"] == ip
        ),
        None,
    )

    if lease is None:
        flash(
            "Dispozitivul nu mai apare în lease-urile DHCP.",
            "warning",
        )
        return redirect(url_for("index"))

    reservations = dns.get_reservations()
    enriched = dns.enrich_device_names(
        [lease],
        reservations,
    )
    lease = dns.refresh_last_seen(enriched)[0]

    reservation = next(
        (
            item
            for item in reservations
            if item["mac"] == lease["mac"]
        ),
        None,
    )

    detection_source = ""

    try:
        hardware_data = json.loads(
            Path(
                "/var/lib/misc/"
                "netcenter-device-models.json"
            ).read_text(encoding="utf-8")
        )

        hardware = hardware_data.get(
            "devices",
            {},
        ).get(
            lease["mac"],
            {},
        )

        detection_source = hardware.get("source", "")
    except (OSError, ValueError, TypeError):
        detection_source = ""

    if (
        not detection_source
        and lease.get("device_name")
    ):
        detection_source = "Hostname DHCP memorat"

    return render_template(
        "dhcp_device.html",
        lease=lease,
        reservation=reservation,
        detection_source=detection_source,
    )


@app.route("/images")
def images():
    from database import get_db

    conn = get_db()

    images = conn.execute("""
        SELECT *
        FROM boot_images
        ORDER BY
            category,
            sort_order,
            name
    """).fetchall()

    conn.close()

    from services.windows import is_image_imported

    images = [dict(image) for image in images]

    for image in images:
        image["imported"] = is_image_imported(image)

    return render_template(
        "images.html",
        images=images
    )

@app.route("/profiles")
def profiles():
    from services.profiles import get_profiles

    return render_template(
        "profiles.html",
        profiles=get_profiles()
    )



@app.route("/reserve", methods=["POST"])
def reserve():
    mac = request.form.get("mac", "").strip()
    reservation = dns.get_reservation_by_mac(mac)
    lease = dns.get_lease_by_mac(mac)

    if reservation:
        lease = reservation
    elif lease is None:
        flash("Dispozitivul nu a fost găsit.", "danger")
        return redirect(url_for("index"))

    return render_template("reserve.html", lease=lease, edit=bool(reservation))


@app.route("/new")
def new_reservation():
    lease = {"hostname": "", "ip": "192.168.100.", "mac": ""}
    return render_template("reserve.html", lease=lease, edit=False)


@app.route("/save", methods=["POST"])
def save():
    hostname = request.form.get("hostname", "").strip()
    ip = request.form.get("ip", "").strip()
    mac = request.form.get("mac", "").strip()

    success, message = dns.save_reservation(hostname=hostname, ip=ip, mac=mac)
    flash(message, "success" if success else "danger")
    return redirect(url_for("index"))


@app.route("/delete", methods=["POST"])
def delete():
    mac = request.form.get("mac", "").strip()
    success, message = dns.delete_reservation(mac)
    flash(message, "success" if success else "danger")
    return redirect(url_for("index"))


@app.route("/crowdsec")
def crowdsec():
    try:
        decisions = get_banned_ips()
        error = None
    except CrowdSecError as exc:
        decisions = []
        error = str(exc)

    return render_template(
        "crowdsec.html",
        decisions=decisions,
        error=error,
    )


@app.route("/crowdsec/ip/<path:ip>")
def crowdsec_ip(ip):
    try:
        details = lookup_ip(ip)
        error = None
    except IpLookupError as exc:
        details = {"ip": ip}
        error = str(exc)

    return render_template(
        "crowdsec_ip.html",
        details=details,
        error=error,
    )



@app.route("/crowdsec/block", methods=["POST"])
def crowdsec_block():
    ip = request.form.get("ip", "").strip()
    duration = request.form.get("duration", "24h").strip()
    reason = request.form.get(
        "reason",
        "Blocare manuală din NetCenter",
    ).strip()

    try:
        message = block_ip(
            ip,
            duration=duration,
            reason=reason,
        )
        flash(message, "success")
    except CrowdSecError as exc:
        flash(str(exc), "danger")

    return redirect(url_for("crowdsec"))



@app.route("/crowdsec/unblock", methods=["POST"])
def crowdsec_unblock():
    ip = request.form.get("ip", "").strip()

    try:
        message = unblock_ip(ip)
        flash(message, "success")
    except CrowdSecError as exc:
        flash(str(exc), "danger")

    return redirect(url_for("crowdsec"))


@app.route("/lab")
def lab():
    return render_template("lab.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
