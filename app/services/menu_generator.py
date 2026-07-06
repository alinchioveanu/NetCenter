from database import get_db


def get_menu(category):
    conn = get_db()

    rows = conn.execute(
        """
        SELECT
            id,
            name,
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

    return rows
