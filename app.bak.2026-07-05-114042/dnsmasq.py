from pathlib import Path

LEASES_FILE = Path("/var/lib/misc/dnsmasq.leases")
RESERVATIONS_FILE = Path("/etc/dnsmasq.d/20-reservations.conf")


class DnsmasqManager:

    def get_leases(self):
        leases = []

        if not LEASES_FILE.exists():
            return leases

        with LEASES_FILE.open() as f:
            for line in f:
                parts = line.strip().split()

                if len(parts) < 4:
                    continue

                leases.append({
                    "mac": parts[1],
                    "ip": parts[2],
                    "hostname": parts[3] if parts[3] != "*" else ""
                })

        return leases


    def get_reservations(self):
        reservations = []

        if not RESERVATIONS_FILE.exists():
            return reservations

        with RESERVATIONS_FILE.open() as f:
            for line in f:

                line = line.strip()

                if not line.startswith("dhcp-host="):
                    continue

                values = line.replace("dhcp-host=", "").split(",")

                if len(values) < 3:
                    continue

                reservations.append({
                    "mac": values[0],
                    "ip": values[1],
                    "hostname": values[2]
                })

        return reservations

    def is_reserved(self, mac):
        reservations = self.get_reservations()

        for reservation in reservations:
            if reservation["mac"].lower() == mac.lower():
                return True

        return False

    def get_lease_by_mac(self, mac):
        for lease in self.get_leases():
            if lease["mac"].lower() == mac.lower():
                return lease

        return None
