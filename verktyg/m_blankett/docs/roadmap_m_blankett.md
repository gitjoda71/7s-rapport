# Roadmap: Automatisering av M-blankett i Microsoft Word (VBA)

Detta dokument fungerar som en detaljerad och tekniskt handlingsinriktad roadmap för att bygga ett VBA-makro i Microsoft Word som omvandlar råtext till en svensk M-blankett. Dokumentet är särskilt framtaget för att överlämnas till en AI-kodassistent (Claude Opus 4.6).

För att säkerställa att lösningen blir städad, skalbar och framtidssäkrad har följande mappstruktur upprättats lokalt/på Dropbox och ska användas för projektet:
`hv/verktyg/m_blankett/`
- `docs/` - Dokumentation, roadmaps och kravspecifikationer.
- `src/vba/` - Exporterade `.bas`- eller `.cls`-filer med VBA-kod för versionshantering.
- `templates/` - Word-mallar (`.dotm`) som innehåller makrot.
- `tests/` - Testfiler med exempel på råtext (indata) respektive förväntad M-blankett (utdata).

---

## A. Målbild
**Syfte:** En användare ska kunna klistra in en oformaterad textmassa i ett Word-dokument, köra ett makro, och få innehållet automatiskt strukturerat och formaterat så att det liknar en klassisk svensk Meddelande-blankett (M-blankett).
**Känsla:** Resultatet ska omedelbart kännas igen av användare som vanligen fyller i M-blanketter. Utseendet ska vara lågmält, sparsmakat och maskinskrivet/funktionellt – *inte* en snygg inhouse-design eller modern tidningslayout. 

**Användarflöde:**
1. Användaren öppnar en Word-mall (`.dotm`) eller ett dokument med makrot förberett.
2. Användaren klistrar in sin text (t.ex. en rapport eller order) skriven i ett överenskommet format.
3. Användaren klickar på en knapp ("Skapa M-blankett") eller använder ett kortkommando.
4. Makrot extraherar fält som *Från, Till, Tid, Samverkansgrad* och *Ämne*, bygger header-delen med korrekt avstånd och lägger därefter in själva meddelandetexten i brödtextformatet.
5. Inga felmeddelanden visas om fält saknas; makrot degraderar snyggt.

---

## B. Analys av referensblanketten
Ur den ursprungliga referens-PDF:en (Handbok Stabstjänst Grunder 2016, s. 101-102) går det att utläsa att M-blanketten bygger på ett tydligt formulär med specifika informationsblock. 

**Kännetecken att återskapa i Word:**
- **Informationshierarki:** Upptill finns fält för routing och administration (Till, Från, Avdelning, Tid, Signalskyddsgrad, Löpnummer etc.).
- **Etiketter:** Fältnamn skrivs traditionellt i versaler (t.ex. "FRÅN", "TILL", "AVS SIGN") med en liten (ofta 8–9 pt) stil för att inte stjäla uppmärksamhet.
- **Linjering:** Informationen är strikt uppdelad, ibland avgränsad av tydliga svarta streck. Mellan huvudet och själva meddelandetexten finns ett tydligt skiljestreck (t.ex. kantlinje under stycke).
- **Styckeindelning:** Meddelandetexten har enkla radbrytningar. Ingen extra spaltning.
- **Typografi:** Tydlig koppling till äldre skrivmaskinsarv. Ett vanligt typsnitt som Arial, Calibri eller Courier New i 10–11 pt är tillräckligt. Inga specialtypsnitt.

**Vad som INTE behöver återskapas:**
- Checkrutor för "Krypto/Klartext" eller "Sänt/Mott" som ska fyllas i manuellt med penna om de inte efterfrågas i råtexten.
- Fysiska textrutor/tabeller för kryssrutor som komplicerar Word-layouten. 

---

## C. Tolkning av råtext
För att makrot robust ska kunna parsa råtexten, rekommenderas ett tydligt men enkelt "markdown-liknande" nyckelordsformat baserat på kolon.

**Exempel på föreslagen MVP-råtext:**
```text
TILL: Insatskompaniet
FRÅN: Bataljonsstaben
TID: 151500A
ÄMNE: ORDER LÅNGBEN
SIGN: N. Nilsson
---
1. LÄGE
Fienden befinner sig söder om objekt...

2. UPPGIFT
Insatskompaniet ska lösa...

[Ytterligare fritext och vanliga radbrytningar]
```

**Tolkningslogik:**
- Makrot läser rad för rad fram till avskiljaren `---` (eller tre tomma rader om avskiljare saknas).
- Nyckelorden i headern identifieras via Regex (t.ex. `^TILL:\s*(.*)`). 
- Allt efter avskiljaren `---` (utom SIGN) hanteras som ren brödtext/meddelande.
- Fältet `SIGN:` (Underskrift) kan valfritt ligga i botten av inmatningen men ska tvingas ner i slutet av dokumentet under en valfri avslutande rad.

---

## D. Teknisk VBA-strategi
För att uppnå "blankettkänsla" utan att skapa en frustrerande Word-fil full av stela tabeller, bör VBA-makrot förlita sig på **Word Styles** och **Tab Stops**.

**Arkitekturrekommendation för Claude Opus:**
1. **Råtextextraktion:** Makrot sparar hela dokumentets text i en osynlig string-variabel och rensar sedan dokumentet helt (`ActiveDocument.Content.Text = ""`).
2. **Regex Parsing:** Använd VBScript.RegExp för att hitta fälten och spara dem i en struktur (Dictionary eller Type). Separering av Header-data och Body-text.
3. **Paginering & Layout (Paragraphs):** 
   - Makrot skapar nya `Paragraph`-objekt linje för linje. 
   - Tab-stopp appliceras på styckenivå (`Paragraph.TabStops.Add`) för att t.ex. linjera fälten "FRÅN" och "TID" på samma visuella rad men med vänster- respektive styrsättning på fasta centimeter-mått.
4. **Programmatisk formatering (Direct Formatting vs Styles):** Skapa Word-styles i mallen (`M_HeaderField`, `M_HeaderValue`, `M_BodyText`) och låt makrot tilldela dessa *eller* applicera direkt formatering (ex. `.Font.Size = 8`, `.Font.Allcaps = True` för etiketter) vid textgenereringen ifall inga malländringar önskas.
5. **Robusthet:** All textinsättning sker med `Range`-objekt (snabbt och stabilt), undvik `Selection`.

---

## E. Implementationsplan i etapper

**Steg 1: Mall och Mappstruktur**
- Skapa en `.dotm`-fil i `templates/`. Säkerställ att sidmarginalerna är något bredare (standardtjänstedokument). Bygg kofots-stilar (Styles) om nödvändigt.

**Steg 2: Skapa Parsern (VBA)**
- *Syfte:* Att ta textsträngen och bryta isär den i dess logiska beståndsdelar.
- *Test:* Validera med en MsgBox eller Debug.Print att funktionen korrekt separerat "Till", "Från", och Body.

**Steg 3: Applicera Grundlayout (Header)**
- *Syfte:* Rensa dokumentet och rita upp M-blankettens huvud med fältetiketter på översta raden och värdena inunder genom `Range.InsertAfter`.
- *Test:* Verifiera att "Till" och "Från" linjerar prydligt och att etiketter är små versaler. Rita ut ett understruket streck under headern (BorderBottom).

**Steg 4: Brödtext och Sektioner**
- *Syfte:* Klistra in Body-texten under headern. 
- *Test:* Säkerställ att radbrytningar respekteras men att inga löjligt stora avstånd skapas mellan stycken (0 pt before, max 6 pt after).

**Steg 5: Testning mot extremfall**
- Se *Teststrategi*.

---

## F. Förslag på konkret dokumentlayout i Word
- **Typsnitt:** Hela dokumentet i Arial (eller likvärdigt linjärt typsnitt).
- **Etiketter i Huvud:** 8 pt, STOR BOKSTÄVER, grå text (RGB: 80,80,80) eller svart.
- **Inmatade Header-värden:** 11 pt, Svart, Fetstil (frivilligt men ökar läsbarhet).
- **Placering Huvud (via Tabb-stopp):**
  - Vänster: TILL, AVS SIGN
  - Mitten (Tab runt 7cm): FRÅN
  - Höger (Tab runt 13cm): TID (datum och klockslag)
- **Avdelare:** Ett massivt svart streck (Styckekantlinje / Bottom Border) under det sista Header-fältet.
- **Meddelandetext (Body):** 11 pt, vanligt, ingen fetstil, vänsterställt men med ett indrag (Left Indent) på 0.5 cm för att ge en blankettliknande inramning. Enkelt radavstånd.
- **Avslutning:** Etiketten "SIGNATURE:" längst ner följt av eventuellt signaturvärde.

---

## G. Felhantering och begränsningar
**Degraderingsprinciper:**
1. **Saknad avgränsare (`---`):** Om makrot inte hittar strängen `---` läser det fram till första tomma Dubbel-radbrytning, eller antar att allt som inte matchar kända fält med kolon är brödtext.
2. **Okända fält:** Ignoreras i sidhuvudet och flyter med in i M-blankettens brödtext, så att data aldrig går förlorad.
3. **Skadad Råtext:** Om texten är helt formlös och saknar kolon plockas ingenting ut, men koden kraschar inte. Hela texten skrivs istället ut i brödtexten.

---

## H. Teststrategi
De slutgiltiga testerna ska sparas som textfiler i `tests/`.

1. **Test 1: Välstrukturerad råtext**
   *Input:* Innehåller alla fältnamn (TILL:, FRÅN:, TID:, ÄMNE:, SIGN:) och är separerat med `---`.
   *Förväntat resultat:* Perfekt genererad ruta i toppen och snygg brödtext.
2. **Test 2: Halvstrukturerad råtext (Missing fields)**
   *Input:* Saknar TID och SIGN. Ingen `---` men en extra tomrad mellan header och body.
   *Förväntat resultat:* Att "TID" blir tomt i blankettmallen. Resten ritas upp korrekt.
3. **Test 3: Rörig råtext / Ren fritext**
   *Input:* Bara en lång textmassa från ett klippbord utan nyckelord.
   *Förväntat resultat:* Huvudet trycks med tomma linjer. Hela textmassan läggs in i Body. Ingen krasch.

---

## J. Framtida etapp: Signal-integration (digital → analog automat)

> **Status:** Planerad – ej påbörjad. Implementeras i en senare fas.

**Syfte:** Skapa en helautomatisk pipeline som övervakar en Signal-grupp, fångar inkommande meddelanden och producerar en utskriven M-blankett på papper – utan manuell interaktion. Digitalt in, analogt ut.

**Översikt:**
```
Signal-grupp → Python-tjänst (parsa + generera PDF) → Skriv ut PDF på förvald skrivare
```

**Tekniskt vägval:** Word COM-automation har ratats till förmån för en ren Python-lösning som genererar PDF direkt. Detta eliminerar beroendet av en Word-licens, undviker den sköra COM-automatiseringen och gör lösningen plattformsoberoende.

**Funktionskrav:**

1. **Signal-lyssnare (plugin/bot/bridge):**
   - Övervakar en specifik, förkonfigurerad Signal-grupp.
   - Reagerar på varje nytt inkommande meddelande.
   - Teknikalternativ att utvärdera: signal-cli (CLI-baserat), signal-cli-rest-api (REST-wrapper), eller liknande bridge/bot-lösning.

2. **Meddelandeextraktion:**
   - Kopierar meddelandets fullständiga text.
   - Om meddelandetexten saknar ett TNR (tidnummerreferens/löpnummer) ska ett sådant genereras automatiskt baserat på tidpunkten då meddelandet skickades (t.ex. `260800AMAR2026` eller ett löpande serienummer).

3. **PDF-generering (ersätter Word-automation):**
   - Python parsar meddelandetexten med samma logik som VBA-parsern (regex-fältextraktion, header/body-separation).
   - Genererar en PDF med M-blankettens layout direkt via **FPDF2** (lättviktsbibliotek, ren Python, inga externa beroenden).
   - Alternativ: **ReportLab** (kraftfullare) eller **WeasyPrint** (HTML/CSS → PDF, flexibel layout).
   - PDF:en sparas tillfälligt innan utskrift.

4. **Automatisk utskrift:**
   - **Windows:** `SumatraPDF -print-to "Skrivarnamn" fil.pdf` (tyst utskrift, gratis) eller PowerShell `Start-Process`.
   - **Linux/Mac:** `lp` eller `lpr` kommandot.
   - Skrivare konfigureras i en settings-fil (`.env` eller `config.json`).

**Arkitekturskiss:**
```
┌─────────────┐     ┌──────────────────────────────────┐     ┌───────────┐
│  Signal-     │────▶│  Python-tjänst                   │────▶│  Skrivare │
│  grupp       │     │  1. signal-cli (lyssna)          │     │  (förvald)│
│              │     │  2. Parsa meddelande + skapa TNR │     │           │
│              │     │  3. FPDF2 → M-blankett.pdf       │     │           │
│              │     │  4. SumatraPDF/lp → utskrift     │     │           │
└─────────────┘     └──────────────────────────────────┘     └───────────┘
```

**Beroenden (pip):**
- `fpdf2` — PDF-generering
- Inget Word, ingen COM, ingen .dotm-mall behövs

**Överväganden:**
- **Säkerhet:** Signal-klienten kräver registrering och krypteringsnycklar. Dessa ska förvaras säkert, inte i repot.
- **Plattform:** Lösningen är plattformsoberoende (Windows/Linux/Mac). Enda plattformsspecifika delen är utskriftskommandot.
- **Felhantering:** Om skrivaren inte är tillgänglig ska meddelandet köas och skrivas ut när resursen blir tillgänglig igen.
- **Loggning:** Alla mottagna och utskrivna meddelanden loggas med tidstämpel och TNR för spårbarhet.
- **VBA-makrot lever kvar:** Det manuella Word-makrot (`MBlankett_Allt.bas`) behålls som ett separat verktyg för användare som vill formatera M-blanketter manuellt i Word. Automatpipelinen är fristående.

---

## I. Instruktion till Claude Opus 4.6

**Hej Claude!** Din uppgift är att implementera VBA-koden för Microsoft Word baserad på denna roadmap.
Följande principer och ordning gäller för din iteration:
1. **Fokusera på arkitekturen först:** Skapa logiken för Regex-parsing och hantering av Range-objekt (som förklarat i kapitel D) innan du gräver ner dig i exakta layoutmått. Bygg upp moduler/subrutiner (ParseText, BuildHeader, BuildBody). Exportera gärna funktionerna som `.bas` för placering i `src/vba/`.
2. **Enkelhet före extravagans:** Använd Paragraph-objekt och TabStops hellre än röriga och prestandatunga Tables. Resultatet ska kännas "tjänstemässigt" och rustikt.
3. **Säkerhet & Degradering:** Felhantering är extremt viktigt (kapitel G). Användaren klipp-och-klistrar från diverse chatprogram eller anteckningar. Koden får inte krascha oavsett inmatning; okänd text ska alltid spillas över i brödtext-området.
4. **Din första leverans:** Skriv de faktiska VBA-funktionerna för att extrahera text via Regular Expressions och sätta in den i ett nytt tomt dokument. Lämna kommentarer där layout-specifik finjustering (font-storlek, tab-stopp centimeters) appliceras.
5. **Verktygskedjan:** Anteckna dina macro-skripts i mappen `src/vba` inom det överenskomna systemet (`hv/verktyg/m_blankett/src/vba/`). 

Börja implementera enligt etapp 1 och 2 (se kapitel E). Tillämpa bästa praxis för VBA (Option Explicit, tydlig variabelnamngivning, nollställande av objekt).
