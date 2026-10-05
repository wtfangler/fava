# Fancy Vanilla 2.1.0: więcej questów i Epilog (przegląd Claude)

Data: 2026-10-05. Wydanie 2.1.0 = 2.0.4 Codexa + rozbudowa questów na prośbę użytkownika:
*więcej questów, w tym takich, które zatrzymają gracza po zabiciu smoka*. Oryginalne wydanie 2.0.4
(pliki w `dist/`) pozostaje nietknięte.

## Co się zmieniło

- **TEMPERED 2.17.0** (z 2.16.2). Oryginalne 89 zadań, nagrody i progi er są **bajt w bajt takie same**
  (test `tools/test_release.py` porównuje je z oryginalnym JAR-em 2.16.0). Dopisane tylko osiągnięcia opcjonalne.
- **+21 questów w erach** (3 na erę, razem 42), w konwencji Codexa: `tempered:bonus/<era>/<nazwa>`, bramka
  `tempered:age/N`, nagroda wyłącznie XP 10–30, osobny postęp, wpisy w `reset_bonus`.
- **Epilog: 35 questów po zabiciu smoka.** Ukryty korzeń `tempered:bonus/epilog/root` odblokowuje się, gdy gracz
  pokona Smoka Endu albo ma już vanillowe osiągnięcie `minecraft:end/kill_dragon` (istniejące światy).
  Cele: bossowie (Warden, starszy strażnik, skrzypiący, wicher, brutal), hodowla i oswajanie, budowle, mikstury i
  zaklęcia, kolekcje (głowy, płyty, netheryt, jajo smoka) i wyprawy (siedem struktur). Razem 1915 XP na osobę (nowe questy er: 455 XP).
  Pełna lista: `docs/QUESTS.md`. Generator: `tools/gen_more_quests.py` (źródło prawdy).
- **Fancy Journal 1.0.4** (z 1.0.3): zakładka złożona wyłącznie z questów opcjonalnych (Epilog) pokazuje licznik
  „x/y” zamiast „0/0”, a korzeń Epilogu nie jest kartą.
- `tools/build_tempered.py`: walidacja (42 questy er, Epilog ukryty i zależny od smoka, nagrody 25–200 XP) i konwersja
  schematu 26.2 → 26.3 rozszerzona o `player_generates_container_loot` (`loot_table` → `loot_tables`).

## Dowody

| Test | Wynik |
|---|---|
| Identyfikatory 56 nowych questów (bloki, przedmioty, moby, mikstury, efekty) | wszystkie istnieją w oficjalnych rejestrach 26.2 i 26.3 |
| Walidacja receptur z oficjalnymi serwerami | 83 strażników, 26.2 i 26.3 |
| `python -m unittest tools.test_release` | OK (hasze, wersje, układ questów, pokrycie `reset_bonus`, 89 oryginalnych zadań) |
| Serwer 26.2: czysty start, `/reload`, restart | 1862 osiągnięcia, 0 błędów parsowania |
| Serwer 26.3: czysty start, `/reload`, restart | 2040 osiągnięć, 0 błędów parsowania |
| Klient 26.2, scenariusz Codexa (progresja, blokady, układy, sekrety) | 63 asercje, exit 0 |
| Klient 26.3, scenariusz Codexa | 58 asercji, exit 0 |
| Klient 26.2 i 26.3, scenariusz Epilog | po 24 asercje, exit 0 |

Scenariusz Epilog (prawdziwy klient, pełna paczka, świat jednoosobowy): (1) Epilog jest zablokowany przed smokiem,
a quest „Zapas rakiet” nie zalicza się mimo posiadania 64 rakiet; (2) po nadaniu `minecraft:end/kill_dragon`
korzeń odblokowuje się sam; (3) `give` elytry, jaja smoka i zestawu nawigatora zalicza odpowiednie questy
naturalnym zdarzeniem inwentarza; (4) Dziennik pokazuje zakładkę Epilog, filtry i układ bez nakładania się
elementów (zrzuty w `test-logs/claude-2.1.0/`).

Logi: `test-logs/claude-2.1.0/`. Wszystkie przebiegi używały Java 25 (Zulu 25 z Modrinth App), Fabric 0.19.5,
świata wygenerowanego oficjalnym serwerem (seed 424242), 0 innych graczy.

## Ograniczenia (uczciwie)

- **Z 56 nowych questów w grze zaliczono 4 na każdej wersji** (elytra, jajo smoka, zestaw nawigatora, zapas rakiet).
  Pozostałe są sprawdzone **składniowo i rejestrowo** (serwer je wczytuje, identyfikatory istnieją), ale nie
  zdobywano ich w grze: m.in. walki z bossami, hodowla, budowanie zestawów bloków, mikstury, struktury.
  Warunki oparto o spróbowane wcześniej wzorce z oficjalnych osiągnięć vanilli.
- Warunek „przedmiot w ekwipunku” sprawdza zmieniony stos (zachowanie vanilli): jeśli gracz już trzyma wymagany
  przedmiot w chwili odblokowania Epilogu, quest zaliczy się po pierwszym przestawieniu/dobraniu tego stosu.
- Epilog nie wymaga obecności konkretnej ery TEMPERED, tylko pokonania smoka.
- Brak testu długiej gry, kilku graczy i wydajności. To nadal wydanie alpha.
- 26.3: pole `loot_tables` w `sky_ship` jest konwertowane przez builder; serwer 26.3 wczytuje je bez błędów, ale
  quest nie był zaliczany w grze.
