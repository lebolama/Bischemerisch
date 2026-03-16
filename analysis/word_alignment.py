import csv
import difflib

def load_dictionary(path):
    pairs = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pairs.append((row["hochdeutsch"], row["bischemerisch"]))
    return pairs


def align_words(pairs):
    alignments = []

    for hd, dialect in pairs:

        matcher = difflib.SequenceMatcher(None, hd, dialect)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():

            alignments.append({
                "type": tag,
                "hochdeutsch": hd[i1:i2],
                "dialekt": dialect[j1:j2]
            })

    return alignments


if __name__ == "__main__":

    pairs = load_dictionary("../data/bischemer_lexikon_master.csv")

    alignments = align_words(pairs)

    for a in alignments[:50]:
        print(a)
