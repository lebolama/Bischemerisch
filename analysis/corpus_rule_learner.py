import csv
import logging
import re
from collections import Counter
from pathlib import Path

LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

CORPUS_PATH = BASE_DIR / "data" / "baerthel.txt"
MODEL_PATH = BASE_DIR / "output" / "dialect_model.json"

OUTPUT_WORDS = BASE_DIR / "output" / "corpus_dialect_words.csv"
OUTPUT_PATTERNS = BASE_DIR / "output" / "corpus_patterns.csv"


def load_corpus():

    if not CORPUS_PATH.exists():
        raise FileNotFoundError(f"Corpus-Datei nicht gefunden: {CORPUS_PATH}")

    with open(CORPUS_PATH, encoding="utf-8") as f:

        return f.read().lower()


def tokenize(text):

    return re.findall(r"[a-zäöüß]+", text)


def load_dictionary():
    import json

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Dialektmodell nicht gefunden: {MODEL_PATH}")

    with open(MODEL_PATH, encoding="utf-8") as f:

        model = json.load(f)

    return set(model["direct_dictionary"].values())


def extract_frequent_words(tokens, dictionary):

    counter = Counter(tokens)

    results = []

    for word, freq in counter.most_common(500):

        if len(word) < 3:
            continue

        # bereits bekannte Dialektwörter ignorieren
        if word in dictionary:
            continue

        results.append((word, freq))

    return results


def extract_patterns(tokens):

    patterns = Counter()

    for word in tokens:

        for i in range(len(word)):

            for j in range(i + 2, min(i + 5, len(word))):

                part = word[i:j]

                if len(part) >= 2:

                    patterns[part] += 1

    return patterns


def save_words(words):
    OUTPUT_WORDS.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_WORDS, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["dialektwort", "frequency"])
        writer.writerows(words)


def save_patterns(patterns):
    OUTPUT_PATTERNS.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATTERNS, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pattern", "frequency"])
        for p, n in patterns.most_common(200):
            writer.writerow([p, n])


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    text = load_corpus()
    tokens = tokenize(text)

    dictionary = load_dictionary()

    frequent_words = extract_frequent_words(tokens, dictionary)

    patterns = extract_patterns(tokens)

    save_words(frequent_words)

    save_patterns(patterns)

    LOGGER.info("Corpus-Analyse abgeschlossen.")
    LOGGER.info("Neue Dialektwörter: %s", OUTPUT_WORDS)
    LOGGER.info("Neue Muster: %s", OUTPUT_PATTERNS)


if __name__ == "__main__":
    main()
