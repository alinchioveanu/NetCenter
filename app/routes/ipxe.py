import os
from flask import Blueprint, abort, request
from database import get_db
from bootprofiles import GENERATORS

bp = Blueprint("ipxe", __name__)


@bp.route("/boot/<int:image_id>.ipxe")
def boot(image_id):

    conn = get_db()

    row = conn.execute("""
        SELECT
            b.*,
            p.generator
        FROM boot_images b
        JOIN boot_profiles p
          ON p.id=b.profile_id
        WHERE b.id=?
    """, (image_id,)).fetchone()

    conn.close()

    if row is None:
        abort(404)

    base_url = os.environ.get("NETCENTER_BASE_URL", "").strip().rstrip("/") or request.host_url.rstrip("/")

    return (
        GENERATORS[row["generator"]](row, base_url),
        200,
        {"Content-Type": "text/plain"},
    )
