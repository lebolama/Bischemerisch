import csv
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "output" / "dialect_model.json"
OUTPUT_PATH = BASE_DIR / "output" / "generated_candidates.csv"


def load_model(path=MODEL_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def preserve_case(source, target):
    if not source:
        return target
    if source.isupper():
        return target.upper()
    if source[0].isupper():
        return target[:1].upper() + target[1:]
    return target


def apply_rules_verbose(word, rules):
    """
    Wendet Regeln auf ein Wort an und protokolliert,
    welche Regeln tatsächlich gegriffen haben.
    """
    result = word.lower()
    applied = []

    sorted_rules = sorted(
        rules,
        key=lambda r: (len(r["src"]), r["confidence"], r["support"]),
        reverse=True,
    )

    for rule in sorted_rules:
        src = rule["src"]
        dst = rule["dst"]

        if not src:
            continue

        if src in result:
            occurrences_before = result.count(src)
            new_result = result.replace(src, dst)
            if new_result != result:
                applied.append({
                    "src": src,
                    "dst": dst,
                    "confidence": rule["confidence"],
                    "support": rule["support"],
                    "count": occurrences_before,
                })
                result = new_result

    return result, applied


def generate_candidate(word, model):
    """
    Erzeugt für ein unbekanntes Wort eine plausible büschemerische Form.
    """
    direct_dictionary = model["direct_dictionary"]
    rules = model["rules"]

    clean = word.lower()

    if clean in direct_dictionary:
        return {
            "input_word": word,
            "candidate": preserve_case(word, direct_dictionary[clean]),
            "known_word": True,
            "applied_rules": [],
        }

    candidate, applied_rules = apply_rules_verbose(clean, rules)

    return {
        "input_word": word,
        "candidate": preserve_case(word, candidate),
        "known_word": False,
        "applied_rules": applied_rules,
    }


def tokenize_words(text):
    return re.findall(r"\w+", text, flags=re.UNICODE)


def save_candidates(rows, out_path=OUTPUT_PATH):
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "hochdeutsch",
            "vorschlag_bischemerisch",
            "known_word",
            "applied_rule_count",
            "applied_rules",
        ])
        for row in rows:
            rules_str = " | ".join(
                f"{r['src']}->{r['dst']} (conf={r['confidence']}, support={r['support']}, n={r['count']})"
                for r in row["applied_rules"]
            )
            writer.writerow([
                row["input_word"],
                row["candidate"],
                row["known_word"],
                len(row["applied_rules"]),
                rules_str,
            ])


if __name__ == "__main__":
    model = load_model()

    sample_words = [
        "Krankenhaus",
        "Telefon",
        "Messer",
        "Schmetterling",
        "arbeiten",
        "Bürgermeister",
        "Fensterladen",
        "Sommerabend",
    ]

    results = [generate_candidate(w, model) for w in sample_words]
    save_candidates(results)

    for row in results:
        print(row["input_word"], "->", row["candidate"])
        if row["known_word"]:
            print("  bekanntes Wort aus Wörterbuch")
        else:
            print("  angewendete Regeln:", len(row["applied_rules"]))
            for r in row["applied_rules"][:5]:
                print(
                    f"   - {r['src']} -> {r['dst']} "
                    f"(conf={r['confidence']}, support={r['support']}, n={r['count']})"
                )
        print()
