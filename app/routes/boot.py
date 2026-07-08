from flask import Blueprint, send_from_directory

boot = Blueprint("boot", __name__)


@boot.route("/boot.ipxe")
def boot_ipxe():
    from services.menu_generator import generate_main_menu
    return generate_main_menu(), 200, {"Content-Type": "text/plain"}


@boot.route("/menu/<path:filename>")
def menu_files(filename):
    return send_from_directory("/app/menus", filename)


@boot.route("/ipxe/<path:filename>")
def ipxe_files(filename):
    return send_from_directory("/app/ipxe", filename)
