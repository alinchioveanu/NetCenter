from pathlib import Path

from flask import Blueprint, abort, send_from_directory

bp = Blueprint("bootfiles", __name__)

ROOTS = {
    "windows": Path("/app/boot/windows"),
    "winpe": Path("/app/boot/winpe"),
    "linux": Path("/app/boot/linux"),
    "rescue": Path("/app/boot/rescue"),
}


@bp.route("/bootfiles/<system>/<image>/<path:filename>")
def bootfile(system, image, filename):
    if system not in ROOTS:
        abort(404)

    folder = ROOTS[system] / image

    if not folder.exists():
        abort(404)

    return send_from_directory(folder, filename, as_attachment=False)
