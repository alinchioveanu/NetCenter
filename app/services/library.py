from pathlib import Path

IMAGE_ROOT = Path("/images")

EXTENSIONS = {
    ".iso",
    ".img",
    ".wim",
    ".efi",
}

IGNORE_DIRS = {
    "ventoy",
}

CATEGORY_RULES = {
    "windows": "Windows",
    "win11": "Windows",
    "win10": "Windows",
    "server": "Windows",

    "winpe": "WinPE",
    "strelec": "WinPE",
    "hiren": "WinPE",

    "ubuntu": "Linux",
    "debian": "Linux",
    "mint": "Linux",
    "fedora": "Linux",
    "android": "Linux",
    "linux": "Linux",
    "cutefish": "Linux",

    "clonezilla": "Rescue",
    "rescue": "Rescue",
    "kaspersky": "Rescue",
    "acronis": "Rescue",

    "memtest": "Utilities",
    "partition": "Utilities",
    "parted": "Utilities",
    "aomei": "Utilities",
    "easeus": "Utilities",
    "passcape": "Utilities",
    "r_studio": "Utilities",
    "seatools": "Utilities",
    "shell": "Utilities",
}


def detect_category(name: str):
    lower = name.lower()

    for keyword, category in CATEGORY_RULES.items():
        if keyword in lower:
            return category

    return "Other"


def scan_library():

    images = []
    seen = set()

    for file in IMAGE_ROOT.rglob("*"):

        if not file.is_file():
            continue

        if any(part.lower().startswith("ventoy") for part in file.parts):
            continue

        if file.suffix.lower() not in EXTENSIONS:
            continue

        if file.stat().st_size == 0:
            continue

        if str(file) in seen:
            continue

        seen.add(str(file))

        images.append({
            "name": file.stem,
            "filename": file.name,
            "path": str(file),
            "extension": file.suffix.lower(),
            "size": file.stat().st_size,
            "category": detect_category(file.stem),
        })

    return sorted(images, key=lambda x: (x["category"], x["name"].lower()))

from database import get_db


def sync_library():
    conn = get_db()

    images = scan_library()

    added = 0

    for image in images:

        exists = conn.execute(
            "SELECT id FROM boot_images WHERE path=?",
            (image["path"],)
        ).fetchone()

        if exists:
            continue

        conn.execute(
            """
            INSERT INTO boot_images
            (name, category, boot_type, path)
            VALUES (?, ?, ?, ?)
            """,
            (
                image["name"],
                image["category"],
                image["extension"].lstrip(".").upper(),
                image["path"],
            ),
        )

        added += 1

    conn.commit()
    conn.close()

    return {
        "added": added,
        "total": len(images),
    }
