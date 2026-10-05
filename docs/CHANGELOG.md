# Changelog

## 2.3.0 alpha — Minecraft 26.2 / 26.3 — 05.10.2026

- Własny loader Fancy Vanilla (Fancy Journal 1.1.0): ciemny ekran z logo i paskiem postępu zamiast logo Mojang przy starcie gry i przeładowaniu zasobów oraz przy komunikatach typu „Zapisywanie świata”. Vanilla nadal steruje ładowaniem i wygaszaniem; nakładka tylko rysuje na wierzchu.
- Dwa języki (PL/EN): komunikaty komend administracyjnych (`help`, `diag`, `gate_on/off`, `set_age`, `reset`, status) korzystają teraz z kluczy tłumaczeń (TEMPERED 2.19.0), tak jak zadania i osiągnięcia. Wersja angielska działa po przełączeniu języka gry.
- Zadania opcjonalne: 63 w erach (po 9) i 55 w Epilogu (po zabiciu smoka); progi przejścia er bez zmian. Wbudowany przycisk „Postępy” w menu pauzy zastąpiono jednym dziennikiem pod klawiszem J.

## 2.0–2.2 (zbiorczo)

- Poprawiono zamykanie klienta z aktywnymi animowanymi teksturami: Fancy Journal kończy pulę roboczą Animatica przy wyjściu z gry.
- Kolejność paczek zasobów zachowuje Clearer Slot Highlight nad DARK, a lista wyjątków zgodności wynika z rzeczywistych metadanych pobranych ZIP-ów. Wariant 26.3 korzysta z przypiętej, zweryfikowanej czcionki 4.0.

- Fancy Journal 1.1.0: dopasowanie do okna, przewijanie zakładek/zadań, poprawna widoczność ukrytych osiągnięć, stabilny wybór zakładki i odświeżanie po zmianach postępu. Zwykły singleplayer zatrzymuje się jak przy ekranie vanilli.
- TEMPERED 2.19.0: wyłączenie ograniczeń przez gate_off przetrwa restart; gate_on ponownie je włącza. Reset obejmuje też nieobecnych graczy, set_age sprawdza zakres 1–7, a natywny sprzęt miedziany i włócznie mają przypisane poziomy. Ery pozostają globalne, z zachowanymi 89 zadaniami i stałymi progami. Dodano po trzy osobiste questy opcjonalne do każdej ery, z niewielkimi nagrodami XP; nie zwiększają wymaganego postępu ery.
- Dziennik otrzymał konfigurowalny skrót J oraz przycisk w menu pauzy. Zadania opcjonalne są oddzielone od licznika zadań potrzebnych do przejścia ery.
- ModernFix: przywrócono wyłączone czyszczenie ClassInfo i leniwe tworzenie rendererów. Poprzednie logi zawierały wyjątek klientowej klasy na serwerze oraz tworzenie renderera na CullThread klienta.
- 26.2: Particle Core korzysta z BOUNDING_BOX; jego optymalizacje i efekty wizualne zostają. Zoomify jest wybranym zoomem, ustawienie Chloride wyłączone i jego klawisz zwolniony.
- Paczki zasobów: poprawiona kolejność i usunięte powtórzenia. Clearer Slot Highlight znajduje się powyżej DARK; konfiguracje uwzględniają rzeczywisty zestaw modów danego wariantu.
- Zachowano identyfikację Fancy Vanilla: własne grafiki, menu, roślinność, animacje, efekty, dźwięk i opcjonalne shadery.
- Liczby składu obejmują całe locki i dwa dołączone mody: 26.2 — 102 pliki modów, 27 paczek zasobów, 2 shadery; 26.3 — 97, 27, 2.
- Instrukcje serwera opisują nowy katalog oraz ograniczony zakres `--no-download`. Lokalna strona odsyła do projektu Modrinth; nie zakłada istnienia opublikowanego adresu `/version/2.3.0`.

**Weryfikacja:** Potwierdzone testy uruchomieniowe 2.3.0: klient 26.2, klient 26.3, serwer 26.2, serwer 26.3. Zakres i logi: docs/CLAUDE_REVIEW_2.1.0.md oraz docs/CODEX_REVIEW.md. Test uruchomienia nie stanowi benchmarku FPS ani testu pojemności serwera. Wyniki z pięciu próbek wcześniejszej wersji usunięto z deklaracji wydajności.

### Różnice wariantu 26.3

Brak w tym locku: chloride, particle-core, wakes, particle-rain, betterf3, better-mount-hud. Paczki zasobów wykorzystujące wydania 26.2: simple-grass-flowers, better-leaves, fancy-crops, blocky-armor-stands, even-better-enchants, als-creepers-revamped, als-enderman-revamped-x-fresh-animations, als-scorpions-crabs-x-fresh-animations, als-skeletons-revamped-x-fresh-animations, qraftys-capitalized-font. Zgodność wyglądu wymaga sprawdzenia w grze.

## 2.0.3 alpha

Dodano pierwszą wersję Fancy Journal do paczek 26.2 i 26.3. Dostępne stare logi potwierdzają uruchomienia w kontrolowanych światach, ale zawierają też błędy konfiguracji oraz brak pobieranych paczek zasobów w tamtym teście. Nie należy traktować ich jako potwierdzenia bieżącego wydania ani jego wydajności.
