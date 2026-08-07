# Changelog

## 4.6.0 — 2026-08-07

### Adăugat

- integrare CrowdSec direct în interfața NetCenter;
- pagină dedicată CrowdSec pentru vizualizarea adreselor IP blocate;
- acțiuni pentru blocarea și deblocarea adreselor IP prin CrowdSec;
- pagină de detalii pentru adresele IP din CrowdSec;
- serviciu de lookup IP pentru afișarea informațiilor suplimentare despre o adresă;
- pagină dedicată de informații pentru dispozitivele DHCP;
- acces la informațiile unui dispozitiv prin click pe adresa IP din lista DHCP;
- identificarea și afișarea modelului dispozitivelor DHCP;
- afișarea numelui atribuit de utilizator pentru dispozitivele DHCP.

### Îmbunătățit

- adresele IP din DHCP sunt afișate ca linkuri către pagina dispozitivului;
- informațiile disponibile despre dispozitive sunt reunite într-o pagină dedicată;
- afișarea valorii `-` pentru informațiile care nu au putut fi detectate;
- integrarea informațiilor de identificare a dispozitivelor în lista DHCP;
- navigarea NetCenter cu acces direct la secțiunea CrowdSec;
- interfața DHCP și paginile asociate pentru afișare desktop și mobil;
- consistența vizuală între DHCP, Boot Images, Boot Profiles, Laborator și CrowdSec.


## 4.5.5 — 2026-08-05

### Adăugat

- coloana `Last seen` pentru lease-urile DHCP;
- verificarea simultană a dispozitivelor prin ICMP;
- memorarea persistentă în SQLite a datei și orei ultimului răspuns;
- indicatoare Online și Offline pentru dispozitivele DHCP;
- sortare crescătoare și descrescătoare pentru lease-urile active;
- sortare crescătoare și descrescătoare pentru rezervările DHCP;
- sortare pe coloanele Nume, Categorie, Tip, Cale și Status din Boot Images;
- controlul sortării din tastatură cu Enter sau Space.

### Îmbunătățit

- interfața Boot Images pentru ecrane desktop și mobile;
- bara de navigare responsive cu meniu pliabil pe mobil;
- pagina Boot Profiles cu afișare pe carduri și stare pentru generatoare;
- ordonarea cronologică a profilurilor de boot după ID;
- descrierile profilurilor Windows Setup, WinPE, Linux Live și Rescue;
- marcarea generatoarelor încă neimplementate;
- pagina Laborator testare iPXE și QEMU;
- afișarea comenzilor laboratorului în secțiuni separate;
- margini unitare `container-fluid` în toate paginile;
- aspect vizual unitar pentru DHCP, Boot Images, Boot Profiles și Laborator;
- adaptarea tabelelor și butoanelor pentru dispozitive mobile.

### Dependențe

- adăugat `iputils-ping` în imaginea Docker pentru verificarea dispozitivelor.

## 4.5.0 — 2026-08-04

### Adăugat

- import și pornire pentru imagini Linux, Android-x86 și Rescue;
- generator dedicat pentru imagini Rescue ISO și EFI;
- importul categoriilor Other, Rescue și Utilities.

### Îmbunătățit

- detectarea automată a kernelului, initrd-ului și sistemului de fișiere Linux;
- generarea scripturilor iPXE pentru mai multe tipuri de distribuții;
- importul și procesarea imaginilor Windows.

### Corectat

- URL-urile scripturilor de boot folosesc `NETCENTER_BASE_URL`;
- revenirea în meniul principal pentru imaginile Rescue incomplete;
- afișarea autorului în bara de navigare.


## 4.0.0 — 2026-08-03

### Adăugat

- sincronizare automată a bibliotecii;
- import Windows Setup și WinPE;
- suport Strelec, AOMEI, EaseUS și utilitare WinPE;
- detectarea stării importului;
- ștergerea importului din interfață;
- filtrarea meniului PXE la imaginile importate;
- suport BIOS și UEFI;
- configurare prin variabile de mediu;
- metadate de versiune Docker.

### Corectat

- clasificarea imaginilor;
- extragerea ISO-urilor UDF cu 7-Zip;
- importurile WinPE fără `bootmgr` separat;
- căile BCD, SDI și WIM;
- rutele Flask duplicate;
- valorile locale hardcodate.

### Curățat

- backupurile;
- fișierele temporare;
- cache-urile Python;
- arhivele vechi.
