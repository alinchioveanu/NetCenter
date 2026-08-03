import os

from flask import Blueprint, send_from_directory, request

boot = Blueprint("boot", __name__)


def get_base_url():
    configured = os.environ.get(
        "NETCENTER_BASE_URL",
        "",
    ).strip()

    if configured:
        return configured.rstrip("/")

    return request.host_url.rstrip("/")


@boot.route("/boot.ipxe")
def boot_ipxe():
    from services.menu_generator import generate_main_menu
    return generate_main_menu(get_base_url()), 200, {"Content-Type": "text/plain"}


@boot.route("/menu/<category>")
def category_menu(category):
    from services.menu_generator import generate_category_menu
    return generate_category_menu(
        category,
        get_base_url()
    ), 200, {"Content-Type": "text/plain"}


@boot.route("/ipxe/<path:filename>")
def ipxe_files(filename):
    return send_from_directory("/app/ipxe", filename)
