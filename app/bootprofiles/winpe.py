from pathlib import Path

BOOT_ROOT = Path("/app/boot/winpe")


def generate(image, base_url):

    folder = BOOT_ROOT / str(image["id"])
    base = f"{base_url}/bootfiles/winpe/{image['id']}"

    wim = "boot.wim"

    if (folder / "strelec11x64Eng.wim").exists():
        wim = "strelec11x64Eng.wim"

    return f"""#!ipxe

isset ${{platform}} || set platform unknown

kernel {base_url}/wimboot

iseq ${{platform}} efi && goto uefi || goto bios

:bios
initrd {base}/BCD BCD
goto common

:uefi
initrd {base}/BCD.UEFI BCD
goto common

:common
initrd {base}/boot.sdi boot.sdi
initrd {base}/{wim} boot.wim


boot
"""
