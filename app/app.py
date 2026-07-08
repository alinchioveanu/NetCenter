from flask import Flask, flash, redirect, render_template, request, url_for, Response, send_from_directory

from dnsmasq import DnsmasqManager
from routes.windows import bp as windows_bp
from routes.ipxe import bp as ipxe_bp
from routes.files import bp as files_bp
from routes.wimboot import bp as wimboot_bp
from routes.boot import boot
from database import init_db
from services.library import sync_library

app = Flask(__name__)
app.secret_key = "netcenter-local-only"

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

    reserved_macs = {r["mac"] for r in reservations}
    for lease in leases:
        lease["reserved"] = lease["mac"] in reserved_macs

    leases.sort(key=lambda item: (not item["reserved"], item["hostname"] or "zzz", item["ip"]))

    if query:
        leases = [l for l in leases if query in " ".join([l.get("hostname", ""), l.get("ip", ""), l.get("mac", "")]).lower()]
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

@app.route("/ipxe/<path:filename>")
def ipxe_files(filename):
    return send_from_directory("/app/ipxe", filename)

@app.route("/menu/<category>")
def menu_files(category):
    from services.menu_generator import generate_category_menu

    return (
        generate_category_menu(category),
        200,
        {"Content-Type": "text/plain"},
    )

@app.route("/lab")
def lab():
    return render_template("lab.html")

@app.route("/boot.ipxe")
def boot_ipxe():
    from services.menu_generator import generate_main_menu
    return generate_main_menu(), 200, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
