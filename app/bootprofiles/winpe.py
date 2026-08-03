from pathlib import Path
from urllib.parse import quote


BOOT_ROOT = Path("/app/boot/winpe")


def generate(image, base_url):
    folder = BOOT_ROOT / str(image["id"])
    base = f"{base_url}/bootfiles/winpe/{image['id']}"

    selection_file = folder / "selected_wim.txt"

    if selection_file.exists():
        wim = selection_file.read_text().strip()
    else:
        candidates = sorted(folder.glob("*.wim"))
        wim = candidates[0].name if candidates else "boot.wim"

    wim_url = quote(wim)

    bios_loader = ""
    if (folder / "bootmgr").exists():
        bios_loader = f"initrd {base}/bootmgr bootmgr\n"

    efi_loader = ""
    if (folder / "bootmgfw.efi").exists():
        efi_loader = (
            f"initrd --name bootmgfw.efi "
            f"{base}/bootmgfw.efi bootmgfw.efi\n"
        )

    return f"""#!ipxe

isset ${{platform}} || set platform unknown
imgfree

iseq ${{platform}} efi && goto uefi || goto bios

:bios
kernel {base_url}/wimboot pause
{bios_loader}initrd {base}/BCD BCD
initrd {base}/boot.sdi boot.sdi
initrd {base}/{wim_url} boot.wim
imgstat
boot

:uefi
kernel {base_url}/wimboot pause
{efi_loader}initrd --name BCD {base}/BCD.UEFI BCD
initrd --name boot.sdi {base}/boot.sdi boot.sdi
initrd --name boot.wim {base}/{wim_url} boot.wim
imgstat
boot
"""
