from pathlib import Path

from database import get_db


IMAGE_ROOT = Path("/images")

EXTENSIONS = {
    ".iso",
    ".img",
    ".wim",
    ".efi",
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

PROFILE_MAP = {
    "Windows": 1,
    "WinPE": 2,
    "Linux": 3,
    "Rescue": 4,
    "Utilities": 4,
    "Other": 4,
}


WINPE_UTILITY_KEYWORDS = (
    "mini_tool",
    "minitool",
    "passcape",
    "r_studio",
    "r-studio",
)


def detect_profile(category: str, name: str) -> int:
    lower = name.lower()

    if category == "Utilities":
        if any(
            keyword in lower
            for keyword in WINPE_UTILITY_KEYWORDS
        ):
            return 2

    return PROFILE_MAP[category]


def detect_category(name: str) -> str:
    lower = name.lower()

    # Reguli specifice înaintea celor generale.
    if any(keyword in lower for keyword in (
        "winpe",
        "strelec",
        "hiren",
    )):
        return "WinPE"

    if any(keyword in lower for keyword in (
        "memtest",
        "partition",
        "parted",
        "aomei",
        "easeus",
        "passcape",
        "r_studio",
        "seatools",
        "shell",
    )):
        return "Utilities"

    if any(keyword in lower for keyword in (
        "clonezilla",
        "rescue",
        "kaspersky",
        "acronis",
    )):
        return "Rescue"

    if any(keyword in lower for keyword in (
        "ubuntu",
        "debian",
        "mint",
        "fedora",
        "android",
        "linux",
        "cutefish",
    )):
        return "Linux"

    if any(keyword in lower for keyword in (
        "windows",
        "win11",
        "win10",
        "server",
    )):
        return "Windows"

    return "Other"


def scan_library() -> list[dict]:
    images = []

    if not IMAGE_ROOT.exists():
        return images

    for file in IMAGE_ROOT.rglob("*"):
        if not file.is_file():
            continue

        if any(part.lower().startswith("ventoy") for part in file.parts):
            continue

        extension = file.suffix.lower()

        if extension not in EXTENSIONS:
            continue

        try:
            if file.stat().st_size == 0:
                continue
        except OSError:
            continue

        category = detect_category(file.stem)

        images.append({
            "name": file.stem,
            "path": str(file),
            "extension": extension,
            "category": category,
            "profile_id": detect_profile(category, file.stem),
        })

    return sorted(
        images,
        key=lambda image: (
            image["category"],
            image["name"].lower(),
            image["path"].lower(),
        ),
    )


def sync_library() -> dict:
    images = scan_library()
    scanned_paths = {image["path"] for image in images}

    conn = get_db()

    # Cei doi workeri Gunicorn pot importa aplicația simultan.
    # BEGIN IMMEDIATE serializează operațiile și previne dublurile.
    conn.execute("BEGIN IMMEDIATE")

    existing_rows = conn.execute(
        "SELECT id, path FROM boot_images"
    ).fetchall()

    existing_by_path = {
        row["path"]: row["id"]
        for row in existing_rows
    }

    removed = 0
    added = 0
    updated = 0

    for path, image_id in existing_by_path.items():
        if path not in scanned_paths:
            conn.execute(
                "DELETE FROM boot_images WHERE id=?",
                (image_id,),
            )
            removed += 1

    for image in images:
        image_id = existing_by_path.get(image["path"])

        if image_id is None:
            conn.execute(
                """
                INSERT INTO boot_images
                (
                    name,
                    category,
                    boot_type,
                    path,
                    profile_id
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    image["name"],
                    image["category"],
                    image["extension"].lstrip(".").upper(),
                    image["path"],
                    image["profile_id"],
                ),
            )
            added += 1
        else:
            conn.execute(
                """
                UPDATE boot_images
                SET
                    name=?,
                    category=?,
                    boot_type=?,
                    profile_id=?
                WHERE id=?
                """,
                (
                    image["name"],
                    image["category"],
                    image["extension"].lstrip(".").upper(),
                    image["profile_id"],
                    image_id,
                ),
            )
            updated += 1

    conn.commit()
    conn.close()

    return {
        "added": added,
        "updated": updated,
        "removed": removed,
        "total": len(images),
    }
