# Roadmap & Arkitektur: Stabssystem för 7S-Rapportering

## 1. Målbild & Designfilosofi
Systemet ska ge staben omedelbar, överskådlig och korrekt lägesinformation i realtid. Layouten på kartan ska vara så gott som identisk med OpenStreetMaps standardutseende. Syftet är att få in sekundsnabba 7S-rapporter från Signal-gruppen. Karta, punkter och tillhörande textrapporter är det enda som visas. Inga ljud, avancerade animationer eller bilagor (foton/filmer). Detta ska kunna rulla konstant på en stor TV-skärm.

Genom att skala bort all onödig komplexitet blir systemet mycket enklare att bygga, iterera på och felsöka.

### Koppling till PWA-rapportverktyget
Soldater fyller i rapporter via PWA-appen (`index.html`, `what.html`, m.fl.) och kopierar den genererade textsträngen till Signal-gruppen. Stab-systemet tar emot denna sträng och plottar den. Parsningslogiken i `main.py` **måste matcha exakt det format som PWA:n genererar** – inte en approximation. Se `FORMAT.md` för exakt specifikation.

PWA:n har även rapporttyperna WHAT, SCRIM, WEFT och AH. Stab-systemet **ignorerar dessa** och behandlar enbart 7S-rapporter (innehåller MGRS-koordinat). Icke-igenkända format loggas som rådata men plottas inte.

---

## 2. Arkitektur & Teknisk Stack

För att uppnå en snabb och stabil utvecklingscykel rekommenderas följande extremt förenklade arkitektur:

### A. Mottagarlager (Signal -> System)
Ansvarar enbart för att ta emot meddelanden och pusha dem vidare.
* **Mjukvara:** `signal-cli` (körs via Docker på Windows, t.ex. `balthazar/signal-cli-rest-api`). Det ger ett enkelt HTTP/REST-gränssnitt och Webhooks. Ingen bräcklig mus/tangentbords-automation behövs.

### B. Datalagring & Backend (Tolkning & API)
* **Språk/Framework:** Python med **FastAPI**. Snabbt att skriva, startar omedelbart och har inbyggt stöd för WebSockets.
* **Parsning:** Enkla Regex-regler för att utvinna 7S-fälten samt ett Python-bibliotek (`mgrs`) för att konvertera MGRS till Lat/Long. Sagesmanformatet (`NIN 111. 1a p, 2 grp. Nils Nilsson`) parsas automatiskt och används som label på kartpinsen.
* **Datalagring:** **SQLite** (inbyggd `sqlite3` i Python, ingen installation krävs). Ger persist vid omstart – kritiskt i fält. (Inga tunga PostgreSQL/PostGIS-installationer krävs).
* **Säkerhet:** Enkel API-nyckel eller HTTP Basic Auth via FastAPI. Lösenord konfigureras i en `.env`-fil. Systemet **exponeras aldrig mot internet** – enbart lokalt nätverk eller VPN.
* **Filosofi:** Backend kan även servera själva webbsidan (frontend) som en statisk fil, så man slipper starta flera servrar lokalt.

### C. Visningslager - Del 1: Infokartan (Webb-app)
* **Framework:** Ett enda `index.html`-dokument med Vanilla JavaScript (inga tunga byggsteg med React/Vue/Vite behövs).
* **Karta:** **Leaflet.js** med OpenStreetMaps standardkarta. Leaflet är extremt lättkodat, beprövat och snabbt att få upp.
* **Design & UI:** Grundläggande CSS (flexbox). En yta för kartan, och en sidopanel för listan med inkommande textrapporter. Bara pins och popup-text på raderna.
* **Mediastöd:** Helt bortvalt. Inga bilagor, filmer, animationer eller ljud. Bara robust rådata i textform.

### D. Visningslager - Del 2: Auto-utskrift (Windows)
* **Förenklat flöde:** En separat `print.html`-vy serveras av backenden. Den visar enbart rapportlistan i utskriftsvänligt format. Utskrift triggas via webbläsarens inbyggda `window.print()` + CSS `@media print`. Undviker PDF-konvertering och Print Spooler-komplexitet.
* Om automatisk utskrift ändå krävs: ett enkelt Python-skript lyssnar på WebSocket och skickar rapporttexten direkt till skrivaren via `win32print`.

---

## 3. Förslag för enklare kodning, iteration & felsökning

När ambitionerna skalas ner (inga animationer eller mediabuffring) blir systemet mycket mer tillförlitligt och smidigt att skriva:

1. **Monolithic Project:** Ha backend, statisk HTML (frontend) och utskriftsskript i samma projektmapp. Starta webbsidan och backenden med ett enda Python-kommando. Oerhört lätt att administrera och felsöka jämfört med utspridda mikrotjänster.
2. **"Dumb Frontend" (Stateless):** Låt webbplatsen vara helt utan internt tillstånd. När backend skickar en WebSocket-uppdatering om en ny/ändrad rapport – rensa Leaflet-kartan och rita om alla markörer från början. Det utraderar nästan alla potentiella UI-buggar.
3. **Mocking-verktyg:** Bygg tidigt in en `mock_sender.py` eller en testknapp i webbgränssnittet. Då kan du snabbt spamma in påhittade 7S-testrapporter till backenden lokalt, utan att behöva sitta med telefonen och skicka Signal-meddelanden varje gång du ska testa din kod. **OBS:** `mock_sender.py` ska generera exakt samma textsträng som PWA:ns kopieringsfunktion – se `FORMAT.md`.
4. **Logga Rådata:** Printa alltid den obehandlade Signal-JSON-strängen till en textfil (`raw_signals.log`). Kraschar din backend på ett oväntat meddelande från Signal har du en exakt kopia som du kan köra ett py-test emot i efterhand!

---

## 4. Förenklad Roadmap

### Fas 1: Grundsystem (Mottagning & Backend)
* [ ] Skapa `FORMAT.md` som dokumenterar exakt vilken textsträng PWA:n genererar för en 7S-rapport. Används som referens för parsning och mock-data.
* [ ] Sätt upp `signal-cli-rest-api` mot stabs-telefonnumret via Docker.
* [ ] Skriv en `mock_sender.py` som skickar lokala testrapporter (i exakt PWA-format) så kodningen snabbas upp.
* [ ] Utveckla FastAPI-filen (`main.py`). Skapa en `/webhook`-endpoint som fångar Signal-meddelanden.
* [ ] Lägg till `/health`-endpoint som returnerar serverstatus. Används av TV-klienten för att varna om backenden är nere.
* [ ] Bygg logik för text-parsning (7S -> JSON) och lat/long-konvertering (MGRS -> dec). Extrahera sagesmanfältet för pin-label.
* [ ] Spara tolkade meddelanden i **SQLite** (persist vid omstart).
* [ ] Skapa `run_system.bat` som startar Signal-Docker och FastAPI med ett dubbelklick.

### Fas 2: Kartmotor & Statisk Webb (Infokarta)
* [ ] Skapa `index.html` som returneras via ex. `http://localhost:8000/`.
* [ ] Lägg in Leaflet.js och OpenStreetMaps standard-tile-lager.
* [ ] Dra in och plotta rapporterna (i frontend-JS) som standard-markers via en fetch på en REST-endpoint (`/api/reports`).

### Fas 3: Sekundsnabb Realtid (WebSockets)
* [ ] Lägg till WebSocket-endpoint till FastAPI:n och koppla an Javascriptet i `index.html`.
* [ ] När backend fångar ett Signal-meddelande → skicka via WebSocket.
* [ ] Javascript tar emot paketet on-the-fly, uppdaterar sidebar-listan med den rena texten och sätter direkt en pin på OpenStreetMap. Pin-label sätts från sagesmanfältet.
* [ ] Implementera auto-reconnect i frontend-JS (exponential backoff). Klienten ska återansluta automatiskt om servern startas om.

### Fas 4: Smidig Ändring & Auto-utskrift
* [ ] Redigering i Signal: Signal pushar en uppdatering. Backend uppdaterar befintligt meddelande i sin logg och skickar en full uppdatering via WebSocket. Frontend ritar om skärmen.
* [ ] Skriv `print_service.py` som i bakgrunden står anslutet till WebSockets, och efter en buffertfönster på 60 sek renderar HTML-layout -> Print Spooler.

### Fas 5: Systemtest (I fält)
* [ ] Fullskärmskörning på TV:n: Se över storlek på text (font-size i CSS) så att den är massiv och lättläst från andra sidan stabsborden.
* [ ] Skapa en `run_system.bat` fil för Windows. Ett dubbelklick startar Signal-Docker, server och ev. print-tjänst automagiskt för en befälselev med andan i halsen.
