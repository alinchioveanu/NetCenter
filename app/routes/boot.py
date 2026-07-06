from flask import Blueprint, send_from_directory

boot = Blueprint("boot", __name__)


@boot.route("/boot.ipxe")
def boot_ipxe():
    return send_from_directory("/app/menus", "main.ipxe", mimetype="text/plain")


@boot.route("/menu/<path:filename>")
def menu_files(filename):
    return send_from_directory("/app/menus", filename)


@boot.route("/ipxe/<path:filename>")
def ipxe_files(filename):
    return send_from_directory("/app/ipxe", filename)
