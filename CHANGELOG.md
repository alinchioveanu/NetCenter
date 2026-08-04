# Changelog

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
