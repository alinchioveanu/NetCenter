# Changelog

## 2.0.0 — 2026-08-03

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
