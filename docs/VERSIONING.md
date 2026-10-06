# Numeracja wersji

Jeden styl dla wszystkich paczek Fancy Vanilla:

```
<wersja bazy Streamline Master>.<rewizja Fancy Vanilla na tej bazie>
```

| Paczka | Baza Streamline Master | Rewizja | Numer |
|---|---|---:|---|
| Minecraft 26.2 | 1.5.1 | 1 | **1.5.1.1** |
| Minecraft 26.3 | 1.6.2 (beta) | 1 | **1.6.2.1** |

- Numer bazy jest brany z nazwy pliku w `inputs/` (`Streamline Master <wersja>...mrpack`), a `tools/build.py` składa z niego numer paczki (`VERSIONS`). Nie wpisuje się go ręcznie.
- **Rewizja** (`REVISION` w `tools/build.py`) rośnie o 1, gdy paczka się zmienia, a baza zostaje ta sama: nowy mod, zmiana konfiguracji, nowa wersja TEMPERED lub Fancy Journal. Gdy zmienia się baza, rewizja wraca do 1.
- Każda wersja gry ma własny numer, bo ma własną bazę.
- Kanał (alpha, beta, release) ustawia się przy wgrywaniu na Modrinth; nie jest częścią numeru.

Mody własne mają osobną, zwykłą numerację semantyczną `MAJOR.MINOR.PATCH` i ich numer nie musi pasować do numeru paczki:

| Mod | Numer | Gdzie |
|---|---|---|
| TEMPERED | 2.20.0 | `tools/build_tempered.py` (`VERSION`) |
| Fancy Journal | 1.2.0 | `journal-mod/build.py` (`VERSION`), `tools/build.py` (`JOURNAL_VERSION`) |

Wersje robocze sprzed tego schematu (2.0 do 2.4.x) nie były publikowane i zostały zastąpione numeracją powyżej.
