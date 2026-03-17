import csv
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from generator.novel_word_generator import generate_candidate, load_model

LOGGER = logging.getLogger(__name__)

WORDLIST = BASE_DIR / "corpus" / "deutsche_wortliste.txt"
OUTPUT = BASE_DIR / "output" / "unsichere_woerter.csv"


def score_candidate(input_word, candidate, applied_rules):
    """
    Heuristische Unsicherheitsbewertung.
    Hoher Score = relativ plausibel
    Niedriger Score = eher unsicher
    """

    if not input_word:
        return 0.0

    if not applied_rules:
        # wenn keine Regel angewendet wurde, ist es entweder bekannt
        # oder praktisch unverändert geblieben -> meist unsicher
        if input_word.lower() == candidate.lower():
            return 0.15
        return 0.45

    avg_conf = sum(r["confidence"] for r in applied_rules) / len(applied_rules)
    avg_support = sum(r["support"] for r in applied_rules) / len(applied_rules)

    # Normierung grob auf 0..1
    support_factor = min(avg_support / 50, 1.0)

    # Je mehr Regeln greifen, desto besser – aber nur bis zu einem Punkt
    coverage_factor = min(len(applied_rules) / 4, 1.0)

    # Wenn sich das Wort stark verändert hat, ist das oft ein gutes Zeichen,
    # solange die Regeln stark sind
    changed = input_word.lower() != candidate.lower()
    change_factor = 1.0 if changed else 0.3

    score = (
        0.45 * avg_conf
        + 0.25 * support_factor
        + 0.20 * coverage_factor
        + 0.10 * change_factor
    )

    return round(max(0.0, min(score, 1.0)), 3)


def classify_confidence(score):
    if score >= 0.75:
        return "hoch"
    if score >= 0.50:
        return "mittel"
    return "niedrig"


def load_wordlist(path=WORDLIST):
    if not path.exists():
        raise FileNotFoundError(f"Wortliste nicht gefunden: {path}")

    words = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            word = line.strip()
            if word:
                words.append(word)
    return words


def generate_uncertain_words(model, threshold=0.50):
    rows = []
    for word in load_wordlist():
        result = generate_candidate(word, model)

        if result["known_word"]:
            continue

        score = score_candidate(
            result["input_word"],
            result["candidate"],
            result["applied_rules"],
        )

        label = classify_confidence(score)

        if score < threshold:
            rows.append({
                "hochdeutsch": result["input_word"],
                "vorschlag_bischemerisch": result["candidate"],
                "confidence_score": score,
                "confidence_label": label,
                "applied_rule_count": len(result["applied_rules"]),
                "applied_rules": result["applied_rules"],
            })

    return rows


def save_results(rows, out_path=OUTPUT):
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "hochdeutsch",
            "vorschlag_bischemerisch",
            "confidence_score",
            "confidence_label",
            "applied_rule_count",
            "applied_rules",
        ])

        for row in rows:
            rules_str = " | ".join(
                f"{r['src']}->{r['dst']} (conf={r['confidence']}, support={r['support']}, n={r['count']})"
                for r in row["applied_rules"]
            )
            writer.writerow([
                row["hochdeutsch"],
                row["vorschlag_bischemerisch"],
                row["confidence_score"],
                row["confidence_label"],
                row["applied_rule_count"],
                rules_str,
            ])


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    model = load_model()
    rows = generate_uncertain_words(model, threshold=0.50)
    save_results(rows)

    LOGGER.info("%s unsichere Wörter gespeichert unter: %s", len(rows), OUTPUT)

    for row in rows[:20]:
        LOGGER.info(
            "%s -> %s | score: %s | label: %s",
            row["hochdeutsch"],
            row["vorschlag_bischemerisch"],
            row["confidence_score"],
            row["confidence_label"],
        )


if __name__ == "__main__":
    main()
