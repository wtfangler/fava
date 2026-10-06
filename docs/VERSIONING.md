# Numeracja wersji

Styl jak w większości popularnych paczek na Modrinth (np. Vanilla Perfected `1.0.3+26.2`, Fabulously Optimized `15.0.0-alpha.5`): zwykły `MAJOR.MINOR.PATCH`, a o stabilności mówi **kanał** wydania, nie numer.

```
<MAJOR.MINOR.PATCH>+<wersja gry>        np.  0.2.0+26.2   i   0.2.0+26.3
```

- **Jeden numer na wydanie, ten sam dla obu wersji gry.** Wersja gry jest po plusie, więc w Modrinth każda paczka ma własny, czytelny numer. Plik nazywa się `Fancy Vanilla 0.2.0 for 26.2.mrpack`.
- **0.x = faza wczesna (alpha/beta).** Kanał ustawia się przy wgrywaniu na Modrinth. **1.0.0** będzie pierwszym wydaniem stabilnym, nie wcześniej niż po dłuższej grze i teście serwera z graczami.
- Podbijanie: **PATCH** (0.1.1) to poprawki bez nowych funkcji; **MINOR** (0.2.0) to nowe funkcje, zmiana bazy optymalizacyjnej, nowe mody lub zmiana zachowania; **MAJOR** zmienia się przy 1.0.0 i przy zmianach łamiących istniejące światy.
- Numer jest w jednym miejscu: `VERSION` w `tools/build.py`. Baza Streamline Master (plik w `inputs/`) jest opisana w changelogu: 26.2 używa 1.5.2, 26.3 używa 1.6.2-beta.

Mody własne mają osobną numerację semantyczną i jej numer nie musi pasować do numeru paczki:

| Mod | Numer | Gdzie |
|---|---|---|
| TEMPERED | 2.20.0 | `tools/build_tempered.py` (`VERSION`) |
| Fancy Journal | 1.2.0 | `journal-mod/build.py` (`VERSION`), `tools/build.py` (`JOURNAL_VERSION`) |

Wcześniejsze numery 1.0 do 1.0.2 na stronie projektu Modrinth dotyczą starej koncepcji paczki, a robocze 2.x i krótkotrwałe 1.5.1.1/1.6.2.1 nie były publikowane.
