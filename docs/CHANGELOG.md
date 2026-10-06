# Changelog

## 0.1.0 alpha — Minecraft 26.2 / 26.3 — 06.10.2026

- Pierwsze wydanie w numeracji `MAJOR.MINOR.PATCH+wersja gry` (zasady w `docs/VERSIONING.md`); dotychczasowe numery robocze 2.x nie były publikowane.
- **26.3** stoi na nowej bazie optymalizacyjnej **Streamline Master 1.6.2-beta** (własna wersja autora dla 26.3): mody bazy są w dokładnie tych wersjach, które wskazuje jej paczka, razem z jej ustawieniami i konfiguracjami. Dodatki Fancy Vanilla (oprawa, TEMPERED, Fancy Journal, loader) zostają. **26.2** stoi na Streamline Master 1.5.1.
- Śledzenie zadań (Fancy Journal 1.2.0): pinezka przy każdym zadaniu w dzienniku. Panel w prawym dolnym rogu ekranu pokazuje nazwę zadania, opis, listę wymagań z haczykami i liczniki (np. „Zdobądź: Dowolne deski 20/32”): przedmioty liczone są z ekwipunku, reszta ze statystyk gracza, a przy zadaniach wieloetapowych każdy krok ma osobny haczyk. Po ukończeniu panel znika sam. Wybór i róg panelu (`corner`) zapisują się w `config/fancy_journal.json`. Tylko 26.2 i 26.3. Uwaga: liczniki ze statystyk to statystyki całego życia gracza w świecie, więc w świecie założonym przed TEMPERED mogą wyprzedzać wewnętrzny licznik zadania; panel nie pokaże wtedy ukończenia przed serwerem.
- Nowa ikona moda TEMPERED (TEMPERED 2.20.0).
- Usunięto mod Remove Reloading Screen (RRLS): Controlify blokuje go przy każdym uruchomieniu, a własny loader rysuje się niezależnie od niego. Zalecana pamięć klienta to teraz 6 GB (paczka ma ponad 100 modów).
- Opisy modów w Mod Menu zależą od języka gry (po angielsku i po polsku), tak jak zadania, komendy i dziennik. Język wybiera się w grze: Opcje > Język; moda nie mają osobnego przełącznika.

## Robocze 2.3.0 (poprzednia numeracja, nieopublikowane)

- Własny loader Fancy Vanilla (Fancy Journal 1.1.0): ciemny ekran z logo i paskiem postępu zamiast logo Mojang przy starcie gry i przeładowaniu zasobów oraz przy komunikatach typu „Zapisywanie świata”. Vanilla nadal steruje ładowaniem i wygaszaniem; nakładka tylko rysuje na wierzchu.
- Dwa języki (PL/EN): komunikaty komend administracyjnych (`help`, `diag`, `gate_on/off`, `set_age`, `reset`, status) korzystają teraz z kluczy tłumaczeń (TEMPERED 2.19.0), tak jak zadania i osiągnięcia. Wersja angielska działa po przełączeniu języka gry.
- Zadania opcjonalne: 63 w erach (po 9) i 55 w Epilogu (po zabiciu smoka); progi przejścia er bez zmian. Wbudowany przycisk „Postępy” w menu pauzy zastąpiono jednym dziennikiem pod klawiszem J.

## Robocze 2.0–2.2 (nieopublikowane)

- Poprawiono zamykanie klienta z aktywnymi animowanymi teksturami: Fancy Journal kończy pulę roboczą Animatica przy wyjściu z gry.
- Kolejność paczek zasobów zachowuje Clearer Slot Highlight nad DARK, a lista wyjątków zgodności wynika z rzeczywistych metadanych pobranych ZIP-ów. Wariant 26.3 korzysta z przypiętej, zweryfikowanej czcionki 4.0.

- Fancy Journal 1.2.0: dopasowanie do okna, przewijanie zakładek/zadań, poprawna widoczność ukrytych osiągnięć, stabilny wybór zakładki i odświeżanie po zmianach postępu. Zwykły singleplayer zatrzymuje się jak przy ekranie vanilli.
- TEMPERED 2.20.0: wyłączenie ograniczeń przez gate_off przetrwa restart; gate_on ponownie je włącza. Reset obejmuje też nieobecnych graczy, set_age sprawdza zakres 1–7, a natywny sprzęt miedziany i włócznie mają przypisane poziomy. Ery pozostają globalne, z zachowanymi 89 zadaniami i stałymi progami. Dodano po trzy osobiste questy opcjonalne do każdej ery, z niewielkimi nagrodami XP; nie zwiększają wymaganego postępu ery.
- Dziennik otrzymał konfigurowalny skrót J oraz przycisk w menu pauzy. Zadania opcjonalne są oddzielone od licznika zadań potrzebnych do przejścia ery.
- ModernFix: przywrócono wyłączone czyszczenie ClassInfo i leniwe tworzenie rendererów. Poprzednie logi zawierały wyjątek klientowej klasy na serwerze oraz tworzenie renderera na CullThread klienta.
- 26.2: Particle Core korzysta z BOUNDING_BOX; jego optymalizacje i efekty wizualne zostają. Zoomify jest wybranym zoomem, ustawienie Chloride wyłączone i jego klawisz zwolniony.
- Paczki zasobów: poprawiona kolejność i usunięte powtórzenia. Clearer Slot Highlight znajduje się powyżej DARK; konfiguracje uwzględniają rzeczywisty zestaw modów danego wariantu.
- Zachowano identyfikację Fancy Vanilla: własne grafiki, menu, roślinność, animacje, efekty, dźwięk i opcjonalne shadery.
- Liczby składu obejmują całe locki i dwa dołączone mody: 26.2 — 101 pliki modów, 27 paczek zasobów, 2 shadery; 26.3 — 104, 27, 2.
- Instrukcje serwera opisują nowy katalog oraz ograniczony zakres `--no-download`. Lokalna strona odsyła do projektu Modrinth; nie zakłada istnienia opublikowanego adresu `/version/0.1.0`.

**Weryfikacja:** Potwierdzone testy uruchomieniowe 0.1.0: klient 26.2, klient 26.3, serwer 26.2, serwer 26.3. Zakres i logi: docs/CLAUDE_REVIEW_2.1.0.md oraz docs/CODEX_REVIEW.md. Test uruchomienia nie stanowi benchmarku FPS ani testu pojemności serwera. Wyniki z pięciu próbek wcześniejszej wersji usunięto z deklaracji wydajności.

### Różnice wariantu 26.3

Brak w tym locku: wakes, particle-rain, better-mount-hud. Paczki zasobów wykorzystujące wydania 26.2: brak. Zgodność wyglądu wymaga sprawdzenia w grze.

**Mody zbudowane pod inną wersję gry** (autorzy oznaczają je jako zgodne): 26.2: Chat Heads (26.1), Falling Leaves (26.1), Fast IP Ping (26.1.2), Visuality (26.3); 26.3: Async Logger (26.1.2), Entity View Distance (26.2), Explosive Enhancement (26.2), FastQuit (26.2), Glowing Torchflower (26.2), Main Menu Credits (26.2), Make Bubbles Pop (26.2).

**Mody w wersjach beta i alpha:** 26.2: Concurrent Chunk Management Engine (Fabric) (beta), EclipseUI (beta), OptiGUI (beta), Particle Rain (beta), Smooth Swapping (beta), Sound Physics Remastered (beta), Sounds (beta), Very Many Players (Fabric) (alpha), Visuality (beta), Wakes (beta); 26.3: Better Clouds (beta), Better Statistics Screen (beta), EclipseUI (beta), OptiGUI (beta), Smooth Swapping (beta), Sound Physics Remastered (beta), TCDCommons API (beta), Visuality (beta). Przed dłuższą grą na serwerze sprawdź FastBack i odtworzenie świata.

## Robocze 2.0.3 (nieopublikowane)

Dodano pierwszą wersję Fancy Journal do paczek 26.2 i 26.3. Dostępne stare logi potwierdzają uruchomienia w kontrolowanych światach, ale zawierają też błędy konfiguracji oraz brak pobieranych paczek zasobów w tamtym teście. Nie należy traktować ich jako potwierdzenia bieżącego wydania ani jego wydajności.
