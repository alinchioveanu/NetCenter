# NetCenter 4.5

NetCenter administrează DHCP și o bibliotecă de imagini PXE.

## Funcții

- administrare rezervări DHCP;
- scanare automată a imaginilor;
- import și pornire pentru imagini Linux și Android-x86;
- import pentru categoriile Other, Rescue și Utilities;
- pornire Rescue direct din fișiere ISO și EFI;
- detectare automată kernel, initrd și filesystem Linux;
- import Windows Setup și WinPE;
- suport Strelec, AOMEI, EaseUS, MiniTool, Passcape și R-Studio;
- ștergerea importului fără ștergerea ISO-ului;
- meniu PXE limitat la imaginile importate;
- pornire BIOS Legacy și UEFI;
- laborator QEMU.

## Instalare

1. Copiază `.env.example` ca `.env`.
2. Configurează `IMAGES_PATH`, `NETCENTER_BASE_URL`, `TZ` și `FLASK_SECRET_KEY`.
3. Rulează `docker compose build`.
4. Rulează `docker compose up -d`.
5. Deschide `http://ADRESA_SERVERULUI:8099`.

## Configurare

Exemplu `.env`:

    IMAGES_PATH=/cale/catre/imagini
    TZ=Europe/Bucharest
    NETCENTER_BASE_URL=http://ADRESA_SERVERULUI:8099
    FLASK_SECRET_KEY=valoare-aleatoare

Generează cheia cu `openssl rand -hex 32`.

## Date locale

Repository-ul nu include baza de date, importurile generate,
imaginile ISO/IMG, configurația `.env` sau discurile laboratorului.

## Securitate

Containerul rulează privilegiat pentru integrarea cu dnsmasq.
Folosește aplicația numai într-o rețea de încredere.

## Versiune

4.5.0
