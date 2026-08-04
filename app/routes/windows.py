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
          AND profile_id IN (1, 2, 3, 4)
        """,
        (image_id,),
    ).fetchone()

    conn.close()

    if image is None:
        abort(404)

    try:
        result = import_windows_iso(
            image["path"],
            profile_id=image["profile_id"],
            image_id=image["id"],
        )
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        flash(
            f"Import eșuat pentru {image['name']}: {error}",
            "danger",
        )
        return redirect(url_for("images"))

    if result["ready"]:
        flash(
            f"Import finalizat: {image['name']} este pregătită pentru PXE.",
            "success",
        )
    else:
        missing = result.get("missing", [])
        details = ", ".join(missing) if missing else "fișiere necunoscute"

        flash(
            f"Import incomplet pentru {image['name']}. Lipsesc: {details}",
            "danger",
        )

    return redirect(url_for("images"))


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
          AND profile_id IN (1, 2, 3, 4)
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

