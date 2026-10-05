# Przegląd i poprawki Fancy Vanilla 2.0.4

Data pracy: 2026-10-04/05. Status: **ukończono; oba warianty 2.0.4 alpha przeszły testy**.
Źródłem aktualnego wydania jest `fava/FancyVanilla-26.2/`, także dla Minecrafta 26.3.
Zachowano oryginalne grafiki, markę Fancy Vanilla, zawartość vanilli i globalną
progresję TEMPERED. Nie dodano worldgenu ani systemów z Expedition.

## Gotowe poprawki

- **Fancy Journal 1.0.3:** własny konfigurowalny skrót J i przycisk Dziennik
  w menu pauzy. Zamknięcie z tego przycisku wraca do pauzy. Kompaktowy układ
  wyszukiwarki i filtrów, przewijane
  zakładki z przyciętymi obszarami kliknięć, stabilny wybór zakładki przez ID,
  ukrywanie nieukończonych sekretów oraz zadania korzeni vanilli. Dane są
  przebudowywane po aktualizacjach serwera; przywrócono pauzę singleplayera,
  obsługę klawiatury i narracji oraz opis progów er w tooltipie.
- **TEMPERED 2.16.2:** poprawne wykrywanie wymiaru gracza i kopiowanie stanu
  blokady dla każdego gracza osobno. Miedź, włócznie oraz pełny netheritowy
  smithing należą do istniejących er. 83 ukryte osiągnięcia receptur zabezpieczają
  przed odblokowaniem sprzętu przez zwykłe odkrywanie receptur; nie dodano
  odpytywania co tick. Wszystkie 89 zadań, nagrody i siedem progów zachowano.
- Na dalszą prośbę użytkownika dodano **21 osobistych zadań opcjonalnych**,
  po trzy na każdą erę: baza, ogród, wyprawy, archeologia, kolej i przyczółek Endu.
  Lista jest w `docs/QUESTS.md`. Dają razem 410 XP na osobę, nie zwiększają
  `#done`, wymagają odblokowanej ery i korzystają ze zdarzeń vanilli. Licznik
  wymaganych zadań w Dzienniku pozostaje osobny. Zmiana ery administracyjnie
  zachowuje bonusy; wyraźny reset zeruje je także po powrocie nieobecnego gracza.
- `gate_off/on` obejmuje crafting i osłabienia sprzętu oraz przetrwa restart.
  Reset czyści także wyniki nieobecnych graczy i oba liczniki miedzi; zmiana
  generacji postępu synchronizuje ich widok po powrocie. `set_age` przyjmuje 1–7.
- ModernFix: wyłączone wymuszone czyszczenie ClassInfo i leniwe tworzenie
  rendererów, które powodowały wyjątki serwera i renderera na CullThread.
  ParticleCore 26.2 używa BOUNDING_BOX. C pozostaje skrótem Zoomify.
- Clearer Slot Highlight ma pierwszeństwo przed DARK. Lista wyjątków zgodności
  zasobów wynika z metadanych ZIP-ów, z poprawną obsługą granic minor. Czcionka
  26.3 jest przypięta do zweryfikowanej wersji 4.0.
- Animatica 0.6.2 dla 26.3 pozostawia cztery wątki po użyciu animowanych zasobów.
  Klientowy dodatek kończy tę pulę przy wyjściu. Wersja 26.2 ma już własną
  poprawkę autora i dodatkowe sprzątanie jest tam pomijane.
- Opisy liczą cały skład: **102 / 97 plików modów**, **27 paczek zasobów**,
  **2 opcjonalne shadery**. Wyjaśniają wspólne ery, rzeczywiste osłabienia
  sprzętu i stan świata pozostający po usunięciu JAR-a.

## Dowody i zakres sprawdzenia

- Oba JAR-y TEMPERED: 379 wpisów; 83 receptury i lokalizacje ich osiągnięć
  zweryfikowane wobec oficjalnych serwerów 26.2 / 26.3. Format danych 107.1 / 121.0.
- Kompilacja obu wariantów Dziennika; test sortowania bardzo długich identyfikatorów.
- Kontrola gotowych archiwów, sum SHA512, składu, konfiguracji i kolejności zasobów;
  testy semantyki formatów oraz 11 regresji narzędzia zależności.
- Niezależne odbudowanie obu paczek daje identyczne bajty. Audyt z rzeczywistym
  Loaderem 0.19.5: 102 / 97 JAR-ów wydania, zero błędów zależności; 22 / 17
  ostrzeżeń o opcjonalnych rekomendacjach i alternatywach bibliotek zagnieżdżonych.
- Dedykowany serwer 26.2 i 26.3: czysty start, `/reload`, restart, aktywny datapack,
  trwałe wyłączenie blokad, reset dwóch liczników nieobecnego właściciela wyniku.
  **0 graczy**, Java Temurin 25.0.4.1, Fabric 0.19.5, heap 2 GB,
  seed 20261005204. Finalne logi i `server-probe.json` są w
  `test-logs/codex-2.0.4/server-quests/`; wcześniejsze próby zachowano osobno.
  **20 asercji na wersję**, 1805 / 1983 osiągnięcia przy starcie, przeładowaniu
  i restarcie, czyli dokładnie 21 więcej niż w poprzedniej próbie. Nie ma błędów
  predykatów TEMPERED. Osobista epoka bonusów przetrwa restart; `set_age` jej
  nie zmienia, reset zwiększa ją o jeden. Zestawy 39 / 40 JAR-ów serwera
  porównano bajtowo z finalnym wydaniem; wszystkie cztery uruchomienia zakończyły
  się kodem 0.
- Klient testowy pobiera **wszystkie** mody, paczki zasobów i shadery, sprawdzając
  oba hashe i rozmiary plików. Shadery pozostają wyłączone. Scenariusz obejmuje
  receptury, przejścia Nether/End, kilka skal GUI, sekrety i klasyczny ekran.
  Niekompletne, wcześniejsze próby pozostają w katalogu tymczasowym jako diagnostyka.
- Końcowe klienty **26.2 i 26.3 zakończyły się kodem 0**. Naturalne zdobycie
  kompasu i mapy zalicza `survey_kit` dopiero po odblokowaniu ery 3, nie zmienia
  globalnego licznika. `set_age` zachowuje bonus, reset go usuwa. Dziennik
  utrzymuje pierwotne 4/9 ery 1 oraz osobną pulę trzech celów opcjonalnych;
  zapamiętuje ID ery 7, ukrywa nieukończony sekret i pokazuje go po ukończeniu.
  J otwiera istniejący Dziennik, przycisk w pauzie mieści się w kompaktowym GUI,
  a zamknięcie wraca do menu pauzy. Klasyczny widok pozostaje dostępny.
  Logi, po pięć screenshotów i `client-probe.json` są w
  `test-logs/codex-2.0.4/`. Na 26.3 potwierdzono zakończenie wszystkich czterech
  wątków Animatica; 26.2 używa własnej poprawki autora. Wszystkie 27 paczek
  zasobów są zaznaczone, własne menu jest ostatnie, oba shadery zainstalowane
  i nieaktywne.

Test resetu nieobecnego właściciela wyniku używa wpisu scoreboard; nie zastępuje
sesji z wracającym rzeczywistym graczem. Nie wykonano długiej gry ani obciążenia
kilkoma graczami. To wydanie alpha, bez deklaracji benchmarku FPS lub pojemności
serwera. W logach pozostają komunikaty Windows Perflib, autoryzacji konta testowego
i opcjonalnych integracji. Controlify blokuje usuwanie pierwszego ekranu
ładowania przez RRLS; komunikat ma poziom ERROR, ale gra zachowuje ekran i
kontynuuje poprawnie. SteamDeckUtil pomija kontrolę rozszerzonego sterownika.
Nie są dowodem błędu progresji. We wcześniejszej próbie
serwera 26.3 wystąpił wyjątek Spark podczas inicjalizacji; nie powtórzył się
w końcowych testach z nowymi questami. Czasy startu przy równoległych testach
klienta są wyłącznie diagnostyczne.

## Oryginały i odtwarzanie

Poprzednie JAR-y i oba mrpacki 2.0.3 zachowano. Kopia stanu sprzed poprawek:
`.codex-backups/claude-2.0.3-before-review.zip`. Nowe źródła TEMPERED są w
`src/tempered/`; skrypty budowania pozostają w `tools/` i `journal-mod/`.
Strona w `dist/fancy-vanilla-site.zip` jest lokalnym artefaktem; nic nie opublikowano.

Finalne paczki zawierają TEMPERED 2.16.2 i Fancy Journal 1.0.3:

- `Fancy Vanilla 2.0.4.mrpack` (26.2), SHA512:
  `631807a2615420043f355052a3ee42c4be31b1093b2bf718245b22e2b16c1cbf6565bcf2d0767494f09e49ec4034915484e6301e4d92a6d94bfa0d1d009ddc17`
- `Fancy Vanilla 2.0.4 for 26.3.mrpack`, SHA512:
  `129fc512251466155b9ad412078a46e785e4de48f5969fd488409721ce70762969a08e5ff19925608665412e4542814d46d95af43e29e6a4b7fb332af3f94cd7`

---

# Historyczny przegląd Fancy Vanilla 2.0.3

Data: 2026-10-04. Aktualny kierunek wskazany przez użytkownika: **Fancy Vanilla**,
stary branding, zawartość vanilli, oprawa, rdzeń Streamline i autorski TEMPERED.
Przegląd nie zmienia tej decyzji ani nie dodaje zawartości Expedition.

## Co sprawdziłem

README, opis i changelog, build/resolver, aktualny `.mrpack`, jego sumę SHA512,
ustawienia domyślne, oryginalny branding, kod datapacka TEMPERED i zachowany log
serwera. Indeks 2.0.3 zgadza się liczbowo z lockiem; suma artefaktu jest poprawna.
To kontrola zawartości i kodu, nie test klienta ani pomiar FPS.

Artefakt zawiera **100 pobieranych modów + TEMPERED**, **26 pobieranych paczek
zasobów + własne menu** i 2 shadery. Liczba 23 paczek w README liczy tylko nowe
dodatki; warto to nazwać wprost. Oryginalne grafiki i marka są zachowane.

## Najpierw naprawić poprawność TEMPERED

Źródło: `src/mods/TEMPERED2.16.0mc26.2.jar` (SHA256
`7cc285f48453e5702ca32ae7875c0344202bb1a3bfcfc5e864aecc1fa8643a8b`).
Poniższe ścieżki odnoszą się do wnętrza JAR-a.

1. **Wymiar jest sprawdzany w kontekście funkcji, zamiast gracza.**
   `data/tempered/function/check/5.mcfunction:19` i `check/6.mcfunction:20`
   używają `as @a if dimension ...`. Funkcje wywoływane z głównego cyklu nie
   przenoszą kontekstu do Netheru/Endu wraz z graczem. Dodać `at @s` po `as @a`.
   Zweryfikować zaliczenie po wejściu przez oba portale, nie wyłącznie przez
   ręczne wywołanie funkcji z danego wymiaru.
2. **Historia blokady ekwipunku miesza wyniki graczy.**
   `data/tempered/function/core/locks.mcfunction:64` przypisuje wieloma źródłami
   `operation @a tempered.lock = @a tempered.lockn`. Zamienić na przypisanie
   osobne dla każdej osoby:
   `execute as @a run scoreboard players operation @s tempered.lock = @s tempered.lockn`.
   Sprawdzić dwie osoby, jedną z przyszłym ekwipunkiem i drugą bez blokady,
   oraz odłożenie przedmiotu. Problem dotyczy pamiętania stanu i komunikatów;
   sama bieżąca detekcja przedmiotu używa `lockn`.
3. **Niepełne pokrycie wyposażenia Minecraft 26.2.** Listy tierów i blokad receptur
   nie obejmują `minecraft:copper_*` ani vanilla włóczni. Potwierdziłem obecność
   miedzianej zbroi, narzędzi i włóczni w danych oficjalnego serwera 26.2.
   Dodać właściwe identyfikatory do świadomie wybranych er i sprawdzić zdobycie
   przedmiotu z łupu oraz crafting. Nie ustalać nowych progów er przy tej poprawce.

## Bezpieczne wyłączenie i opis progresji

Zachować autorską decyzję o domyślnych blokadach. Opisać jednak faktyczne działanie:

- Era i zadania są **wspólne dla świata**, także na serwerze. Nowa osoba dołącza
  do aktualnego etapu; nie zaczyna osobnej kampanii i nie otrzymuje dawnych XP.
- Nie trzeba wykonać 89 zadań. Progi wynoszą 6/9, 9/15, 8/13, 8/13, 9/14, 8/13,
  8/12; istnieje wybór. Śmierć i wielokilometrowy marsz nie są obowiązkowe.
- Widocznie pokazać `/trigger tempered.menu`. To instrukcja gry, której nowa
  osoba potrzebuje do zrozumienia ograniczeń.
- Usunięcie JAR-a **nie usuwa zapisanej gamerule** ani nie przywraca receptur.
  W istniejącym świecie po wyłączeniu moda wykonać jako administrator:
  `/gamerule minecraft:limited_crafting false` oraz `/recipe give @a *`.
  Na serwerze mod wyłącza administrator po stronie serwera, nie pojedynczy klient.
- `tempered:admin/gate_off` obecnie wyłącza tylko crafting. Debuffy ekwipunku
  zostają; restart lub `/reload` ponownie włącza crafting (`core/init:77`).
- „Blokada użycia sprzętu” to obecnie Mining Fatigue i Weakness. Nie odbiera
  ochrony pancerza, lotu elytrą ani wszystkich działań prawego przycisku. Opis
  powinien mówić dokładnie to, co implementacja zapewnia.
- Istniejący zaawansowany świat wymaga świadomego ustawienia ery albo wyłączenia
  TEMPERED. Samo zalecenie importu do dowolnego świata może zaskoczyć gracza.

Dodatkowy test administracyjny: `admin/reset` pomija `tempered.2m1`/`2m2` i działa
na obecnych graczach; uwzględnić powrót osoby nieobecnej podczas resetu.

## Konkretne poprawki oprawy i konfiguracji

1. **Particle Rain + agresywne odrzucanie cząsteczek.** W spakowanym
   `config/particle_core_config.toml` jest `cullingBehavior="AGGRESSIVE"`
   i pusta blacklist. Autor Particle Rain opisuje migotanie/znikanie efektów
   przy Particle Core i zaleca bounding box albo blacklistę. Wybrać obsługiwany
   enum w tej konkretnej wersji i sprawdzić deszcz ze shaderem oraz bez niego.
   [Dokumentacja autora Particle Rain](https://modrinth.com/mod/particle-rain).
2. **Dwa zoomy na C.** Chloride ma `[zoom].enabled=true`, a `options.txt` przypisuje
   C zarówno Chloride, jak i Zoomify. Zostawić jeden kontroler zoomu; proponuję
   Zoomify i wyłączenie zoomu Chloride.
3. **Clearer Slot Highlight jest nadpisany.** Build włącza go przed odziedziczonym
   Recolourful Containers DARK. Obie paczki zawierają różne sprite'y
   `slot_highlight_front.png` i `slot_highlight_back.png`; późniejsze DARK wygrywa.
   Ustawić świadomą kolejność, zgodną z obiecanym efektem.
4. Fast Better Grass i Simple Grass Flowers nakładają pięć blockstate'ów,
   m.in. `grass_block` i `podzol`. BetterGrassify też obsługuje wygląd boków trawy.
   To powód do ustalenia jednego właściciela efektu, nie dowód crasha. Natomiast
   Os' Grasses, Simple Grass Flowers, Bushier Bushes i Better Leaves nie mają
   wzajemnych kolizji ścieżek JSON i nie należy usuwać ich jako pozornych duplikatów.
5. Część efektów liści, bąbelków i plusków ma kilka dostawców. Wybrać właścicieli
   w konfiguracjach i porównać obraz. Fresh Animations → dodatki AL mają prawidłowy
   porządek; wspólne `emissive.properties` RAY/AL używają tego samego sufiksu `_e`.

## Wydajność i dowody testów

2.0.3 podnosi domyślne render/simulation distance z 8/5 w Streamline do **12/8**,
przy licznych efektach, modelach i paczkach. To świadomy koszt oprawy, nie dowód,
że będzie wolno. Potrzebne porównanie na tym samym sprzęcie, świecie i trasie.
Sensowne presety to oszczędny 8/5 i krajobrazowy 12/8, bez zmiany zawartości świata.

Zachowany `test-logs/server-run1_start-ok.log` pokazuje działający TEMPERED i 20 TPS
bez graczy, ale także wyjątek ładowania `GuiEventListener` podczas audytu ModernFix
oraz błąd monitora spark. W pliku nadal występuje usunięte później Elytra Trims,
więc nie jest to walidacja identycznego składu 2.0.3. Opcja
`mixin.perf.clear_mixin_classinfo=true` jest nadal dziedziczona; sprawdzić ją na
świeżym serwerze i rozważyć wyłączenie tylko tej optymalizacji po stronie serwera.

Przed oznaczeniem release: czysty start dokładnie 2.0.3, wejście klienta, nowy
świat i portale, dwie osoby z różnym wyposażeniem, ponowne dołączenie gracza,
deszcz/las/wioska ze shaderami i bez nich, pomiary frame time/FPS i MSPT.
Datę, seed, sprzęt, ustawienia i SHA testowanego artefaktu zapisać wraz z logiem.
Nie utożsamiać pustego serwera ze sprawdzoną płynnością ani liczby zadań z obietnicą
wielotygodniowej zabawy. Zachować progi TEMPERED; wydłużanie liczników GUI nie
tworzy nowych przygód.
