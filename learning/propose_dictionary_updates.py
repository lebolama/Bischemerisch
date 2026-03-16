import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT = BASE_DIR / "output" / "unsichere_woerter.csv"
OUTPUT = BASE_DIR / "output" / "dictionary_update_candidates.csv"


def load_uncertain_words():

    if not INPUT.exists():

        print("Keine unsicheren Wörter gefunden.")
        print("Datei fehlt:", INPUT)

        return []

    rows = []

    with open(INPUT, encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            try:
                score = float(row["confidence_score"])
            except:
                continue

            if score >= 0.45:

                rows.append(row)

    return rows


def save_candidates(rows):

    if not rows:

        print("Keine Wörterbuchkandidaten erzeugt.")
        return

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

    print(len(rows), "Wörterbuchkandidaten gespeichert.")
