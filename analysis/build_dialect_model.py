import json
from pathlib import Path

from analysis.rule_miner import mine_rules, load_dictionary
from analysis.phonetic_model import extract_patterns


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"


def build_direct_dictionary(pairs):
    """
    Erstellt ein Wörterbuch hochdeutsch → bischemerisch.
    Wenn mehrere Varianten existieren, wird zunächst die erste genommen.
    """

    d = {}

    for hd, bi in pairs:

        if hd not in d:
            d[hd] = bi

    return d


def serialize_rules(rules, top_n=200):
    """
    Reduziert Regeln auf ein kompaktes JSON-Format.
    """

    return [
        {
            "src": r["src"],
            "dst": r["dst"],
            "support": r["support"],
            "confidence": r["confidence"],
        }
        for r in rules[:top_n]
    ]


def serialize_phonetic_patterns(patterns, top_n=200):
    """
    Wandelt die häufigsten phonetischen Muster in ein JSON-Format um.
    """

    result = []

    for pattern, freq in patterns.most_common(top_n):

        result.append(
            {
                "pattern": pattern,
                "frequency": freq
            }
        )

    return result


def save_model_json(model, out_path):

    with open(out_path, "w", encoding="utf-8") as f:

        json.dump(model, f, ensure_ascii=False, indent=2)


def save_llm_rules_text(rules, phonetic_patterns, out_path, top_n=80):

    with open(out_path, "w", encoding="utf-8") as f:

        f.write("Büschemerisch-Regeln für LLM-Prompt\n\n")

        f.write("Nutze bekannte Wörter aus dem Wörterbuch immer bevorzugt.\n")
        f.write("Für unbekannte Wörter verwende diese statistisch erkannten Muster:\n\n")

        f.write("Orthographische Regeln:\n")

        for r in rules[:top_n]:

            f.write(
                f"- {r['src']} → {r['dst']} "
                f"(confidence={r['confidence']}, support={r['support']})\n"
            )

        f.write("\nPhonetische Muster:\n")

        for p in phonetic_patterns[:top_n]:

            f.write(
                f"- {p['pattern']} (frequency={p['frequency']})\n"
            )


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Wörterbuch laden
    pairs = load_dictionary()

    # Regeln berechnen
    rules = mine_rules()

    # phonetische Muster berechnen
    phonetic_patterns_counter = extract_patterns()

    # Wörterbuch erzeugen
    direct_dictionary = build_direct_dictionary(pairs)

    # Muster serialisieren
    phonetic_patterns = serialize_phonetic_patterns(
        phonetic_patterns_counter
    )

    model = {
        "model_name": "bischemerisch_rule_model_v2",
        "dictionary_size": len(direct_dictionary),
        "rule_count": min(len(rules), 200),
        "phonetic_pattern_count": len(phonetic_patterns),
        "direct_dictionary": direct_dictionary,
        "rules": serialize_rules(rules, top_n=200),
        "phonetic_patterns": phonetic_patterns
    }

    save_model_json(
        model,
        OUTPUT_DIR / "dialect_model.json"
    )

    save_llm_rules_text(
        rules,
        phonetic_patterns,
        OUTPUT_DIR / "llm_rules.txt"
    )

    print("Dialektmodell erzeugt:")
    print(OUTPUT_DIR / "dialect_model.json")
    print(OUTPUT_DIR / "llm_rules.txt")


if __name__ == "__main__":
    main()
