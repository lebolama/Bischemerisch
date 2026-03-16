import csv
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "bischemer_lexikon_master.csv"
OUTPUT_PATH = BASE_DIR / "output" / "phonetic_patterns.csv"


VOWELS = "aeiouäöü"


def split_syllables(word):
    """
    Sehr einfache Silbentrennung.
    """

    syllables = []
    current = ""

    for c in word:

        current += c

        if c in VOWELS:

            syllables.append(current)
            current = ""

    if current:
        syllables.append(current)

    return syllables


def load_pairs():

    pairs = []

    with open(DATA_PATH, encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for r in reader:

            pairs.append(
                (r["hochdeutsch"].lower(), r["bischemerisch"].lower())
            )

    return pairs


def extract_patterns():

    pairs = load_pairs()

    counter = Counter()

    for hd, bi in pairs:

        for i in range(len(hd)):

            for j in range(i + 1, min(i + 4, len(hd))):

                src = hd[i:j]

                if src in bi:
                    continue

                if len(src) < 2:
                    continue

                counter[src] += 1

    return counter


def save_patterns(counter):

    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:

        writer = csv.writer(f)

        writer.writerow(["pattern", "frequency"])

        for p, n in counter.most_common(200):

            writer.writerow([p, n])


if __name__ == "__main__":

    patterns = extract_patterns()

    save_patterns(patterns)

    print("Phonetische Muster gespeichert:")
    print(OUTPUT_PATH)
