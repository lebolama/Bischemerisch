# Analysis Module – Büschemerisch Dialektanalyse

Dieser Ordner enthält Analysewerkzeuge, die aus der Wortliste

```
data/bischemer_lexikon_master.csv
```

automatisch **sprachliche Regeln des Dialekts Büschemerisch** ableiten.

Ziel ist es, aus Paaren

```
hochdeutsch → bischemerisch
```

Transformationen zu erkennen, die später zur automatischen Dialektübersetzung verwendet werden.

---

# Aufgaben der Analyse

Die Analyse besteht aus mehreren Schritten:

## 1 Wortalignment

Wörter werden Buchstabe für Buchstabe verglichen.

Beispiel:

```
hochdeutsch: einfach
dialekt:     aafoch
```

Alignment:

```
ei → aa
nf → f
ch → ch
```

---

## 2 Mustererkennung

Die häufigsten Veränderungen werden statistisch gesammelt.

Beispiele:

```
ei → aa
pf → f
au → aa
en → e
```

Diese Muster werden als mögliche Dialektregeln betrachtet.

---

## 3 Regelgenerierung

Aus den häufigsten Mustern werden Dialektregeln erzeugt.

Diese Regeln werden später verwendet für:

* automatische Wortübersetzung
* Satzübersetzung
* Prompt-Generierung für LLM-Modelle

---

# Ergebnis der Analyse

Die Analyse erzeugt folgende Dateien:

```
output/dialect_rules.md
output/phonetic_patterns.csv
```

Diese enthalten:

* Lautregeln
* Schreibregeln
* Häufigkeiten
* Beispiele

---

# Ziel

Das langfristige Ziel ist es, ein Regelmodell zu erzeuge
