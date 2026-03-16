import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "output" / "dialect_model.json"
TEMPLATE_PATH = BASE_DIR / "prompts" / "bischemer_prompt_template.txt"
OUTPUT_PATH = BASE_DIR / "output" / "generated_prompt.txt"


def load_model():
    with open(MODEL_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_rules_section(rules, limit=60):
    lines = []
    for r in rules[:limit]:
        lines.append(
            f"- {r['src']} → {r['dst']} "
            f"(confidence={r['confidence']}, support={r['support']})"
        )
    return "\n".join(lines)


def build_dictionary_examples(direct_dictionary, limit=40):
    items = list(direct_dictionary.items())[:limit]
    lines = [f"- {hd} → {bi}" for hd, bi in items]
    return "\n".join(lines)


def main():
    model = load_model()

    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = f.read()

    prompt = template
    prompt = prompt.replace("{{DIALEKTREGELN}}", build_rules_section(model["rules"]))
    prompt = prompt.replace("{{WÖRTERBUCHBEISPIELE}}", build_dictionary_examples(model["direct_dictionary"]))

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"Prompt gespeichert unter: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
