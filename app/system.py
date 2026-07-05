from pathlib import Path


class SystemManager:

    @staticmethod
    def apply_dnsmasq():

        flag = Path("/etc/dnsmasq.d/.netcenter-reload")
        flag.touch(exist_ok=True)

        return True, "Configurarea a fost salvată. Reload în așteptare."
