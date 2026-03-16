import csv
import json
from pathlib import Path
from rule_miner import mine_rules, load_dictionary

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"


def build_direct_dictionary(pairs):
    """
    Wörterbuch hochdeutsch -> häufigste bekannte bischemerische Form.
    Falls mehrere Varianten existieren, wird zunächst einfach die erste genommen.
    Das kann später noch verfeinert werden.
    """
    d = {}
    for hd, bi in pairs:
        if hd not in d:
            d[hd] = bi
    return d


def serialize_rules(rules, top_n=200):
    return [
        {
            "src": r["src"],
            "dst": r["dst"],
            "support": r["support"],
            "confidence": r["confidence"],
        }
        for r in rules[:top_n]
    ]


def save_model_json(model, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=False, indent=2)


def save_llm_rules_text(rules, out_path, top_n=80):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Büschemerisch-Regeln für LLM-Prompt\n\n")
        f.write("Nutze bekannte Wörter aus dem Wörterbuch immer bevorzugt.\n")
        f.write("Für unbekannte Wörter verwende diese statistisch erkannten Muster:\n\n")
        for r in rules[:top_n]:
            f.write(
                f"- {r['src']} → {r['dst']} "
                f"(confidence={r['confidence']}, support={r['support']})\n"
            )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pairs = load_dictionary()
    rules = mine_rules()
    direct_dictionary = build_direct_dictionary(pairs)

    model = {
        "model_name": "bischemerisch_rule_model_v1",
        "dictionary_size": len(direct_dictionary),
        "rule_count": min(len(rules), 200),
        "direct_dictionary": direct_dictionary,
        "rules": serialize_rules(rules, top_n=200),
    }

    save_model_json(model, OUTPUT_DIR / "dialect_model.json")
    save_llm_rules_text(rules, OUTPUT_DIR / "llm_rules.txt")

    print("Dialektmodell erzeugt:")
    print(OUTPUT_DIR / "dialect_model.json")
    print(OUTPUT_DIR / "llm_rules.txt")


if __name__ == "__main__":
    main()
