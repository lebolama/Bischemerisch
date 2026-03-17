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
```

---

## Projektstruktur (aktuell)

```text
Bischemerisch/
├── analysis/
│   ├── build_dialect_model.py
│   ├── rule_miner.py
│   ├── phonetic_model.py
│   ├── corpus_rule_learner.py
│   ├── dialect_plausibility_model.py
│   └── ...
├── generator/
│   ├── rule_based_translator.py
│   ├── sentence_transformer.py
│   ├── novel_word_generator.py
│   ├── confidence_estimator.py
│   └── ...
├── learning/
├── prompts/
│   ├── bischemer_prompt_template.txt
│   └── prompt_builder.py
├── data/
├── output/
└── tests/
```

---

## Kern-Workflow

### 1) Modell bauen

```bash
python analysis/build_dialect_model.py
```

Erzeugt u. a.:

- `output/dialect_model.json`
- `output/llm_rules.txt`

### 2) Grammatikmodell erzeugen

```bash
python analysis/grammar_model.py
```

Erzeugt:

- `output/grammar_rules.json`

### 3) Prompt erzeugen

```bash
python prompts/prompt_builder.py
```

Erzeugt:

- `output/generated_prompt.txt`

> `output/generated_prompt.txt` wird bewusst aus dem Template gebaut,
> damit Prompt-Logik reproduzierbar bleibt.

### 4) Übersetzung testen

```bash
python -m tests.translation_tests
```

---

## Hinweise

- Wörterbucheinträge haben Priorität gegenüber abgeleiteten Regeln.
- Das Korpus (`baerthel.txt`) wird zur Ableitung zusätzlicher Dialektsignaturen genutzt.
- Für unbekannte Wörter nutzt der Generator Regeln + korpusgestützte Muster.

---

## Endziel

Ein robustes Regelmodell und ein konsistenter Prompt, die ein LLM befähigen,
**flüssig und möglichst authentisch Büschemerisch** zu erzeugen.
