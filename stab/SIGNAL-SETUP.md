# Signal → Obsidian – Installationsguide

## Översikt

```
Signal-grupp → signal-cli-rest-api [Docker :8080] → ingest.py [:8000] → Obsidian
```

---

## Steg 1 – Installera Docker Desktop

1. Gå till https://www.docker.com/products/docker-desktop
2. Ladda ned och installera (Windows-versionen)
3. Starta om datorn
4. Öppna Docker Desktop och vänta tills det står "Engine running"

---

## Steg 2 – Länka Signal-nummer

Öppna en terminal i den här mappen (`hv/stab/`) och kör:

```
docker compose up -d
```

Öppna sedan i webbläsaren:

```
http://localhost:8080/v1/qrcodelink?device_name=Stab
```

En QR-kod visas. Scanna den med Signal-appen på din mobil:
**Signal → Inställningar → Länkade enheter → Länka ny enhet**

Vänta ca 10 sekunder. Länkningen är klar när QR-sidan försvinner.

---

## Steg 3 – Hitta grupp-ID

Kör följande kommando i terminalen (byt ut `+46XXXXXXXXX` mot ditt nummer):

```
curl http://localhost:8080/v1/groups/+46XXXXXXXXX
```

Svaret är en JSON-lista med dina grupper. Leta upp rätt grupp och kopiera dess `id`-fält
(ser ut som `group.XXXX...`).

---

## Steg 4 – Starta ingest.py

Dubbelklicka på `run_system.bat` i den här mappen.

Terminalen ska visa:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Steg 5 – Testa

Skicka ett 7S-meddelande i Signal-gruppen:

```
7S RAPPORT

Stund: 101423
Ställe: 34VDL3300083000
Styrka: 3
Slag: Personbil
Sysselsättning: Rör sig norrut
Symbol: Röd
Sagesman: NIN 111. 1a p, 2 grp. Nils Nilsson
```

En ny not ska skapas i `Stabssystem/Rapporter/` och en ny pin dyka upp på Masterkartan.

---

## Kontrollkommandon

| Kommando | Syfte |
|----------|-------|
| `docker compose up -d` | Starta Signal-bryggan |
| `docker compose down` | Stoppa Signal-bryggan |
| `docker compose logs -f` | Se live-logg från containern |
| `curl http://localhost:8000/health` | Kontrollera att ingest.py är igång |

---

## Felsökning

**Pinen dyker inte upp i Obsidian:**
- Kontrollera att ingest.py körs (`run_system.bat`)
- Kontrollera att Obsidian Local REST API-pluginet är aktiverat (Inställningar → Plugin)
- Kontrollera att OBSIDIAN_TOKEN i `.env` stämmer med pluginets token

**Signal-länken försvann:**
- Kör `docker compose down && docker compose up -d` och länka om

**Felmeddelande "MGRS parse error":**
- Kontrollera att Ställe-fältet innehåller en giltig MGRS-koordinat
- Rapporten loggas ändå som rådata i `raw_signals.log`
