from database import get_db


def get_profiles():
    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            name,
            description,
            generator
        FROM boot_profiles
        ORDER BY id
    """).fetchall()

    conn.close()

    return rows
