# Fancy Vanilla 2.4.0

Minecraft 26.2 / 26.3, Fabric, Java 25. Oprawa Fancy Vanilla, optymalizacja Streamline Master i progresja TEMPERED. Docelowo singleplayer i mały serwer ze znajomymi.

| Plik / katalog | Przeznaczenie |
|---|---|
| `releases/26.2/Fancy Vanilla 2.4.0 for 26.2.mrpack` | Klient Minecraft 26.2 |
| `releases/26.3/Fancy Vanilla 2.4.0 for 26.3.mrpack` | Klient Minecraft 26.3 |
| `docs/modrinth_description.md` | Opis PL/EN |
| `docs/CHANGELOG.md` | Zmiany wydania |
| `docs/CODEX_REVIEW.md` | Zakres weryfikacji i uwagi |
| `server/build_server.py`, `server/template/` | Budowa dedykowanego serwera |
| `site/` (źródło), `build/site/` (wynik) | Strona projektu; `python tools/build_site.py` składa ją i pakuje do ZIP-a do wdrożenia |
| `brand/`, `src/resourcepack/` | Oryginalna identyfikacja wizualna (logo, ikony, banery) |

## Skład

| Minecraft | Pliki modów | Paczki zasobów | Shadery |
|---|---:|---:|---:|
| 26.2 | 102 (100 + 2 własne) | 27 (26 + 1 własna) | 2 |
| 26.3 | 97 (95 + 2 własne) | 27 (26 + 1 własna) | 2 |

Dwa własne mody to TEMPERED 2.20.0 i Fancy Journal 1.2.0. Paczka FancyVanilla.zip jest własnym zasobem. Liczymy wszystkie wpisy obu locków oraz te pliki dołączone w overrides; nie tylko nowo dodane dodatki. Zagnieżdżone biblioteki nie są osobnymi plikami w tym zestawieniu.

## Instalacja i progresja

Zaimportuj wariant `.mrpack` zgodny z wersją gry. Klient: Java 25, początkowo 4–6 GB RAM; shadery są wyłączone. Zrób kopię istniejącego świata przed dodaniem progresji.

TEMPERED ma 7 er, 89 oryginalnych zadań, 63 nowych opcjonalnych celów w erach i 55 w gałęzi Epilog (po zabiciu smoka). Blokadę przepisów oraz osłabienia zbyt zaawansowanego sprzętu można włączyć lub wyłączyć. Pancerz i elytra nie są fizycznie zablokowane przed założeniem. TEMPERED jest datapackiem w formie moda. Usunięcie `TEMPERED2.20.0mc26.2.jar` usuwa funkcje po ponownym wczytaniu świata, ale pozostawia zapisaną regułę ograniczonego craftingu i odblokowane przepisy. **Przed usunięciem wywołaj gate_off.** Jeżeli plik już usunięto, administrator może użyć `/gamerule minecraft:limited_crafting false` oraz `/recipe give @a *` dla obecnych graczy (powtórz odblokowanie po dołączeniu nieobecnych).

Ery są globalne dla świata. Na serwerze osiągnięcia graczy przesuwają wspólną erę; nie ma trybu er indywidualnych. Stałe progi to **6/9, 9/15, 8/13, 8/13, 9/14, 8/13, 8/12**; nie trzeba zaliczyć wszystkich zadań. Paczka nie udostępnia konfiguracji tych progów.

Stan progresji sprawdzisz przez `/trigger tempered.menu` bez OP. Poniższe funkcje administracyjne wymagają uprawnień do komend (OP na serwerze lub komendy w świecie). Zmianę wspólnej ery i reset uzgodnij z pozostałymi graczami.

- Wyłącz blokadę przepisów i osłabienia sprzętu (ustawienie przetrwa restart): `/function tempered:admin/gate_off`.
- Ponownie włącz ograniczenia progresji: `/function tempered:admin/gate_on`.
- Ustaw wspólną erę, przykład ery 3 (dozwolone 1–7): `/function tempered:admin/set_age {n:3}`.
- Wyzeruj postęp wszystkich graczy, także nieobecnych; używaj świadomie: `/function tempered:admin/reset`.

Fancy Journal otwierasz przez **J**, przycisk **Dziennik** w menu pauzy lub **L**. Własny skrót jest konfigurowalny. Dostępne są wyszukiwarka, filtry, przewijanie i klasyczny ekran pod **Shift**. Dziennik zachowuje widoczność ukrytych osiągnięć, stabilny wybór zakładki i aktualizuje listę po zmianach postępu. Zatrzymuje zwykły singleplayer; na serwerze nie zatrzymuje świata.

Dodatkowe questy (9 w każdej erze oraz 55 w Epilogu po zabiciu smoka) są osobiste, opcjonalne i nagradzane XP. Nie liczą się do progu przejścia wspólnej ery. [Lista nowych zadań](docs/QUESTS.md).

## Serwer

Gracze instalują ten sam wariant paczki. Buduj w **nowym katalogu**; nie nadpisuj istniejącej instalacji z innym zestawem modów.

```powershell
python server/build_server.py "releases/26.2/Fancy Vanilla 2.4.0 for 26.2.mrpack" moj_serwer_26_2 --ram 4G
python server/build_server.py "releases/26.3/Fancy Vanilla 2.4.0 for 26.3.mrpack" moj_serwer_26_3 --ram 4G
```

W paczce serwerowej pobranej jako osobny ZIP skrypt jest w katalogu głównym: użyj `python build_server.py ...` i zachowaj katalog `template` obok niego. Przeczytaj EULA, zaakceptuj ją samodzielnie w `eula.txt`, a następnie uruchom `start.bat` lub `start.sh` na Java 25. Builder sprawdza hashe modów, wybiera stronę serwerową i zachowuje istniejące ustawienia/start scripts; nie zarządza światem.

Domyślne `view-distance=8`, `simulation-distance=6`, limit 15 graczy i 4 GB maksymalnej pamięci są ustawieniami startowymi, nie potwierdzoną pojemnością serwera. Zacznij od kilku znajomych, potem oceń czasy ticków przez spark. Chunky służy do przygotowania terenu, FastBack do kopii zapasowych. Zweryfikuj konfigurację backupu i możliwość odtworzenia świata przed dłuższą grą.

`--no-download` tworzy konfiguracje/skrypty i dołączone mody. **Nie tworzy kompletnego, gotowego do uruchomienia serwera.** W nowym katalogu nie dostarcza pobieranych modów ani Fabric launchera.

## Budowa ze źródeł

`tools/resolve.py` ustala locki; aktualizacja wymaga świadomego wyboru. Następnie zbuduj TEMPERED i Fancy Journal zgodnie z ich narzędziami, potem paczki:

```powershell
python tools/build.py --mc 26.2
python tools/build.py --mc 26.3
python tools/check_deps.py KATALOG_JAROW_26_2 --side both --index "releases/26.2/Fancy Vanilla 2.4.0 for 26.2.mrpack" --fabric-loader-jar FABRIC_LOADER_0_19_5_JAR
python tools/check_deps.py KATALOG_JAROW_26_3 --side both --index "releases/26.3/Fancy Vanilla 2.4.0 for 26.3.mrpack" --fabric-loader-jar FABRIC_LOADER_0_19_5_JAR
python tools/gen_docs.py
```

Kontrola zależności jest domyślnie offline; `--download` jawnie pozwala pobrać brakujące pliki. Oba katalogi audytu muszą zawierać także dwa jary z `overrides/mods`. Podaj rzeczywisty JAR Fabric Loader, żeby uwzględnić jego dołączone biblioteki. Po zmianie locka odczytaj metadane zasobów przez `python tools/annotate_resources.py --mc 26.2 --cache KATALOG_RESOURCEPACKS` (analogicznie 26.3; `--download` pobiera brakujące pliki). Budowanie Dziennika wymaga Java 25, zestawu klienta/bibliotek w `--dev-dir` oraz właściwego Fabric API w `--fabric-api`. Generator dokumentacji wymaga gotowych paczek i zgodnych SHA512. Zachowuje istniejącą oprawę strony i generuje ZIP w pamięci, bez rozpakowywania i kasowania katalogów. Nie trzeba ponownie uruchamiać `gen_assets.py` do zwykłej budowy wydania.

## Różnice i status testów

26.3 nie zawiera: chloride, particle-core, wakes, particle-rain, betterf3, better-mount-hud. Wydania zasobów użyte jako fallback z 26.2: simple-grass-flowers, better-leaves, fancy-crops, blocky-armor-stands, even-better-enchants, als-creepers-revamped, als-enderman-revamped-x-fresh-animations, als-scorpions-crabs-x-fresh-animations, als-skeletons-revamped-x-fresh-animations, qraftys-capitalized-font.

Potwierdzone testy uruchomieniowe 2.4.0: klient 26.2, klient 26.3, serwer 26.2, serwer 26.3. Zakres i logi: docs/CLAUDE_REVIEW_2.1.0.md oraz docs/CODEX_REVIEW.md. Nie podajemy wyniku FPS z pięciu próbek jako benchmarku. Do dalszych testów należą dłuższa gra, istniejący świat, shader i obciążenie małego serwera. [Projekt Modrinth](https://modrinth.com/modpack/fava).
