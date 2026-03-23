# FORMAT.md – Exakt PWA-format för 7S-rapport

Denna fil dokumenterar den exakta textsträngen som `index.html` (PWA:n) genererar
via `generateReport()` och kopierar till urklipp. **Parsningslogiken i `ingest.py`
måste matcha detta format exakt.**

---

## Exempelrapport (kopierad från PWA)

```
7S RAPPORT

Stund: 101423
Ställe: 33VWD1234567890
Styrka: 3
Slag: Fientlig BTR
Sysselsättning: Rör sig norrut längs väg
Symbol: Grön, inga märkningar
Sagesman: NIN 111. 1a p, 2 grp. Nils Nilsson
```

---

## Fältspecifikation

| Fält           | Format / Innehåll                              | Exempel                            |
|----------------|------------------------------------------------|------------------------------------|
| `Stund`        | `DDHHMM` (dag, timme, minut) – 6 siffror      | `101423` = dag 10, kl 14:23        |
| `Ställe`       | Fritext – MGRS-koordinat eller platsnamn       | `33VWD1234567890`                  |
| `Styrka`       | Fritext – antal                                | `3` eller `ca 10`                  |
| `Slag`         | Fritext – typ av fiende/fordon                 | `Fientlig BTR`                     |
| `Sysselsättning` | Fritext – vad fienden gör                    | `Rör sig norrut längs väg`         |
| `Symbol`       | Fritext – färg, märkning, förbandstecken       | `Grön, inga märkningar`            |
| `Sagesman`     | Fritext – observatörens identitet              | `NIN 111. 1a p, 2 grp. Nils Nilsson` |

---

## Kodskelett för generering (ur `index.html`)

```javascript
let report = "7S RAPPORT\n\n";
report += `Stund: ${stund || '-'}\n`;
report += `Ställe: ${stalle || '-'}\n`;
report += `Styrka: ${styrka || '-'}\n`;
report += `Slag: ${slag || '-'}\n`;
report += `Sysselsättning: ${sysselsattning || '-'}\n`;
report += `Symbol: ${symbol || '-'}\n`;
report += `Sagesman: ${sagesman || '-'}`;   // <- OBS: ingen \n i slutet
```

**Viktigt:**
- Tomma fält ersätts med strängen `-` (bindestreck), inte tom sträng.
- Sista raden (`Sagesman`) avslutas **utan** radbrytning `\n`.
- Rapporten börjar alltid med `7S RAPPORT` följt av **två** radbrytningar (`\n\n`).

---

## MGRS-identifiering

MGRS-koordinater i `Ställe`-fältet följer mönstret:

```
\d{2}[A-Z]{3}\d{10}
```

Exempel: `33VWD1234567890` (2 siffror + 3 bokstäver + 10 siffror, utan mellanslag).

Koordinaten kan även skrivas med mellanslag (`33V WD 12345 67890`) – parsern
ska hantera båda varianterna.

---

## Ignorerade rapporttyper

PWA:n genererar även dessa format som stab-systemet **ignorerar** (loggas som rådata):

| Typ   | Kännetecken i texten    |
|-------|-------------------------|
| WHAT  | Börjar med `WHAT`       |
| SCRIM | Börjar med `SCRIM`      |
| WEFT  | Börjar med `WEFT`       |
| AH    | Börjar med `AH RAPPORT` |

En rapport identifieras som 7S om den börjar med `7S RAPPORT`.
