from pathlib import Path
from urllib.parse import quote


BOOT_ROOT = Path("/app/boot/rescue")


def generate(image, base_url):
    folder = BOOT_ROOT / str(image["id"])
    selection = folder / "selected_media.txt"

    if not selection.is_file():
        return f"""#!ipxe
echo Imaginea nu este importata complet.
sleep 3
chain {base_url}/boot.ipxe
"""

    media = selection.read_text().strip()
    media_url = quote(media)
    url = (
        f"{base_url}/bootfiles/rescue/"
        f"{image['id']}/{media_url}"
    )

    if Path(media).suffix.lower() == ".efi":
        return f"""#!ipxe

imgfree
chain {url} || goto failed

:failed
echo Pornirea aplicatiei EFI a esuat.
sleep 5
chain {base_url}/boot.ipxe
"""

    return f"""#!ipxe

imgfree
sanboot --no-describe {url} || goto failed

:failed
echo Pornirea imaginii {image['name']} a esuat.
echo Aceasta imagine poate necesita un profil PXE special.
sleep 5
chain {base_url}/boot.ipxe
"""
