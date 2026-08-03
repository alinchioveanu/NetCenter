from __future__ import annotations

import ipaddress
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from system import SystemManager

LEASES_FILE = Path(os.getenv("LEASES_FILE", "/var/lib/misc/dnsmasq.leases"))
RESERVATIONS_FILE = Path(os.getenv("RESERVATIONS_FILE", "/etc/dnsmasq.d/20-reservations.conf"))
DNSMASQ_TEST_CMD = os.getenv("DNSMASQ_TEST_CMD", "dnsmasq --test")
DNSMASQ_RESTART_CMD = os.getenv("DNSMASQ_RESTART_CMD", "systemctl restart dnsmasq")

MAC_RE = re.compile(r"^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}$")
HOST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,62}$")


@dataclass
class Reservation:
    mac: str
    ip: str
    hostname: str
    lease: str = "infinite"

    def to_line(self) -> str:
        return f"dhcp-host={self.mac},{self.ip},{self.hostname},{self.lease}"


class DnsmasqManager:
    def __init__(self):
        self.leases_file = LEASES_FILE
        self.reservations_file = RESERVATIONS_FILE

    def normalize_mac(self, mac: str) -> str:
        return (mac or "").strip().lower()

    def normalize_hostname(self, hostname: str) -> str:
        hostname = (hostname or "").strip()
        if not hostname or hostname == "*":
            return "unknown-device"
        return hostname.replace(" ", "-")

    def validate_mac(self, mac: str) -> tuple[bool, str]:
        if not MAC_RE.match(mac or ""):
            return False, "Adresa MAC nu este validă."
        return True, "OK"

    def validate_ip(self, ip: str) -> tuple[bool, str]:
        try:
            ipaddress.IPv4Address(ip)
            return True, "OK"
        except Exception:
            return False, "Adresa IP nu este validă."

    def validate_hostname(self, hostname: str) -> tuple[bool, str]:
        if not HOST_RE.match(hostname or ""):
            return False, "Hostname invalid. Folosește litere, cifre, punct, minus sau underscore."
        return True, "OK"

    def get_leases(self) -> list[dict]:
        leases = []
        if not self.leases_file.exists():
            return leases

        with self.leases_file.open("r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) < 4:
                    continue

                hostname = parts[3] if parts[3] != "*" else ""
                leases.append({
                    "expires": parts[0],
                    "mac": self.normalize_mac(parts[1]),
                    "ip": parts[2],
                    "hostname": hostname,
                })

        leases.sort(key=lambda item: (item["hostname"] or "zzz", item["ip"]))
        return leases

    def _parse_reservation_line(self, line: str) -> Reservation | None:
        stripped = line.strip()
        if not stripped.startswith("dhcp-host="):
            return None

        values = stripped.replace("dhcp-host=", "", 1).split(",")
        if len(values) < 3:
            return None

        mac = self.normalize_mac(values[0])
        ip = values[1].strip()
        hostname = values[2].strip()
        lease = values[3].strip() if len(values) >= 4 and values[3].strip() else "infinite"
        return Reservation(mac=mac, ip=ip, hostname=hostname, lease=lease)

    def get_reservations(self) -> list[dict]:
        reservations = []
        if not self.reservations_file.exists():
            return reservations

        with self.reservations_file.open("r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                reservation = self._parse_reservation_line(line)
                if reservation:
                    reservations.append({
                        "mac": reservation.mac,
                        "ip": reservation.ip,
                        "hostname": reservation.hostname,
                        "lease": reservation.lease,
                    })

        reservations.sort(key=lambda item: ipaddress.IPv4Address(item["ip"]))
        return reservations

    def is_reserved(self, mac: str) -> bool:
        mac = self.normalize_mac(mac)
        return any(item["mac"] == mac for item in self.get_reservations())

    def get_lease_by_mac(self, mac: str) -> dict | None:
        mac = self.normalize_mac(mac)
        for lease in self.get_leases():
            if lease["mac"] == mac:
                return lease
        return None

    def get_reservation_by_mac(self, mac: str) -> dict | None:
        mac = self.normalize_mac(mac)
        for reservation in self.get_reservations():
            if reservation["mac"] == mac:
                return reservation
        return None

    def backup_reservations(self) -> Path | None:
        if not self.reservations_file.exists():
            return None
        backup_dir = self.reservations_file.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = backup_dir / f"{self.reservations_file.name}.{stamp}.bak"
        shutil.copy2(self.reservations_file, backup)
        return backup

    def _read_lines(self) -> list[str]:
        if not self.reservations_file.exists():
            return []
        return self.reservations_file.read_text(encoding="utf-8", errors="ignore").splitlines()

    def _write_reservations(self, reservations: Iterable[Reservation]) -> None:
        self.reservations_file.parent.mkdir(parents=True, exist_ok=True)
        header = [
            "# NetCenter DHCP reservations",
            "# Format: dhcp-host=MAC,IP,HOSTNAME,infinite",
            "",
        ]
        body = [r.to_line() for r in sorted(reservations, key=lambda r: ipaddress.IPv4Address(r.ip))]
        content = "\n".join(header + body) + "\n"
        self.reservations_file.write_text(content, encoding="utf-8")

    def _current_reservation_objects(self) -> list[Reservation]:
        objects = []
        for item in self.get_reservations():
            objects.append(Reservation(**item))
        return objects

    def _validate_duplicates(self, reservations: list[Reservation]) -> tuple[bool, str]:
        seen_macs = set()
        seen_ips = set()
        for reservation in reservations:
            if reservation.mac in seen_macs:
                return False, f"MAC duplicat: {reservation.mac}"
            if reservation.ip in seen_ips:
                return False, f"IP duplicat: {reservation.ip}"
            seen_macs.add(reservation.mac)
            seen_ips.add(reservation.ip)
        return True, "OK"

    def test_config(self) -> tuple[bool, str]:
        return True, "OK"

    def restart_dnsmasq(self) -> tuple[bool, str]:
        return SystemManager.apply_dnsmasq()

    def save_reservation(self, hostname: str, ip: str, mac: str) -> tuple[bool, str]:
        mac = self.normalize_mac(mac)
        hostname = self.normalize_hostname(hostname)
        ip = (ip or "").strip()

        for validator, value in (
            (self.validate_mac, mac),
            (self.validate_ip, ip),
            (self.validate_hostname, hostname),
        ):
            ok, message = validator(value)
            if not ok:
                return False, message

        backup = self.backup_reservations()
        old_content = self.reservations_file.read_text(encoding="utf-8", errors="ignore") if self.reservations_file.exists() else ""

        reservations = self._current_reservation_objects()
        updated = False
        for reservation in reservations:
            if reservation.mac == mac:
                reservation.ip = ip
                reservation.hostname = hostname
                reservation.lease = "infinite"
                updated = True
                break

        if not updated:
            reservations.append(Reservation(mac=mac, ip=ip, hostname=hostname, lease="infinite"))

        ok, message = self._validate_duplicates(reservations)
        if not ok:
            return False, message

        try:
            self._write_reservations(reservations)
            ok, output = self.test_config()
            if not ok:
                self.reservations_file.write_text(old_content, encoding="utf-8")
                return False, f"Configurație invalidă. Nu am aplicat modificarea. {output}"

            ok, output = self.restart_dnsmasq()
            if not ok:
                self.reservations_file.write_text(old_content, encoding="utf-8")
                self.restart_dnsmasq()
                return False, f"Nu am putut reporni dnsmasq. Am revenit la configurația anterioară. {output}"

            action = "actualizată" if updated else "creată"
            return True, f"Rezervarea a fost {action}."
        except Exception as exc:
            try:
                self.reservations_file.write_text(old_content, encoding="utf-8")
            except Exception:
                pass
            return False, f"Eroare la salvare: {exc}"

    def delete_reservation(self, mac: str) -> tuple[bool, str]:
        mac = self.normalize_mac(mac)
        ok, message = self.validate_mac(mac)
        if not ok:
            return False, message

        old_content = self.reservations_file.read_text(encoding="utf-8", errors="ignore") if self.reservations_file.exists() else ""
        self.backup_reservations()

        reservations = [r for r in self._current_reservation_objects() if r.mac != mac]
        if len(reservations) == len(self._current_reservation_objects()):
            return False, "Rezervarea nu a fost găsită."

        try:
            self._write_reservations(reservations)
            ok, output = self.test_config()
            if not ok:
                self.reservations_file.write_text(old_content, encoding="utf-8")
                return False, f"Configurație invalidă. Nu am șters rezervarea. {output}"

            ok, output = self.restart_dnsmasq()
            if not ok:
                self.reservations_file.write_text(old_content, encoding="utf-8")
                self.restart_dnsmasq()
                return False, f"Nu am putut reporni dnsmasq. Am revenit la configurația anterioară. {output}"

            return True, "Rezervarea a fost ștearsă."
        except Exception as exc:
            try:
                self.reservations_file.write_text(old_content, encoding="utf-8")
            except Exception:
                pass
            return False, f"Eroare la ștergere: {exc}"
