# Rapporter – TV-vy

```dataview
TABLE WITHOUT ID
  stund AS "Stund",
  sagesman AS "Sagesman",
  slag AS "Slag",
  styrka AS "Styrka",
  sysselsattning AS "Sysselsättning",
  stalle AS "Ställe"
FROM "Stabssystem/Rapporter"
WHERE type = "7S"
SORT timestamp DESC
LIMIT 50
```
