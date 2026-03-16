import csv
import json
import logging
from collections import Counter
from pathlib import Path

LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "output" / "dialect_model.json"
CORPUS_PATTERNS = BASE_DIR / "output" / "corpus_patterns.csv"

OUTPUT_MODEL = BASE_DIR / "output" / "dialect_plausibility.json"


def load_dialect_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Dialektmodell nicht gefunden: {MODEL_PATH}")

    with open(MODEL_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_corpus_patterns():

    patterns = Counter()

    if not CORPUS_PATTERNS.exists():
        LOGGER.warning("Corpus-Patterns fehlen: %s", CORPUS_PATTERNS)
        return patterns

    with open(CORPUS_PATTERNS, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                patterns[row["pattern"]] = int(row["frequency"])
            except (KeyError, TypeError, ValueError):
                LOGGER.warning("Ungültige Pattern-Zeile übersprungen: %s", row)

    return patterns


def collect_dictionary_patterns(dictionary):

    patterns = Counter()

    for word in dictionary:

        for i in range(len(word)):

            for j in range(i + 2, min(i + 5, len(word))):

                part = word[i:j]

                patterns[part] += 1

    return patterns


def merge_patterns(dict_patterns, corpus_patterns):

    merged = Counter()

    for k, v in dict_patterns.items():
        merged[k] += v

    for k, v in corpus_patterns.items():
        merged[k] += v * 2  # Korpus stärker gewichten

    return merged


def save_model(patterns):

    model = {
        "metadata": {
            "top_k": 500,
            "corpus_weight": 2,
        },
        "patterns": dict(patterns.most_common(500)),
    }

    OUTPUT_MODEL.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MODEL, "w", encoding="utf-8") as f:

        json.dump(model, f, ensure_ascii=False, indent=2)

    LOGGER.info("Dialekt-Plausibilitätsmodell gespeichert: %s", OUTPUT_MODEL)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    dialect_model = load_dialect_model()

    dictionary = dialect_model["direct_dictionary"].values()

    dict_patterns = collect_dictionary_patterns(dictionary)

    corpus_patterns = load_corpus_patterns()

    merged = merge_patterns(dict_patterns, corpus_patterns)

    save_model(merged)


if __name__ == "__main__":
    main()
