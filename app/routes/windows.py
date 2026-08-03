from flask import Blueprint, abort, flash, redirect, url_for
from database import get_db
from services.windows import (
    delete_image_import,
    import_windows_iso,
)

bp = Blueprint("windows", __name__)


@bp.route("/windows/import/<int:image_id>")
def import_iso(image_id):

    conn = get_db()

    image = conn.execute(
        """
        SELECT id, name, path, profile_id
        FROM boot_images
        WHERE id=?
          AND profile_id IN (1, 2)
        """,
        (image_id,),
    ).fetchone()

    conn.close()

    if image is None:
        abort(404)

    result = import_windows_iso(
        image["path"],
        profile_id=image["profile_id"],
        image_id=image["id"],
    )

    if result["ready"]:
        return f'''
<!doctype html>
<meta http-equiv="refresh" content="1; url=/images">
<div style="font-family:Arial;padding:40px">
<h2>✔ Import finalizat</h2>
<p><b>{image["name"]}</b> este pregătită pentru PXE.</p>
<p>Redirecționare...</p>
</div>
'''

    return result


@bp.route(
    "/windows/delete-import/<int:image_id>",
    methods=["POST"],
)
def delete_import(image_id):
    conn = get_db()

    image = conn.execute(
        """
        SELECT id, name, path, profile_id
        FROM boot_images
        WHERE id=?
          AND profile_id IN (1, 2)
        """,
        (image_id,),
    ).fetchone()

    conn.close()

    if image is None:
        abort(404)

    deleted, target = delete_image_import(image)

    if deleted:
        flash(
            f"Importul pentru {image['name']} a fost șters.",
            "success",
        )
    else:
        flash(
            f"Imaginea {image['name']} nu era importată.",
            "warning",
        )

    return redirect(url_for("images"))

