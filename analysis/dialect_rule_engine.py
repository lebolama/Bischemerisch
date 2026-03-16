import csv
from collections import Counter
import difflib

DICT_PATH = "../data/bischemer_lexikon_master.csv"


def load_dictionary():

    pairs = []

    with open(DICT_PATH, encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            hd = row["hochdeutsch"].lower()
            dialect = row["bischemerisch"].lower()

            pairs.append((hd, dialect))

    return pairs


def align_words(pairs):

    transformations = []

    for hd, dialect in pairs:

        matcher = difflib.SequenceMatcher(None, hd, dialect)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():

            if tag == "replace":

                transformations.append(
                    (hd[i1:i2], dialect[j1:j2])
                )

    return transformations


def discover_rules():

    pairs = load_dictionary()

    transforms = align_words(pairs)

    counter = Counter(transforms)

    rules = []

    for (src, dst), freq in counter.most_common():

        if freq > 5:

            rules.append({
                "hochdeutsch": src,
                "dialekt": dst,
                "count": freq
            })

    return rules


def save_rules(rules):

    with open("../output/phonetic_rules.csv", "w", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow(["hochdeutsch", "dialekt", "frequency"])

        for r in rules:

            writer.writerow([
                r["hochdeutsch"],
                r["dialekt"],
                r["count"]
            ])


if __name__ == "__main__":

    rules = discover_rules()

    save_rules(rules)

    for r in rules[:30]:

        print(r)
