import re
import json
import sys
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

CORPUS_PATH = BASE_DIR / "data" / "baerthel.txt"
MODEL_PATH = BASE_DIR / "output" / "dialect_model.json"

OUTPUT_WORDS = BASE_DIR / "output" / "corpus_dialect_words.csv"
OUTPUT_PATTERNS = BASE_DIR / "output" / "corpus_patterns.csv"


def load_corpus():

    if not CORPUS_PATH.exists():

        print("Corpus-Datei nicht gefunden:", CORPUS_PATH)
        return ""

    with open(CORPUS_PATH, encoding="utf-8") as f:

        return f.read().lower()


def tokenize(text):

    return re.findall(r"[a-zäöüß]+", text)


def load_dictionary():

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

    with open(OUTPUT_WORDS, "w", encoding="utf-8") as f:

        f.write("dialektwort,frequency\n")

        for w, n in words:

            f.write(f"{w},{n}\n")


def save_patterns(patterns):

    with open(OUTPUT_PATTERNS, "w", encoding="utf-8") as f:

        f.write("pattern,frequency\n")

        for p, n in patterns.most_common(200):

            f.write(f"{p},{n}\n")


def main():

    text = load_corpus()

    if not text:
        return

    tokens = tokenize(text)

    dictionary = load_dictionary()

    frequent_words = extract_frequent_words(tokens, dictionary)

    patterns = extract_patterns(tokens)

    save_words(frequent_words)

    save_patterns(patterns)

    print("Corpus-Analyse abgeschlossen.")
    print("Neue Dialektwörter:", OUTPUT_WORDS)
    print("Neue Muster:", OUTPUT_PATTERNS)


if __name__ == "__main__":
    main()
