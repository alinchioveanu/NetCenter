from pathlib import Path


BOOT_ROOT = Path("/app/boot/linux")


def failed_menu(image, base_url, message):
    return f"""#!ipxe

echo {message}
echo Imagine: {image["name"]}
sleep 5
chain {base_url}/boot.ipxe
"""


def generate(image, base_url):
    folder = BOOT_ROOT / str(image["id"])
    boot_type_file = folder / "boot_type.txt"

    if not boot_type_file.is_file():
        return failed_menu(
            image,
            base_url,
            "Imaginea Linux nu este importata complet.",
        )

    boot_type = boot_type_file.read_text().strip()
    base = f"{base_url}/bootfiles/linux/{image['id']}"

    if boot_type == "casper":
        return f"""#!ipxe

imgfree
kernel {base}/kernel boot=casper netboot=url ip=dhcp url={base}/filesystem.squashfs || goto failed
initrd {base}/initrd || goto failed
boot || goto failed

:failed
echo Pornirea imaginii Linux Live a esuat.
sleep 5
chain {base_url}/boot.ipxe
"""

    if boot_type == "debian-live":
        return f"""#!ipxe

imgfree
kernel {base}/kernel boot=live components ip=dhcp fetch={base}/filesystem.squashfs || goto failed
initrd {base}/initrd || goto failed
boot || goto failed

:failed
echo Pornirea imaginii Debian Live a esuat.
sleep 5
chain {base_url}/boot.ipxe
"""

    if boot_type == "android":
        ramdisk = ""

        if (folder / "ramdisk.img").is_file():
            ramdisk = (
                f"initrd --name ramdisk.img "
                f"{base}/ramdisk.img ramdisk.img || goto failed\n"
            )

        return f"""#!ipxe

imgfree
kernel {base}/kernel root=/dev/ram0 androidboot.hardware=android_x86 androidboot.selinux=permissive SRC=/ || goto failed
initrd --name initrd.img {base}/initrd initrd.img || goto failed
{ramdisk}initrd --name system.sfs {base}/system.sfs system.sfs || goto failed
boot || goto failed

:failed
echo Pornirea Android-x86 a esuat.
sleep 5
chain {base_url}/boot.ipxe
"""

    return failed_menu(
        image,
        base_url,
        f"Tip Linux necunoscut: {boot_type}",
    )
