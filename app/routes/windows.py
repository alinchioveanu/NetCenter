from flask import Blueprint, abort
from database import get_db
from services.windows import import_windows_iso

bp = Blueprint("windows", __name__)


@bp.route("/windows/import/<int:image_id>")
def import_iso(image_id):

    conn = get_db()

    image = conn.execute(
        """
        SELECT id, name, path
        FROM boot_images
        WHERE id=?
        """,
        (image_id,),
    ).fetchone()

    conn.close()

    if image is None:
        abort(404)

    result = import_windows_iso(image["path"])

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
