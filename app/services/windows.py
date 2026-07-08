from pathlib import Path
import subprocess

BOOT_ROOT = Path("/app/boot/windows")

REQUIRED_FILES = [
    ("bootmgr", "bootmgr"),
    ("boot/bcd", "BCD"),
    ("boot/boot.sdi", "boot.sdi"),
    ("sources/boot.wim", "boot.wim"),
]

def import_windows_iso(iso_path: str):
    iso = Path(iso_path)
    target = BOOT_ROOT / iso.stem

    target.mkdir(parents=True, exist_ok=True)

    for source, output in REQUIRED_FILES:
        subprocess.run(
            [
                "7z",
                "e",
                "-y",
                str(iso),
                source,
                f"-o{target}",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        extracted = target / Path(source).name
        if extracted.exists() and extracted.name != output:
            extracted.rename(target / output)

    missing = [
        output
        for _, output in REQUIRED_FILES
        if not (target / output).exists()
    ]

    return {
        "target": str(target),
        "ready": len(missing) == 0,
        "missing": missing,
    }
