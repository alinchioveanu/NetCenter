from flask import Flask, flash, redirect, render_template, request, url_for

from dnsmasq import DnsmasqManager

app = Flask(__name__)
app.secret_key = "netcenter-local-only"

dns = DnsmasqManager()


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
