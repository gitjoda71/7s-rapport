# Roadmap: Utbyggnad av Rapportsviten (Sju Nya Formulär)

Denna roadmap innehåller detaljerade specifikationer och utvecklingsplaner för sju nya fältformulär (PWA) för Hemvärnet: OBSLÖSA, FORS, PEDARS, POSTSCHEMA, EOBUSARE, OBO och RASSOIKA. Samtliga bygger på befintlig kodbas (HTML/CSS/JS, PWA, Dark Mode).

---

# 1. OBSLÖSA – Postinstruktion (`obslosa.html`)

## 1. SYFTE OCH ANVÄNDNINGSFALL
**Syfte:** Snabb minnesramsa för utställande av en bevakningspost.
**Användare:** Grupp- och plutonschefer (primärt) samt vaktposter (mottagare).
**Scenario:** En plutonchef har beordrat postering vid en vägkorsning. Gruppchefen fyller snabbt i OBSLÖSA-appen, exporterar till utskrift/kopiering, läser upp för posten och lämnar utskriften vid eldställningen så att avlösande posteringar kan repetera ordergrunder.

## 2. FÄLTSPECIFIKATION
Alla standardfält (Sagesman, Stund, Plats) är obligatoriska.
*   **Orientering (O):**
    *   Terrängen (textarea, obligatorisk)
    *   Fienden (textarea, obligatorisk)
    *   Egna förband (textarea, obligatorisk)
    *   Civilbefolkningen (textarea, valfritt)
*   **Bevakningsområde (B):**
    *   Vad ska bevakas (textarea, obligatorisk)
    *   Gräns vänster / höger (text, obligatorisk)
    *   Särskilda observationspunkter (textarea, valfritt)
*   **Sätt att tillkalla chef (S):**
    *   Signal/procedur (textarea, obligatorisk) Hjälp: "Ex: Snabb ryck i signallina."
*   **Lösen (L):**
    *   Ord 1 / Ord 2 (text, valfritt) Hjälp: "Ex: SKO / LÅDA"
*   **Öppna eld (Ö):**
    *   Omständigheter (textarea, obligatorisk)
*   **Ställning och utrustning (S):**
    *   Uppträdande (textarea, obligatorisk)
    *   Extra materiel (textarea, valfritt)
*   **Avlösning (A):**
    *   När/Hur (textarea, obligatorisk)

## 3. EXPORTFORMAT
Exporten maximerar läsbarhet i fält (stora typsnitt).
```text
POSTINSTRUKTION (OBSLÖSA)
Sagesman: JOH 1. 2a p, 1a grp. Johan Johansson
Stund: 2026-03-23 15:30
Plats: 33V UE 12345 67890

= O =
TERRÄNG: Öppen vägkorsning i söderläge.
FIENDE: Små sabotageförband väntas från sydväst.
EGNA: 2.a grupp ligger 300m nordost.
CIVIL: Sparsam civil trafik.

= B =
BEVAKA: Vägkorsning och skogsbryn i SO.
GRÄNS: V: Rött hus. H: Träddungen.
...
```

## 4. UX-ÖVERVÄGANDEN
- **Utskriftsvänlig vy:** Exportknappen måste gömma onödigt UI (knappar, dark mode styling om skrivare används).
- **Läsbarhetsläge:** En knapp "Muntlig order" som gör all inmatad text gigantisk (40px) i mörkerläge för enkel uppläsning för posten under natten.

## 5. AVVIKELSER FRÅN STANDARDMALLEN
Inga större avvikelser förutom tillägget av ett uttalat skriftligt "Read Mode". Sagesman och Plats passar perfekt in här.

## 6. BYGGORDNING / FASPLAN
1. Klona `7s.html` till `obslosa.html` och rensa kroppsinnehåll.
2. Bygg strukturen för varje bokstav med tydliga rubriker och <fieldset>.
3. Implementera "Muntlig order"-vy i CSS (`@media print` och CSS-klass för stor text).
4. Koppla App.js (LocalStorage och Export).

## 7. REGLEMENTSENLIGA OCH INTERNATIONELLA REKOMMENDATIONER
a) **Svensk doktrin:** Följer HvH och Servicereglemente Tvärallmän (Postinstruktion). OBSLÖSA är standardiserat.
b) **NATO-standard:** Guard Orders (General/Special Orders). Motsvarar "Special Orders for a Sentry".
c) **Modern UX:** Offline-first är kritiskt då poster måste få med sig en digital eller utskriven kopia. En QR-kodgenerering vid export (där posten kan scanna med sin egen enhet för att hämta ner texten lokalt) vore mycket avlastande!
d) **Tillägg:** Fält för "Utalarmeringsruta" - rutt för postens eget tillbakadragande (Fallback plan).

## 8. TEKNISKA FALLGROPAR
Att få webbsidor att skrivas ut snyggt ifrån mobila enheter ifält (mobil -> fältskrivare via BT). Media queries för `print` måste rensa ut alla skuggor, svarta bakgrunder (dark mode) och borders för att inte slösa bläck.

---

# 2. FORS – Lägesrapport (`fors.html`)

## 1. SYFTE OCH ANVÄNDNINGSFALL
**Syfte:** Effektiv lägesrapport under strid/verksamhet.
**Användare:** Grupp/pluton (rapporterar till Kompani) eller Kompani (till Bataljon).
**Scenario:** En pluton har nedkämpat ett Ivan-näst, chefen sliter upp telefonen mitt i eldupphöret, väljer "Kompani", knappar in vad fienden gjort (O), vad man själva utfört och ska göra näst (R) och sänder iväg över radio (exportvy).

## 2. FÄLTSPECIFIKATION
*   **Huvuddata:**
    *   Nivå (select: Kompani/Bataljon)
    *   TNR (text, valfritt)
*   **F – Förbandets position:**
    *   Position (textarea). UI-larm: "Ange bara om krypterat samband!" (Röd alert-box).
*   **O – Om motståndaren:**
    *   Situation (textarea, obligatorisk)
*   **R – Redogörelse för VHT:**
    *   Genomförd (textarea) / Pågående (textarea) / Planerad (textarea) (Alla obligatoriska)
*   **S – Slutsatser:**
    *   Dragna slutsatser (textarea, valfritt)

## 3. EXPORTFORMAT
Formatet minimeras för radiopassning.
```text
FORS TNR: 014
FRÅN: JOA 3. 2a p.
F: (Se MGRS på eget system)
O: Fienden omgrupperar söderut efter förlust av två strf.
R: 
- Genomfört eldöverfall. 
- Omhändertar skadade just nu. 
- Fortsätter framryckning om 10 min.
S: Fiendens vänstra flank är oskyddad.
Kom!
```

## 4. UX-ÖVERVÄGANDEN
- **Extreme Speed:** Måste vara fältets snabbaste formulär att fylla i. Röst-till-text API (om PWA tillåter) förtextarea-fälten kan vara ovärderligt under strid.
- **Röd varning för P-Klartext:** Plats är en livsfara över öppen radio under stridskontakt. Röd, blippande varning föreslås om platsfältet är ifyllt och användaren inte checkat i "Kryptosamband".

## 5. AVVIKELSER FRÅN STANDARDMALLEN
Sagesman och Plats används, men Plats ska ha en "Dölj vid export"-toggle beroende på sambandstyp (klartext vs krypto).

## 6. BYGGORDNING / FASPLAN
1. Upprätta HTML med stora, lätt-tappade fält.
2. Bygg varningssystem (Javascript event listener) som detekterar text i "Plats"-fält och varnar.
3. Utveckla export-funktionen som skapar en tajt radio-text.
4. Lägg till select-boxen för Komp/Bat och låt fältens labels dynamiskt anpassas.

## 7. REGLEMENTSENLIGA OCH INTERNATIONELLA REKOMMENDATIONER
a) **Svensk doktrin:** FORS är Försvarsmaktens de-facto lägesrapport vid strid, beskriven i Handbok Markstrid.
b) **NATO-standard:** SITREP (Situation Report) STANAG 2020. NATO SITREP är enorm, FORS motsvarar mer "Contact Report" / "Spot Report".
c) **Modern UX:** "Speech-to-text" under strid (stress). Kognitiv belastning innebär att fritext är svårt under beskjutning; erbjuda select-menyer för typiska situationer ("Understöd behövs," "Fortsätter enligt order," "Utgår från strid") under 'R'.
d) **Tillägg:** Fält för BDA (Battle Damage Assessment). Vad vi förstört de facto (Svensk 'O' täcker det ofta slarvigt).

## 8. TEKNISKA FALLGROPAR
Att tvinga PWA Speech-to-text API:et i en offline-miljö. Ofta krävs webbanlutning för röstanalys vilket bryter "offline first". Bättre att förlita sig på robusta och stora tangentbordsytor i mobilen.

---

# 3. PEDARS – Underhållsrapport (`pedars.html`)

## 1. SYFTE OCH ANVÄNDNINGSFALL
**Syfte:** Rutinmässig underhållsrapport till Kvartermästaren.
**Användare:** Plutonens/kompaniets Stf chef.
**Scenario:** Varje kväll kl 20:00 inventerar Stf PlutC tillgänglig pers, ammo, skador, chassidelar och bränsle för att skicka KvM en PEDARS inför morgondagens "pusher-logistik". 

## 2. FÄLTSPECIFIKATION
*   **P – Personal:** Total (number), Dynamisk lista (namn + select: Permission/Sjuk/Skadad/Död/Saknad)
*   **E – Ersättning utrustning:** Behov (textarea).
*   **D – Drivmedel:** Dynamisk tabell (Fordonstyp | Regnr | %-nivå `type="number"`)
*   **A – Ammunition:** Tabell för inskrivning (7.62 / 9mm / 8.4 / Granater ... + Fritext för Annat)
*   **R – Reparationer:** Dynamisk tabell (Fordon/Reg / Rep-behov / Körbar? Select)
*   **S – Stridsvärde:** Select (Fullt / Reducerat / Kraftigt Red. / Icke Stridsduglig) + Motivering (textarea).

## 3. EXPORTFORMAT
Här måste exporten vara skapad som en snygg lista (JSON-lik).
```text
PEDARS - 2a Plut
Sagesman: AND 2. 2a p. Stf C
Stund: 2026-03-23 20:00

P: 34 Pers tjänstbara. 
 - Johan Svensson (Sjuk)
 - Karl Karlsson (Skadad)
E: 10st knäskydd, 1st Bårbälte.
D: 
 - Pb 8 (11245): 40%
 - Sprinter (22119): 90%
A: 
 - 7.62: 4000
 - P-skott: 4
R: 
 - Pb 8 (11245): Punktering vä fram, Körbar: Begränsad
S: Reducerat. (Avsaknad av vagnchef gör vagn 1 stillastående).
```

## 4. UX-ÖVERVÄGANDEN
- **Matrix-inmatning för Ammo:** Numeriska "steppers" (+ / - knappar med stora träffytor) istället för att användaren ska behöva klicka in sig på mobila tangentbordet för t.ex. P-skott.
- **Dynamiska tabeller i mobilläge:** Standardtabeller är horribla i mobil. Skapa "kort" för varje fordon istället där användaren klickar "Lägg till fordon" och ett nytt flex-kort läggs till.

## 5. AVVIKELSER FRÅN STANDARDMALLEN
Plats är ofta sekundärt för PEDARS då KvM redan vet plutonens positionering (eller så anges det formellt via FORS). Plats-fältet kan dock vara kvar för t.ex UPA (Upphämtningsplats).

## 6. BYGGORDNING / FASPLAN
1. Skapa "Lägg till"-logiken i JS för Pers, Drivmedel och Reparation.
2. Designa flex-kort för Ammo med inkrement-knappar (Javascript `stepUp/stepDown`).
3. Sido-lagring (LocalStorage) är kritiskt här då man fyller i denna över flera timmar i fält.
4. JSON Export (som backup) vid sidan av text, för KvM att importera till Excel.

## 7. REGLEMENTSENLIGA OCH INTERNATIONELLA REKOMMENDATIONER
a) **Svensk doktrin:** Följer Logistikreglemente (LogR), klassisk och heltäckande för Hemvärn/Lätta skyttebataljoner.
b) **NATO-standard:** LOGREP (Logistics Report) STANAG 2045. Mycket mer detaljerad (DOAC - Days Of Ammunition Cargo etc). Er PEDARS är en utmärkt, lättviktig NATO-anpassad motsvarighet, mycket lik USAs "9-Line LOGSTAT".
c) **Modern UX:** Bevara inmatat data oändligt! Om en pluton har 3 fordon ska användaren slippa skriva in Regnr varje kväll. LocalStorage MÅSTE spara fordonsparken mellan inloggningarna så man bara ändrar procenten!
d) **Tillägg:** Fält för Vatten & Mat (DOS - Days of Supply kvar - t.ex. Vatten: 24h, Stridsportion: 48h). Oerhört kritiskt för staben.

## 8. TEKNISKA FALLGROPAR
Att få dynamiska "kort" att bygga in sig korrekt i LocalStore och Exportsträngen utan buggiga loopar. Använd Array of Objects för state.

---

# 4. POSTSCHEMA – Vaktschema (`postschema.html`)

## 1. SYFTE OCH ANVÄNDNINGSFALL
**Syfte:** Automatiserad generation av post/vaktschema (plutons inre tjänst).
**Användare:** Stf Grupp/PlutChef, Dagbefäl.
**Scenario:** Under förläggning drar Stf i igång appen kl 19:00. Han ska ha 2 gubbar på post, 2-timmars pass, under 12 timmar, bland 14 friska gubbar. Algoritmen rullar ut vem som går när på två klick.

## 2. FÄLTSPECIFIKATION
*   **Steg 1 (Settings):**
    *   Enhet (text)
    *   Starttid (datetime-local)
    *   Skiftlängd (number, default: 2)
    *   Antal poster per skift (number, "Lägg till utpekad post")
    *   Timmar (number, total duration)
    *   Soldatlista (dynamisk lista, tryck "Lägg till")
*   **Steg 2 (Schema):**
    *   Ett HTML-grid/Table (Tid | Post | Namn) med möjlighet att "klicka" en cell och byta namn (dropdown).

## 3. EXPORTFORMAT
Ren text-tabell (monospaced om möjligt):
```text
VAKTSCHEMA (2a Plut) - 2026-03-23
Start: 20:00

TID         | POST 1 (Grindar) | POST 2 (Slitset)
20:00-22:00 | Andersson        | Kalle Berglund
22:00-00:00 | Johan S          | Erik E
00:00-02:00 | David O          | Mikael P
02:00-04:00 | Per B            | Kalle Berglund (2a)
...
```

## 4. UX-ÖVERVÄGANDEN
- Algoritmen bör rotera listan rättvist (Queue Array Shift/Push).
- Gränssnittet MÅSTE låta användaren "swappa" två personer manuellt ifall algoritmen dömde en maskinskytt till eldpost direkt efter vaktpass. 
- Visuell Drag-and-Drop (DOM Sortable) är drömmen, men en "Click to Replace" rullgardin räcker utmärkt för mobiler.

## 5. AVVIKELSER FRÅN STANDARDMALLEN
Sagesman är "Schemaansvarig". Plats, och Rapport-stund utgår (ersätts av Start-stund för schemat).

## 6. BYGGORDNING / FASPLAN
1. Bygg State Manager i JS för `soldiers = []`, `shifts = []`.
2. Skapa genereringsalgoritmen (fördela arrayer över tids-slots).
3. Rendera tabellen. Utveckla "Edit Mode" där ett klick öppnar en modal för att swappa ett namn.
4. Generera tabell i monospace string format.

## 7. REGLEMENTSENLIGA OCH INTERNATIONELLA REKOMMENDATIONER
a) **Svensk doktrin:** Följer Inre Tjänst och reglementet för Vakttjänst. Scheman skrivs annars på whiteboard eller Rite-in-the-Rain-block.
b) **NATO-standard:** Rostering sker lokalt på kompaninivå, ofta i små Excel-ark (Watchbill). 
c) **Modern UX:** Visualisera vilotiden! Appen bör ha en liten alert: "Observera: Soldat X får under 4h kontinuerlig sömn". Detta minskar fatala ledarskapsfadäser till fält.
d) **Tillägg:** Eldpost / Kaminvakt parallellt med yttre bevakning i samma schemaalgoritm.

## 8. TEKNISKA FALLGROPAR
Att bygga en perfekt skift-algoritm i JS (`while loop` baserad på modulus över en array soldater). Fel i logiken ger oändliga loopar i webbläsaren. Tabeller i SMS kraschar, monospacing måste bibehållas (ex. `padStart(15)`).

---

# 5. EOBUSARE – Eldställningsrutin (`eobusare.html`)

## 1. SYFTE OCH ANVÄNDNINGSFALL
**Syfte:** Understöds/trygghetsskapande checklista vid förflyttning av eld.
**Användare:** Gruppchef/Omgångschef under stress.
**Scenario:** Truppen trycker ner i skydd. Chefen slår upp EOBUSARE på handleden/mobilen och börjar pricka av: "Eldställning har vi... O är Kalle... B är vägen... U är ladan där (klick klick)". Det tvingar chefen ur tunnel-seende.

## 2. FÄLTSPECIFIKATION
Stegvist kort (Wizard/Accordion format).
*   **E** - Checkbox & Plats (text)
*   **O** - Namn & Position (text)
*   **B** - Gränser (textarea)
*   **U** - Dynamisk UPK-lista (Namn, Riktning, Avstånd)
*   **S** - Checkbox & Kanal (text)
*   **A** - Dynamisk ammolista (% kvar) & Skadade (nummer)
*   **R** - Checkbox & Vem (text)
*   **E** - Planerade förbättringar (textarea)

## 3. EXPORTFORMAT
Statuskvitto:
```text
STATUS: EOBUSARE INTALAR
Sagesman: PET 4. 1a p, 1a grp C

Position: Skuggsidan kullen.
Observatör: Kalle (Trädet V)
U: 1. Vita Ladan (N, 400m). 2. Bro-fästet (NO, 300m).
Radio: Rakel tg 4 KLAR
Ammo: 50%. Skadade: 0.
Rapport avgiven till PlutC: JA.
```

## 4. UX-ÖVERVÄGANDEN
- Kritiskt: Detta är en ACTION checklist. Den MÅSTE opereras snabbt. Gigantiska checkboxar som fyller mobilen ("Cards" som sveps). Haptisk feedback (Vibration `navigator.vibrate(50)`) när ett kort klaras av. Progress bar i toppen ("E - O - B - U - S - A - R - E") som fylls i grönt.

## 5. AVVIKELSER FRÅN STANDARDMALLEN
Mindre inmatning, mycket mer statusövervakning. En dedikerad "Resett/Börja Om"-knapp för nästa omgruppering måste finnas tydligt tillgänglig.

## 6. BYGGORDNING / FASPLAN
1. Designa "Stepper"-komponenten i CSS/JS.
2. Bygg datainput för de 8 stegen.
3. Koda "Auto-Scroll" - när användaren checkar i sista grejen på [E], scrolla mjukt direkt ner till [O].
4. Exportera summary.

## 7. REGLEMENTSENLIGA OCH INTERNATIONELLA REKOMMENDATIONER
a) **Svensk doktrin:** Grundfundament i SoldF / GruppC Utbildning. Exakt enligt bok.
b) **NATO-standard:** Delvis motsvarande "Establish a blocking position". TLP processer täcker detta, men svenska EOBUSARE är unikt genialisk i fält som minnesramsa.
c) **Modern UX:** "One-handed operation". När chefen kryper är en hand upptagen med vapen. Alla element måste kunna nås med en tumme.
d) **Tillägg:** Integrera genast en "Kompass / Riktning" funktion. Istället för skriva Riktning på UPK, låt användaren trycka på "Plocka kompassriktning" som läser telefonens accelerometer/kompass (DeviceOrientation API)!

## 8. TEKNISKA FALLGROPAR
Att få webbläsarens formulär att bete sig som en native "Swipe" applikation utan att behöva bygga in enorma externa bibliotek. Använd Vanilla JS IntersectionOberserver och CSS `scroll-snap-type`.

---

# 6. OBO – Ordergivning (`obo.html`)

## 1. SYFTE OCH ANVÄNDNINGSFALL
**Syfte:** Snabb strids/framrycknings-order från en stridande chef till gruppen.
**Användare:** Gruppchef / Stf (direkt mot enhetsmedlemmar).
**Scenario:** Skyttet tar paus bakom en ås. Chefen vill planera närmaste anfall och snabbt lägga fram en 5-punktsorder. Hon fyller i det absolut mest väsentliga: "Vem, Hur, Vad", läser högt från mobilen, exporterar och sänder till berörda omgångschefer innan de sprider ut sig.

## 2. FÄLTSPECIFIKATION
**Auto-Import / AI-Tolk (Högst upp i formuläret):**
Ett textfält ("Klistra in order") och en uppladdningsknapp ("Ladda upp PDF") där gruppchefen kan ta en 5-punktsorder (PUK) från Plutonchefen. Ett bakomliggande skript (eventuellt kopplat till ett lättviktigt extraherings-API eller regex-logik) läser ordern, extraherar relevant data och auto-fyller OBO-fälten nedan. Chefen reviewar sedan bara rutorna innan den egna ordern genereras.

Format (OBO / OBK i select).
*   **O (Orientering):** Fi, Egna,, Terräng, Civil (valfritt vid export). **Vår Uppgift:** (Oblig).
*   **B (Beslut/Hur):** Målbild, GFI (Inledning, Därefter, Slut), RIL (textarea).
*   **O/K (Order/Kommando):** Dynamisk lista med ordertagare (vem -> gör vad -> beredd).
*   **Uthållighet/Ledning:** Sjukvard, UH, Plats, Stf, Samband.

## 3. EXPORTFORMAT
Målet är ett talspråks-vänligt manus:
```text
ORDER (OBO)

ORIENTERING
Fi: 2 fordon passerat vägen, nu i ro.
Egna: 3e plut täcker vår högra flank.
VÅR UPPGIFT: Ta kontroll över ladan och spärra in/utpassering.

BESLUT
Målbild: Vi är i postition i och runt ladan om 10 min.
Inledningsvis: Rör oss i skydd av dunge.
Därefter: Omgång 1 understödjer Omg 2 över öppen terräng.
Slutligen: Besätter objektet och inväntar PlutC.

ORDER
Kalle (1a omg): Understöd, beredd rök!
Johan (2a omg): Spjutspets och inbrytning, beredd spräng!

SJUKVÅRD: Plats för sårade: Dungen där vi står nu.
JAG LEDER FRÅN: Omg 2.

Slut! Frågor? Framåt!
```

## 4. UX-ÖVERVÄGANDEN
- **Fältkompakthet:** Många fält, de som är irrelevanta just nu (t.ex Civil i ett helt övergivet område) måste vika undan (collapse). Om användaren lämnar tomt ska det 100% försvinna från vy.
- **Preview-ruta:** En "Läs upp"-knapp i botten fäller ut the final output i fullskärm över allt annat, låser skärmen (screen wake-lock) och möjliggör uppläsning för soldaterna.

## 5. AVVIKELSER FRÅN STANDARDMALLEN
Inga. Mycket central för hemvärnets ledningsrytm.

## 6. BYGGORDNING / FASPLAN
1. Hårdkoda strukturen för Orientering och Beslut med HTML.
2. Bygg den dynamiska ordertagar-listan i JS (Input: Role, Task, Prepared-for).
3. Skapa logiken `if(field.value == "") { excludefromExport }`.
4. Lägg in knappen "Läs Upp (WakeLock)".

## 7. REGLEMENTSENLIGA OCH INTERNATIONELLA REKOMMENDATIONER
a) **Svensk doktrin:** OBO (Orientering, Beslut, Order) är en komprimerad variant av formell PUK/5-punktsorder, rekommenderad nedåt Grupp. 
b) **NATO-standard:** SMEAC (Situation, Mission, Execution, Administration/Logistics, Command/Signal) motsvarar ganska väl OBO-strukturen. NATO "Frag Order" (Fragmentary Order) liknar detta.
c) **Modern UX:** Långa textarea-formulär suger på mobil. Tillåt en "Bullet point"-knapp som formaterar input auto-magiskt till listor under "Beslut".
d) **Tillägg:** Inbyggd timer / "Time Hack". "Klockan är nu... vi framrycker om XYZ minuter." Sätt på en countdown via appen som synkar upp alla ifall larm/ljud ska agera GO-signal.

## 8. TEKNISKA FALLGROPAR
Att bibehålla en clean "Read View". Skärmar släcks automatiskt på Mobiler via native OS settings. För OBO och RASSOIKA borde PWA implementations använda `navigator.wakeLock.request('screen')` så skärmen inte slocknar mitt i chefens ordergivning.

---

# 7. RASSOIKA – Patrullchef före utgående (`rassoika.html`)

## 1. SYFTE OCH ANVÄNDNINGSFALL
**Syfte:** Komplett pre-flight minnesramsa innan en patrull skickas ut från egen linje/bas. Dödsallvarlig kontroll.
**Användare:** Patrullchef.
**Scenario:** Patrullen är samlad i basen, sista 10 minuterna. Patrullchefen öppnar rassoika.html och trycker grön bock steg för steg. Hon ber patrullen kontrollhoppa (Skramlar!). Blipp, notering. Visar lösen på kartan. Blipp. Exporterar Statuskvitto till Plutonschefen i tältet brevid: "Vi utgår 22:15, 6 pers, O. är stf".

## 2. FÄLTSPECIFIKATION
Åtta vertikala "Kort / Dragspel" (R, A, S, S, O, I, K, A).
(Se punkt specifikation för dynamiska listmenyer och checkboxar i systemprompten, exakt följsam).

## 3. EXPORTFORMAT
Genererar två utdata som kan togglas:
**1. UPPSTYRD PATRULLORDER (För läsning)**
Textmassan från [O], formaterad med Stor Text.
**2. STATUSKVITTO (För radio/samband/logg)**
```text
KVITTO: PATRULL UTGÅENDE
TID: 2026-03-23 22:15
C: JOA (Alpha 1)
STF: Kalle
Spjut: Johan, Radioman: Sara.
Styrka: 6.
R-A-S-S-O-I-K bekräftade klara.
Anmält PlutC per Radio.
```

## 4. UX-ÖVERVÄGANDEN
- **Checklist-First:** Inte ett formulär, utan en att-göra-lista. Allt som inte är aktivt / färdigbockat är grafiskt gräddat eller "dimmat" tills man öppnar kortet. 
- **Linjär låsning (valfritt):** Du förväntas inte klara "O" (Orientering) innan "S" (Stridsberedskap / Ammunition) är uthämtad. Låt nästa sektion highlightas när aktuell sektion är 100% ibockad.

## 5. AVVIKELSER FRÅN STANDARDMALLEN
Mycket mer komplicerad State Logic. Både textfält, radioknappar och 15+ boolean checkboxar i en array.

## 6. BYGGORDNING / FASPLAN
1. Hårdkoda en `<details>` och `<summary>` (accordion) struktur för de 8 delarna.
2. Infoga all checkbox-logik och dynamiska array-skapare ('Lägg till patrullmedlem').
3. Koda State-checken: När `inputs.length == checkedInputs.length` på ett section-id, aktivera en grön `.done` CSS-klassering.
4. Generera dubbel utmatning (Statuskvitto vs Manus).

## 7. REGLEMENTSENLIGA OCH INTERNATIONELLA REKOMMENDATIONER
a) **Svensk doktrin:** Strikt svensk standard ur Handbok Markstrid / Patrullorder-ramsor. Mycket av svensk soldatutbildning vilar på denna exakta akronym.
b) **NATO-standard:** WARNORD / Patrol Orders + TLP process. Målet är extrem detaljrikedom för patruller bakom linjen. Den svenska ramsan är mycket elegant jämfört med NATOs stora Word-dokument.
c) **Modern UX:** Undvik Scroll-Fatigue! Sätt en fixerad sidoflik eller top-bar med "RASSOIKA"-bokstäverna där man kan trycka för att hoppa direkt (Nav-Anchors). Skärmen är mörk för nattvision; använd RÖD eller BÄRNSTEN (Amber) highlight för aktiv flik, inte bländande vitt, så patrullchefen ej natt-bländas innan uppdrag.
d) **Tillägg:** "Abort/Återsamlingsplan"-fält under [O] (t.ex GOTWA-ramsan för NATO). Stridsvärdesbedömningsverktyg eller en "Traffic Light" (R/Y/G) check innan utpassering. "Verktyg röjda för IFF/laser?"

## 8. TEKNISKA FALLGROPAR
Att binda fast state i checkboxar om appen uppdateras i bakgrunden. En reload får INTE nollställa ett halvfyllt rassoika-formulär! Detta kräver "Throttle" och robust JSON-sparning av varje individuellt Boolean-state ("isAmmoChecked: true, isRadioChecked: false") till `LocalStorage` löpande (debounce 1 sek). WakeLock-API krävs igen för uppläsningen.

---

# ÅTGÄRDSPLAN FÖR FEEDBACK OCH ANVÄNDARTESTNING (BETA)

Ett av de absolut mest effektiva sätten att iterera fram militära verktyg som faktiskt fungerar i skogen är en tät feedbackloop med riktiga användare (Hemvärnsmän ute på övning). Eftersom hela projektet vilar på en modern AI-kodarassistent (Google Antigravity) kan testcykeln från "rapporterad bugg i fält" till "lagad och utrullad funktion" kortas ner från månader till minuter.

Eftersom du redan hostar filerna på **GitHub Pages** (`gitjoda71.github.io/faltrapport`), har du redan tillgång till branschens bästa, inbyggda feedbacksystem: **GitHub Issues**.

## Så här sätter vi upp feedback-loopens ekosystem:

### 1. Inbyggd Feedback-knapp i PWA:n
I varje app (t.ex. under en "Inställningar/Om"-flik eller längst ner i sidfoten) placerar vi en diskret länk:
*`"Hittat en bugg eller saknar en funktion? [Lämna feedback här]"`*

Denna länk pekar direkt mot ditt repos `Issues`-sida. För att göra det idiot-säkert för trötta soldater använder vi inbyggda URL-parametrar för att "för-fylla" deras buggrapport.

Exempel på hur länkadressen konstrueras:
```
https://github.com/gitjoda71/faltrapport/issues/new?title=[Beta-Feedback]%20&body=**Formulär:**%20(T.ex.%20OBSLÖSA)%0A**Beskriv%20problemet/förslaget:**%0A%0A**Vilken%20telefon%20använder%20du?**
```
När soldaten klickar på knappen öppnas GitHub (de kan logga in eller skapa ett snabbt gratiskonto) och mallen ligger reda där. De skriver *“Röda knappen i EOBUSARE syns inte på min Samsung när Dark Mode är på”* och trycker Submit.

### 2. Tolkning & Integration via Google Antigravity
När du sätter dig vid datorn öppnar du bara GitHub Issues och ser vad dina testare har skickat in under helgen. Istället för att du själv kodar in lösningen använder du **Antigravity**.

**Rutin för dig:**
1. Kopiera texten från en GitHub Issue, eller dela länken med Antigravity.
2. Skriv en kort prompt: *"Kolla Issue #12 från testarna: 'Röda knappen i EOBUSARE syns inte på Samsung i Dark Mode'. Kan du fixa CSS-filen för detta?"*
3. **Antigravity** förstår omedelbart kontexten, analyserar din befintliga `style.css` eller `eobusare.html`, och presenterar en konkret kodändring.
4. Du verifierar och "godkänner" Antigravitys förslag (ett klick).
5. Antigravity trycker ändringen och problemet är löst på mindre än en minut.

### Fördelar med detta system
- **Ingen serverkod krävs:** Du behöver inte bygga egna databaser eller PHP-skript för att samla feedback. GitHub hanterar allt säkert och gratis.
- **Kommunicera med testare:** Inne i GitHub Issues kan du svara testaren *"Tack Karlsson, detta är fixat i senaste uppdateringen. Ladda om appen så fungerar det!"*
- **Agerbart språk för AI:** GitHub Issues är exakt den data-form som kodar-AI (som Antigravity) är absolut bäst på att tolka och agera utifrån. Du slipper agera tolk mellan soldatens gnäll och koden.
