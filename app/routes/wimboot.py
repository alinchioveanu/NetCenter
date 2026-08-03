from flask import Blueprint, send_file
from pathlib import Path

bp = Blueprint("wimboot", __name__)

WIMBOOT = Path("/app/wimboot/wimboot")

@bp.route("/wimboot")
def wimboot():
    return send_file(
        WIMBOOT,
        mimetype="application/octet-stream",
        as_attachment=False,
    )
