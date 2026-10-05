# Fancy Vanilla

**Minecraft 26.2 i 26.3 · Fabric · singleplayer i mały serwer ze znajomymi · 2.4.0 alpha**

Znany Minecraft z bogatszą oprawą: animacje mobów, roślinność, cząsteczki, dźwięk, tekstury i opcjonalne shadery. Rdzeń **Streamline Master** odpowiada za optymalizację, a autorski **TEMPERED** porządkuje przygodę w 7 er: 89 oryginalnych zadań oraz 63 nowych zadań opcjonalnych w erach i gałąź **Epilog** z 55 celami po zabiciu smoka. Paczka nie dodaje bloków, mobów ani biomów.

### TEMPERED i własna baza

Zadania prowadzą od drewna do wypraw po Endzie, zostawiając miejsce na budowanie i własne cele. Przepisy wyższych er mogą być blokowane do odpowiedniej ery. Zbyt zaawansowany sprzęt jest ograniczany przez efekty i osłabienia; nie oznacza to fizycznego zakazu zakładania pancerza czy używania elytry. Usunięcie pliku TEMPERED usuwa jego funkcje po ponownym wczytaniu świata, ale nie cofa zapisanej reguły ograniczonego craftingu ani stanu odblokowanych przepisów. Najpierw wyłącz ograniczenia komendą opisaną poniżej.

Ery są **wspólne dla świata**: w singleplayer odblokowujesz je sam, a na serwerze postęp graczy przesuwa wspólną erę. Nie trzeba wykonywać wszystkich zadań, aby przejść dalej: progi kolejnych er to **6/9, 9/15, 8/13, 8/13, 9/14, 8/13, 8/12**. Są stałe; paczka nie oferuje przełącznika er indywidualnych ani konfiguracji tych progów. Administrator może wyłączyć ograniczenia przez `/function tempered:admin/gate_off` i włączyć je przez `/function tempered:admin/gate_on`; wybór przetrwa przeładowanie i restart. Stan sprawdzisz przez `/trigger tempered.menu`.

### Oprawa i wygoda

**Wygląd i animacje:** Entity Model Features, Entity Texture Features, Not Enough Animations, 3D Skin Layers, OptiGUI, Animatica Refabricated, BetterGrassify, Better Clouds, Puzzle.

**Atmosfera i dźwięk:** Ambient Environment, Falling Leaves, Wakes, Visuality, Subtle Effects, Explosive Enhancement, Particle Rain, Particular Reforged, Particle Effects, LambDynamicLights - Dynamic Lights, Make Bubbles Pop, Glowing Torchflower, AmbientSounds, Sound Physics Remastered, Sounds.

**Informacje i wygoda:** Jade, AppleSkin, BetterF3, Better Statistics Screen, Bookshelf Inspector, Durability Tooltip, Status Effect Bars, Inventory Sorting, Searchables, More Chat History, Chat Heads, Controlify (Controller support), Controlling, Xaero's Minimap, Xaero's World Map.

**Narzędzia serwera:** Clumps, Chunky, spark, Fast Backups.

**Shadery:** Complementary Shaders - Reimagined, Miniature Shader. Są domyślnie wyłączone. W ustawieniach Sterowania sprawdzisz skróty Iris do wyboru i przełączania shaderów. **Zoomify** obsługuje przybliżenie pod C. Fancy Vanilla zachowuje własne logo, menu oraz paczkę zasobów.

### Fancy Journal 1.2.0

Naciśnij **J** lub wybierz **Dziennik** w menu pauzy. Własny skrót zmienisz w ustawieniach sterowania. Klawisz osiągnięć **L** również otwiera dziennik z zakładkami, postępem, wyszukiwaniem i filtrami: Wszystkie, Pozostałe, Ukończone. Układ dopasowuje się do rozmiaru okna; listy i zadania można przewijać, a wybór zakładki pozostaje stabilny. Ukryte nieukończone zadania nie są ujawniane. Lista aktualizuje się po zmianach osiągnięć, bez pełnego przebudowywania w każdej klatce. W singleplayer otwarty dziennik zatrzymuje grę jak klasyczny ekran osiągnięć; na serwerze gra trwa dalej. **Shift** przy otwieraniu lub „Klasyczny widok” pozwala wrócić do ekranu vanilli. Zakładki przełączysz także przez **Ctrl+PageUp/PageDown**, a zadania przewiniesz przez **PageUp/PageDown/Home/End**.

Każda era ma 9 dodatkowych celów dla własnej bazy i wypraw. Po pokonaniu Smoka Endu odblokowuje się ukryta zakładka **Epilog**: 55 opcjonalnych celów, które dają co robić po końcu gry. Wszystkie są oznaczone jako **opcjonalne**, mają osobisty postęp i nagrody XP. Nie zwiększają licznika przejścia do kolejnej ery ani nie zmieniają powyższych progów. Lista: [nowe questy](QUESTS.md).

### Instalacja

1. Zaimportuj `.mrpack` do Modrinth App lub Prism Launcher i wybierz wariant zgodny z wersją Minecrafta.
2. Użyj **Java 25**. Zacznij od 6 GB RAM dla klienta (paczka ma ponad 100 modów), dobierając ustawienia do swojego komputera.
3. W nowym świecie progresja zaczyna się od drewna. Przed dodaniem paczki do istniejącego świata zrób kopię; obecny ekwipunek może przekraczać początkową erę.

Paczka nadaje się do singleplayer i małego serwera znajomych. Instrukcja budowy serwera, jego ustawienia startowe oraz funkcje administracyjne są w README. Shadery i wysokość renderowania zwiększają obciążenie; nie podajemy gwarancji FPS ani liczby graczy.

### Warianty

| Minecraft | Pliki modów | Paczki zasobów | Shadery |
|---|---:|---:|---:|
| 26.2 | 101 (99 + 2 własne) | 27 (26 + 1 własna) | 2 |
| 26.3 | 96 (94 + 2 własne) | 27 (26 + 1 własna) | 2 |

Liczby dotyczą plików w paczce. Fabric może raportować więcej modułów, ponieważ biblioteki zawierają zagnieżdżone jary.

**26.3:** wariant nie zawiera: chloride, particle-core, wakes, particle-rain, betterf3, better-mount-hud. Następujące paczki zasobów korzystają z wydań oznaczonych dla 26.2: simple-grass-flowers, better-leaves, fancy-crops, blocky-armor-stands, even-better-enchants, als-creepers-revamped, als-enderman-revamped-x-fresh-animations, als-scorpions-crabs-x-fresh-animations, als-skeletons-revamped-x-fresh-animations, qraftys-capitalized-font. Ich zgodność deklarowana przez autorów jest węższa, dlatego wygląd wymaga sprawdzenia w grze.

**Mody zbudowane pod inną wersję gry** (autorzy oznaczają je jako zgodne): 26.2: Chat Heads (26.1), Falling Leaves (26.1), Fast IP Ping (26.1.2), Visuality (26.3); 26.3: Almanac (26.2), Explosive Enhancement (26.2), FastQuit (26.2), Glowing Torchflower (26.2), Main Menu Credits (26.2), Make Bubbles Pop (26.2).

**Mody w wersjach beta i alpha:** 26.2: Concurrent Chunk Management Engine (Fabric) (beta), EclipseUI (beta), OptiGUI (beta), Particle Rain (beta), Smooth Swapping (beta), Sound Physics Remastered (beta), Sounds (beta), Very Many Players (Fabric) (alpha), Visuality (beta), Wakes (beta); 26.3: Better Clouds (beta), Better Statistics Screen (beta), Concurrent Chunk Management Engine (Fabric) (alpha), EclipseUI (beta), OptiGUI (beta), ScalableLux (alpha), Smooth Swapping (beta), Sound Physics Remastered (beta), TCDCommons API (beta), Very Many Players (Fabric) (alpha), Visuality (beta). Przed dłuższą grą na serwerze sprawdź FastBack i odtworzenie świata.

**Weryfikacja:** Potwierdzone testy uruchomieniowe 2.4.0: klient 26.2, klient 26.3, serwer 26.2, serwer 26.3. Zakres i logi: docs/CLAUDE_REVIEW_2.1.0.md oraz docs/CODEX_REVIEW.md. Testy uruchomienia nie zastępują dłuższej gry ze znajomymi ani porównania wydajności. Dobór shaderów i efekty nakładających się tekstur wymagają oceny na docelowym sprzęcie.

[Projekt Fancy Vanilla na Modrinth](https://modrinth.com/modpack/fava). Pliki i strona WWW powstają lokalnie; samo przygotowanie wydania nie oznacza publikacji.

---

# Fancy Vanilla — English

**Minecraft 26.2 and 26.3 · Fabric · singleplayer and a small server with friends · 2.4.0 alpha**

Familiar Minecraft with richer animation, foliage, particles, audio, textures and optional shaders. **Streamline Master** provides the optimisation base. The author's **TEMPERED** progression adds 7 ages, preserving 89 original quests and adding 63 optional quests plus an **Epilogue** branch of 55 goals after the Ender Dragon, without adding blocks, mobs or biomes.

Higher-age recipes can be locked. Higher-age equipment is restricted through effects and penalties; armour and elytra are not physically prevented from being equipped. Removing the TEMPERED jar removes its functions after reloading the world, but saved limited-crafting rules and recipe unlocks remain. Disable the gates before removing it. Ages are shared across the world: play alone in singleplayer or advance a shared age with friends. Fixed quest thresholds are **6/9, 9/15, 8/13, 8/13, 9/14, 8/13, 8/12**. Individual ages and custom thresholds are not provided. Administrators can disable gates through `/function tempered:admin/gate_off` and restore them through `/function tempered:admin/gate_on`; the setting survives reloads and restarts. Players can check status through `/trigger tempered.menu`.

**Fancy Journal 1.2.0** opens with configurable **J**, the **Journal** button in the pause menu, or **L**, providing a responsive layout, scrolling tabs/tasks, search, filters and progress. Hidden unfinished tasks remain hidden; selected tabs stay stable and the list refreshes when progress changes. It pauses an ordinary singleplayer game like the vanilla advancement screen, while multiplayer keeps running. Hold **Shift** when opening or use *Classic view* for the vanilla screen. **Ctrl+PageUp/PageDown** switches tabs and **PageUp/PageDown/Home/End** scrolls tasks. Each age has 9 extra optional goals for exploration and building, and a hidden **Epilogue** tab unlocks after the Ender Dragon with 55 more; their personal progress and XP rewards do not change the shared age thresholds.

Import the matching `.mrpack` in Modrinth App or Prism Launcher, use **Java 25**, and start with 6 GB client RAM (the pack has over 100 mods). Back up existing worlds before installing: existing equipment may exceed the initial age. Shaders are off by default; rendering settings should be chosen for your hardware.

The 26.2 variant contains **101 top-level mod files**, **27 resource packs** and **2 shader packs**; 26.3 contains **96**, **27** and **2** respectively. Each includes two custom mods, TEMPERED and Fancy Journal. Nested libraries increase the number reported by Fabric.

The 26.3 variant omits: chloride, particle-core, wakes, particle-rain, betterf3, better-mount-hud. Resource packs using 26.2-labelled releases: simple-grass-flowers, better-leaves, fancy-crops, blocky-armor-stands, even-better-enchants, als-creepers-revamped, als-enderman-revamped-x-fresh-animations, als-scorpions-crabs-x-fresh-animations, als-skeletons-revamped-x-fresh-animations, qraftys-capitalized-font; inspect their appearance in game.

**Mods built for another game version** (their authors tag them as compatible): 26.2: Chat Heads (26.1), Falling Leaves (26.1), Fast IP Ping (26.1.2), Visuality (26.3); 26.3: Almanac (26.2), Explosive Enhancement (26.2), FastQuit (26.2), Glowing Torchflower (26.2), Main Menu Credits (26.2), Make Bubbles Pop (26.2).

**Beta and alpha mods:** 26.2: Concurrent Chunk Management Engine (Fabric) (beta), EclipseUI (beta), OptiGUI (beta), Particle Rain (beta), Smooth Swapping (beta), Sound Physics Remastered (beta), Sounds (beta), Very Many Players (Fabric) (alpha), Visuality (beta), Wakes (beta); 26.3: Better Clouds (beta), Better Statistics Screen (beta), Concurrent Chunk Management Engine (Fabric) (alpha), EclipseUI (beta), OptiGUI (beta), ScalableLux (alpha), Smooth Swapping (beta), Sound Physics Remastered (beta), TCDCommons API (beta), Very Many Players (Fabric) (alpha), Visuality (beta). Before long server sessions, check FastBack and world re-creation.

**Validation:** Confirmed 2.4.0 runtime checks: client 26.2, client 26.3, server 26.2, server 26.3. Scope and logs: docs/CLAUDE_REVIEW_2.1.0.md and docs/CODEX_REVIEW.md. Launch checks do not establish a performance benchmark or multiplayer capacity. Visual combinations and shaders need testing on your hardware.

[Fancy Vanilla on Modrinth](https://modrinth.com/modpack/fava). Preparing local archives does not publish them.
