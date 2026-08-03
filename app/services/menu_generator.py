from database import get_db
from bootprofiles import GENERATORS
from services.windows import is_image_imported

MENU_CATEGORIES = [
    "Windows",
    "WinPE",
    "Linux",
    "Other",
    "Rescue",
    "Utilities",
]

def get_menu(category):
    conn = get_db()

    rows = conn.execute(
        """
        SELECT
            id,
            name,
	    display_name,
            profile_id,
            boot_type,
            path
        FROM boot_images
        WHERE enabled=1
          AND category=?
        ORDER BY
            sort_order,
            name
        """,
        (category,),
    ).fetchall()

    conn.close()

    # În meniul PXE apar numai imaginile care au toate
    # fișierele necesare extrase și pregătite pentru boot.
    return [
        row
        for row in rows
        if is_image_imported(row)
    ]

def generate_main_menu(base_url):

    lines = [
        "#!ipxe",
        "",
        ":main",
        "menu NetCenter PXE",
        "",
    ]

    for category in MENU_CATEGORIES:

        rows = get_menu(category)

        if not rows:
            continue

        key = category.lower()

        lines.append(f"item {key} {category}")

    lines.extend([
        "item local Boot local",
        "",
        "choose target || goto cancel",
        "goto ${target}",
        "",
    ])

    for category in MENU_CATEGORIES:

        rows = get_menu(category)

        if not rows:
            continue

        key = category.lower()

        lines.extend([
            f":{key}",
            f"chain {base_url}/menu/{category}",
            "",
        ])

    lines.extend([
        ":local",
        "exit",
        "",
        ":cancel",
        "exit",
    ])

    return "\n".join(lines)

def generate_category_menu(category, base_url):

    rows = get_menu(category)

    lines = [
        "#!ipxe",
        "",
        f":{category}",
        f"menu {category}",
        "",
    ]

    for row in rows:
        lines.append(f"item boot{row['id']} {row['display_name'] or row['name']}")

    lines.extend([
        "",
        "item back Înapoi",
        "",
        "choose target || goto back",
        "goto ${target}",
        "",
    ])

    conn = get_db()

    for row in rows:

        profile = conn.execute("""
            SELECT generator
            FROM boot_profiles
            WHERE id=?
        """, (row["profile_id"],)).fetchone()

        lines.extend([
            f":boot{row['id']}",
            f"chain {base_url}/boot/{row['id']}.ipxe",
            "",
        ])

    conn.close()

    lines.extend([
        ":back",
        f"chain {base_url}/boot.ipxe",
    ])

    return "\n".join(lines)

