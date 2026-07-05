from flask import Flask, render_template, request
from dnsmasq import DnsmasqManager

app = Flask(__name__)

dns = DnsmasqManager()


@app.route("/")
def index():
    leases = dns.get_leases()

    for lease in leases:
        lease["reserved"] = dns.is_reserved(lease["mac"])

    return render_template(
        "index.html",
        leases=leases,
        reservations=dns.get_reservations()
    )

@app.route("/reserve", methods=["POST"])
def reserve():

    mac = request.form.get("mac")

    lease = dns.get_lease_by_mac(mac)

    return render_template(
        "reserve.html",
        lease=lease
    )

@app.route("/save", methods=["POST"])
def save():

    hostname = request.form.get("hostname")
    ip = request.form.get("ip")
    mac = request.form.get("mac")

    return f"""
Hostname: {hostname}<br>
IP: {ip}<br>
MAC: {mac}
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
