from pathlib import Path

BOOT_ROOT = Path("/app/boot/windows")


def generate(image, base_url):

    folder = BOOT_ROOT / Path(image["path"]).stem
    base = f"{base_url}/bootfiles/windows/{folder.name}"

    return f"""#!ipxe

kernel {base_url}/wimboot

initrd {base}/BCD BCD
initrd {base}/boot.sdi boot.sdi
initrd {base}/boot.wim boot.wim

boot
"""
