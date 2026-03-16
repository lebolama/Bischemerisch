import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT = BASE_DIR / "output" / "unsichere_woerter.csv"
OUTPUT = BASE_DIR / "output" / "dictionary_update_candidates.csv"


def load_uncertain_words():

    rows = []

    with open(INPUT, encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            score = float(row["confidence_score"])

            if score >= 0.45:  # nur halbwegs plausible Vorschläge

                rows.append(row)

    return rows


def save_candidates(rows):

    with open(OUTPUT, "w", encoding="utf-8", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "hochdeutsch",
            "vorschlag_bischemerisch",
            "confidence_score",
            "status"
        ])

        for r in rows:

            writer.writerow([
                r["hochdeutsch"],
                r["vorschlag_bischemerisch"],
                r["confidence_score"],
                "review"
            ])


if __name__ == "__main__":

    rows = load_uncertain_words()

    save_candidates(rows)

    print(len(rows), "Kandidaten gespeichert in")

    print(OUTPUT)
