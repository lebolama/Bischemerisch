import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REVIEW = BASE_DIR / "output" / "dictionary_updates_review.csv"
DICTIONARY = BASE_DIR / "data" / "bischemer_lexikon_master.csv"


def load_dictionary():

    rows = []

    with open(DICTIONARY, encoding="utf-8") as f:

        reader = csv.reader(f)

        for r in reader:

            rows.append(r)

    return rows


def load_approved():

    approved = []

    with open(REVIEW, encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for r in reader:

            if r["approve"].lower() == "yes":

                approved.append(
                    (r["hochdeutsch"], r["bischemerisch"])
                )

    return approved


def save_dictionary(rows):

    with open(DICTIONARY, "w", encoding="utf-8", newline="") as f:

        writer = csv.writer(f)

        for r in rows:

            writer.writerow(r)


if __name__ == "__main__":

    dictionary = load_dictionary()

    approved = load_approved()

    for a in approved:

        dictionary.append(list(a))

    save_dictionary(dictionary)

    print(len(approved), "neue Wörter ins Wörterbuch übernommen.")
