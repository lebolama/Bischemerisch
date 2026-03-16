import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT = BASE_DIR / "output" / "dictionary_update_candidates.csv"
OUTPUT = BASE_DIR / "output" / "dictionary_updates_review.csv"


def prepare_review():

    rows = []

    with open(INPUT, encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for r in reader:

            rows.append({
                "hochdeutsch": r["hochdeutsch"],
                "bischemerisch": r["vorschlag_bischemerisch"],
                "confidence": r["confidence_score"],
                "approve": ""
            })

    return rows


def save_review(rows):

    with open(OUTPUT, "w", encoding="utf-8", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "hochdeutsch",
            "bischemerisch",
            "confidence",
            "approve"
        ])

        for r in rows:

            writer.writerow([
                r["hochdeutsch"],
                r["bischemerisch"],
                r["confidence"],
                r["approve"]
            ])


if __name__ == "__main__":

    rows = prepare_review()

    save_review(rows)

    print("Review-Datei erstellt:")
    print(OUTPUT)
