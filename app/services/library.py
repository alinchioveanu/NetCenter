from pathlib import Path
from database import get_db

BOOT_ROOT = Path("/app/boot")

PROFILE_MAP = {
    "Windows": 1,
    "WinPE": 2,
    "Linux": 3,
    "Rescue": 4,
}

def detect_category(name):
    n = name.lower()

    if any(x in n for x in ["win", "server"]):
        return "Windows"
    if any(x in n for x in ["strelec", "winpe", "hiren"]):
        return "WinPE"
    if any(x in n for x in ["mint", "ubuntu", "linux", "android"]):
        return "Linux"
    return "Rescue"


def sync_library():
    conn = get_db()

    rows = conn.execute("SELECT id,name,category FROM boot_images").fetchall()

    fixed = 0

    for r in rows:
        profile = PROFILE_MAP.get(r["category"], 4)

        conn.execute(
            "UPDATE boot_images SET profile_id=? WHERE id=?",
            (profile, r["id"])
        )

        fixed += 1

    conn.commit()
    conn.close()

    return {
        "fixed": fixed
    }
