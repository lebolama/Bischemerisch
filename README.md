# Büschemerisch AI – Dialektmodell für Tauberbischofsheim

## Ziel des Projekts

Dieses Projekt erzeugt automatisch ein **Dialektmodell für Büschemerisch (Bischemerisch)**, den historischen Dialekt der Stadt Tauberbischofsheim.

Ziel ist es, aus einer Wortliste mit Paaren

Hochdeutsch → Büschemerisch

automatisch **sprachliche Transformationsregeln** abzuleiten.

Diese Regeln werden anschließend verwendet, um:

1. Hochdeutsche Wörter automatisch in Büschemerisch umzuwandeln
2. ganze Sätze zu dialektisieren
3. einen Prompt zu erzeugen, der andere LLM-Modelle dazu befähigt, Büschemerisch zu sprechen.

---

# Datenbasis

Die zentrale Datei ist:

```
data/bischemer_lexikon_master.csv
```

Format:

```
hochdeutsch,bischemerisch
Apfel,Apfl
Augen,Aache
einfach,aafoch
```

Jede Dialektvariante steht in einer eigenen Zeile.

---

# Projektstruktur

```
bischemerisch-ai/
│
├── data/
│   └── bischemer_lexikon_master.csv
│
├── analysis/
│   ├── word_alignment.py
│   ├── phonetic_patterns.py
│   └── rule_extraction.py
│
├── generator/
│   ├── dialect_translator.py
│   └── apply_rules.py
│
├── prompts/
│   └── bischemer_prompt_template.txt
│
├── output/
│   ├── dialect_rules.md
│   ├── generated_prompt.txt
│   └── unsichere_woerter.csv
│
└── README.md
```

---

# Aufgaben für Codex

## 1 Regelanalyse

Codex soll aus den Wortpaaren:

```
einfach → aafoch
Apfel → Apfl
Augen → Aache
```

automatisch Transformationsregeln erkennen.

Beispiele:

```
ei → aa
pf → f
au → aa
en → e
```

---

## 2 Dialektgenerator

Codex soll eine Funktion erzeugen:

```
translate_sentence(sentence)
```

die Hochdeutsch automatisch in Büschemerisch überführt.

Dabei sollen folgende Ebenen berücksichtigt werden:

* Lautverschiebungen
* Endungen
* Dialektwörter
* Wortersetzungen

---

## 3 Promptgenerator

Codex soll automatisch einen Prompt erzeugen:

```
prompts/generated_prompt.txt
```

Dieser Prompt soll enthalten:

* Dialektbeschreibung
* Lautregeln
* Grammatikregeln
* Beispiele

Dieser Prompt wird später zusammen mit der Wortliste anderen LLMs gegeben.

---

## 4 Unsicherheitsanalyse

Nicht alle Wörter lassen sich zuverlässig per Regel übersetzen.

Codex soll daher:

1. eine große deutsche Wortliste analysieren
2. Dialektformen generieren
3. einen Confidence-Score berechnen
4. unsichere Wörter sammeln

Datei:

```
output/unsichere_woerter.csv
```

Format:

```
hochdeutsch,vorschlag,confidence
Krankenhaus,Krankehaus,0.41
Telefon,Telifoon,0.33
```

---

# Endziel

Das Projekt soll einen Prompt erzeugen, der jedes LLM dazu befähigt:

**flüssig Büschemerisch zu sprechen.**

Dieser Prompt wird später zusammen mit der Wortliste verwendet.
