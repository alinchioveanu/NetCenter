def generate(image, base_url):
    name = image["name"]
    path = image["path"]

    return f"""#!ipxe

menu {image['display_name']}

item boot Boot {image['display_name']}
item back Inapoi

choose target || goto back
goto ${{target}}

:boot
kernel {base_url}/bootfiles/linux/{name}/vmlinuz boot=casper ip=dhcp url={base_url}/bootfiles/linux/{name}/casper/filesystem.squashfs
initrd {base_url}/bootfiles/linux/{name}/initrd.lz
boot

:back
chain {base_url}/boot.ipxe
"""
