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

Projektstruktur (aktuell)
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

Kern-Workflow
1) Modell bauen
python analysis/build_dialect_model.py
Erzeugt u. a.:

output/dialect_model.json

output/llm_rules.txt

2) Grammatikmodell erzeugen
python analysis/grammar_model.py
Erzeugt:

output/grammar_rules.json

3) Prompt erzeugen
python prompts/prompt_builder.py
Erzeugt:

output/generated_prompt.txt

output/generated_prompt.txt wird bewusst aus dem Template gebaut,
damit Prompt-Logik reproduzierbar bleibt.

4) Übersetzung testen
python -m tests.translation_tests
Hinweise
Wörterbucheinträge haben Priorität gegenüber abgeleiteten Regeln.

Das Korpus (baerthel.txt) wird zur Ableitung zusätzlicher Dialektsignaturen genutzt.

Für unbekannte Wörter nutzt der Generator Regeln + korpusgestützte Muster.

Endziel
Ein robustes Regelmodell und ein konsistenter Prompt, die ein LLM befähigen,
flüssig und möglichst authentisch Büschemerisch zu erzeugen.


### `generator/sentence_transformer.py`
```python
from generator.rule_based_translator import load_model, translate_sentence as translate_sentence_rule_based

_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = load_model()
    return _MODEL


def translate_sentence(sentence):
    return translate_sentence_rule_based(sentence, _get_model())


if __name__ == "__main__":
    sample = "Der Apfel liegt auf dem Tisch."
    print("Hochdeutsch:", sample)
    print("Bischemerisch:", translate_sentence(sample))
