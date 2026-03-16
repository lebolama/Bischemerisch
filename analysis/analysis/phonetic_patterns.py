from collections import Counter
from word_alignment import load_dictionary, align_words


def extract_patterns():

    pairs = load_dictionary("../data/bischemer_lexikon_master.csv")

    alignments = align_words(pairs)

    counter = Counter()

    for a in alignments:

        if a["type"] == "replace":

            key = f"{a['hochdeutsch']} -> {a['dialekt']}"

            counter[key] += 1

    return counter


if __name__ == "__main__":

    patterns = extract_patterns()

    for p, n in patterns.most_common(40):

        print(p, n)
