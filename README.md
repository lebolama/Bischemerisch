# Büschemerisch AI – Dialektmodell für Tauberbischofsheim

## Ziel des Projekts

Dieses Projekt erzeugt automatisch ein **Dialektmodell für Büschemerisch (Bischemerisch)**,
den historischen Dialekt der Stadt Tauberbischofsheim.

Aus einer Wortliste mit Paaren

**Hochdeutsch -> Büschemerisch**

werden sprachliche Transformationsregeln abgeleitet, die für

1. Wortübersetzung,
2. Satzübersetzung,
3. LLM-Prompt-Erzeugung

verwendet werden.

---

## Datenbasis

- Wörterbuch: `data/bischemer_lexikon_master.csv`
- Korpus: `data/baerthel.txt`

CSV-Format:

```csv
hochdeutsch,bischemerisch
Apfel,Apfl
Augen,Aache
einfach,aafoch
