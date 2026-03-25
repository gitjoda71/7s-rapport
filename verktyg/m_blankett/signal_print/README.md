# M-blankett Signal → PDF → Skrivare

Automatisk pipeline som lyssnar på en Signal-grupp, tar emot meddelanden, formaterar dem som svenska M-blanketter (PDF) och skriver ut dem automatiskt.

**Digitalt in → Analogt ut. Helt automatiskt.**

## Snabbstart

### 1. Klona och installera

```bash
git clone <repo-url>
cd signal_print
pip install -r requirements.txt
```

### 2. Konfigurera

```bash
cp config.example.env .env
```

Redigera `.env`:
```ini
SIGNAL_GROUP_ID=din-grupp-id-här
PRINTER_NAME=default
PORT=8080
```

### 3. Starta signal-cli-rest-api (Docker)

```bash
docker run -d --name signal-api \
  -p 8088:8080 \
  -v $HOME/.local/share/signal-cli:/home/.local/share/signal-cli \
  -e MODE=json-rpc \
  bbernhard/signal-cli-rest-api
```

Registrera ditt nummer (första gången):
```bash
curl -X POST 'http://localhost:8088/v1/register/<+46NUMMER>'
curl -X POST 'http://localhost:8088/v1/register/<+46NUMMER>/verify/<KOD>'
```

Konfigurera webhook i signal-cli-rest-api:
```bash
curl -X POST 'http://localhost:8088/v1/webhook' \
  -H 'Content-Type: application/json' \
  -d '{"url": "http://localhost:8080/api/v1/webhook"}'
```

### 4. Starta M-blankett-servern

```bash
python main.py
```

Klart! Meddelanden i Signal-gruppen genererar nu automatiskt M-blanketter och skriver ut dem.

## Testa utan Signal

Generera test-PDF:er från exempelfiler:

```bash
python m_blankett_pdf.py
```

Eller med en specifik fil:

```bash
python m_blankett_pdf.py ../tests/test1_valstrukturerad.txt output/test.pdf
```

Testa utskrift:

```bash
python printer.py output/test1_valstrukturerad.pdf
```

## Meddelandeformat

Meddelanden i Signal-gruppen skrivs i detta format:

```
TILL: Insatskompaniet
FRÅN: Bataljonsstaben
TID: 251400A MAR 2026
ÄMNE: ORDER LÅNGBEN
SIGN: N. Nilsson
---
1. LÄGE
Fienden befinner sig söder om...

2. UPPGIFT
Insatskompaniet ska lösa...
```

**Alla fält är valfria.** Om fält saknas lämnas de tomma i blanketten. Om ingen struktur hittas alls hamnar hela texten i brödtexten. Om TID saknas genereras ett TNR automatiskt.

## Plattformsstöd

| OS | Utskrift | Status |
|----|----------|--------|
| **Mac** | `lp` (inbyggt) | Fungerar direkt |
| **Linux** | `lp` (CUPS) | Fungerar direkt |
| **Windows** | SumatraPDF eller Windows shell | Installera [SumatraPDF](https://www.sumatrapdfreader.com/) för tyst utskrift |

## Konfiguration (.env)

| Variabel | Standard | Beskrivning |
|----------|----------|-------------|
| `SIGNAL_GROUP_ID` | *(tom)* | Signal-gruppens ID. Tom = alla grupper |
| `PRINTER_NAME` | `default` | Skrivarnamn. `default` = systemets standardskrivare |
| `PRINTER_METHOD` | `auto` | `auto`, `lp`, `sumatrapdf`, `osprint` |
| `OUTPUT_DIR` | `./output` | Mapp för genererade PDF:er |
| `PORT` | `8080` | Port för webhook-servern |
| `AUTO_PRINT` | `true` | Skriv ut automatiskt (`true`/`false`) |

## Arkitektur

```
Signal-grupp
    │
    ▼
signal-cli-rest-api (Docker)
    │ webhook POST
    ▼
signal_listener.py (FastAPI)
    │
    ├─► m_blankett_pdf.py  →  PDF-fil
    │
    └─► printer.py  →  Skrivare
```

## Beroenden

- Python 3.10+
- fpdf2 (PDF-generering)
- FastAPI + uvicorn (webhook-server)
- python-dotenv (konfiguration)
- Docker (för signal-cli-rest-api)
