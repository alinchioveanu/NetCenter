from pathlib import Path
import re
import shutil
import subprocess


WINDOWS_ROOT = Path("/app/boot/windows")
WINPE_ROOT = Path("/app/boot/winpe")


def archive_files(iso: Path) -> list[str]:
    result = subprocess.run(
        ["7z", "l", "-slt", str(iso)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    files = []

    for match in re.finditer(r"^Path = (.+)$", result.stdout, re.MULTILINE):
        value = match.group(1).strip()

        if value != str(iso) and "/" in value:
            files.append(value)

    return files


def select_path(files: list[str], candidates: list[str]) -> str | None:
    by_lower = {item.lower(): item for item in files}

    for candidate in candidates:
        found = by_lower.get(candidate.lower())
        if found:
            return found

    return None


def extract_file(
    iso: Path,
    source: str,
    destination: Path,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            "7z",
            "e",
            "-y",
            str(iso),
            source,
            f"-o{destination.parent}",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    extracted = destination.parent / Path(source).name

    if extracted.exists() and extracted != destination:
        extracted.replace(destination)

    if not destination.exists():
        raise RuntimeError(
            f"Nu s-a putut extrage {source} din {iso}. "
            f"Cod 7z: {result.returncode}\n{result.stdout}"
        )


def import_windows_setup(iso: Path) -> dict:
    target = WINDOWS_ROOT / iso.stem
    target.mkdir(parents=True, exist_ok=True)

    required = [
        ("bootmgr", "bootmgr"),
        ("boot/bcd", "BCD"),
        ("boot/boot.sdi", "boot.sdi"),
        ("sources/boot.wim", "boot.wim"),
    ]

    for source, output in required:
        extract_file(iso, source, target / output)

    missing = [
        output
        for _, output in required
        if not (target / output).exists()
    ]

    return {
        "target": str(target),
        "ready": not missing,
        "missing": missing,
    }


def import_winpe(iso: Path, image_id: int) -> dict:
    target = WINPE_ROOT / str(image_id)
    target.mkdir(parents=True, exist_ok=True)

    files = archive_files(iso)

    bios_bcd = select_path(files, [
        "SSTR/BCD",
        "boot/BCD",
        "boot/bcd",
    ])

    uefi_bcd = select_path(files, [
        "EFI/microsoft/boot/BCD",
        "efi/microsoft/boot/bcd",
    ])

    boot_sdi = select_path(files, [
        "SSTR/boot.sdi",
        "boot/boot.sdi",
    ])

    bootmgr = select_path(files, [
        "SSTR/bootmgr",
        "bootmgr",
    ])

    wim_files = sorted(
        (item for item in files if item.lower().endswith(".wim")),
        key=lambda item: (
            "11" not in Path(item).name.lower(),
            Path(item).name.lower() != "boot.wim",
            item.lower(),
        ),
    )

    missing_sources = []

    if not bios_bcd:
        missing_sources.append("BCD")

    if not boot_sdi:
        missing_sources.append("boot.sdi")


    if not wim_files:
        missing_sources.append("imagine WIM")

    if missing_sources:
        raise RuntimeError(
            "ISO WinPE incompatibil. Lipsesc: "
            + ", ".join(missing_sources)
        )

    # Ambele surse se numesc BCD. Extragem întâi varianta UEFI,
    # apoi varianta BIOS, pentru a nu muta BCD-ul BIOS existent.
    if uefi_bcd:
        extract_file(iso, uefi_bcd, target / "BCD.UEFI")

    extract_file(iso, bios_bcd, target / "BCD")

    if not uefi_bcd:
        shutil.copy2(target / "BCD", target / "BCD.UEFI")

    extract_file(iso, boot_sdi, target / "boot.sdi")

    if bootmgr:
        extract_file(iso, bootmgr, target / "bootmgr")

    uefi_loader = select_path(files, [
        "EFI/boot/bootx64.efi",
        "EFI/Microsoft/Boot/bootmgfw.efi",
    ])

    if uefi_loader:
        extract_file(
            iso,
            uefi_loader,
            target / "bootmgfw.efi",
        )

    selected_wim = wim_files[0]
    extract_file(
        iso,
        selected_wim,
        target / Path(selected_wim).name,
    )

    (target / "selected_wim.txt").write_text(
        Path(selected_wim).name + "\n"
    )

    required_outputs = [
        "BCD",
        "BCD.UEFI",
        "boot.sdi",
        Path(selected_wim).name,
        "selected_wim.txt",
    ]

    if bootmgr:
        required_outputs.append("bootmgr")

    if uefi_loader:
        required_outputs.append("bootmgfw.efi")

    missing = [
        output
        for output in required_outputs
        if not (target / output).exists()
    ]

    return {
        "target": str(target),
        "ready": not missing,
        "missing": missing,
        "selected_wim": Path(selected_wim).name,
    }


def import_windows_iso(
    iso_path: str,
    profile_id: int = 1,
    image_id: int | None = None,
) -> dict:
    iso = Path(iso_path)

    if not iso.is_file():
        raise FileNotFoundError(f"ISO inexistent: {iso}")

    if profile_id == 2:
        if image_id is None:
            raise ValueError("Pentru WinPE este obligatoriu image_id.")

        return import_winpe(iso, image_id)

    return import_windows_setup(iso)

def get_import_target(image) -> Path:
    profile_id = int(image["profile_id"])

    if profile_id == 1:
        return WINDOWS_ROOT / Path(image["path"]).stem

    if profile_id == 2:
        return WINPE_ROOT / str(image["id"])

    raise ValueError(
        f"Profilul {profile_id} nu acceptă import."
    )


def is_image_imported(image) -> bool:
    try:
        target = get_import_target(image)
    except (ValueError, KeyError, TypeError):
        return False

    if not target.is_dir():
        return False

    if int(image["profile_id"]) == 1:
        required = (
            "bootmgr",
            "BCD",
            "boot.sdi",
            "boot.wim",
        )

        return all(
            (target / name).is_file()
            for name in required
        )

    required = (
        target / "BCD",
        target / "boot.sdi",
        target / "selected_wim.txt",
    )

    if not all(file.is_file() for file in required):
        return False

    selected_wim = (
        target / "selected_wim.txt"
    ).read_text().strip()

    if not selected_wim:
        return False

    return (target / selected_wim).is_file()


def delete_image_import(image) -> tuple[bool, Path]:
    target = get_import_target(image)

    if int(image["profile_id"]) == 1:
        expected_root = WINDOWS_ROOT
    else:
        expected_root = WINPE_ROOT

    # Protecție: ținta trebuie să fie copil direct al
    # directorului de import permis.
    if target.parent != expected_root or target == expected_root:
        raise ValueError(
            f"Țintă de ștergere invalidă: {target}"
        )

    if not target.exists():
        return False, target

    shutil.rmtree(target)
    return True, target

