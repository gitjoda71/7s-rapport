# Stabskarta – Aktuellt läge

> Uppdateras automatiskt när nya rapporter inkommer. Ladda om noten vid behov.

```leaflet
id: stabskarta
lat: 59.35
long: 17.85
height: 550px
minZoom: 8
maxZoom: 18
defaultZoom: 13
unit: km
scale: 1
markerFolder: Stabssystem/Rapporter
```

---

## Inkomna rapporter

```dataview
TABLE
  sagesman AS "Sagesman",
  slag AS "Slag",
  styrka AS "Styrka",
  stalle AS "Ställe",
  stund AS "Stund"
FROM "Stabssystem/Rapporter"
WHERE type = "7S"
SORT timestamp DESC
LIMIT 30
```
