import logging
from collections import Counter
from pathlib import Path

from analysis.word_alignment import load_dictionary, align_words

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "bischemer_lexikon_master.csv"


def extract_patterns():

    pairs = load_dictionary(DATA_PATH)

    alignments = align_words(pairs)

    counter = Counter()

    for a in alignments:

        if a["type"] == "replace":

            key = f"{a['hochdeutsch']} -> {a['dialekt']}"

            counter[key] += 1

    return counter


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    patterns = extract_patterns()

    for p, n in patterns.most_common(40):
        logging.info("%s %s", p, n)
