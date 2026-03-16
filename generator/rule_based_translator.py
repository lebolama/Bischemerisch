import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "output" / "dialect_model.json"


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


def tokenize(text):
    return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)


def apply_rules_to_word(word, rules):
    result = word.lower()

    # längere Regeln zuerst, dann höhere confidence
    sorted_rules = sorted(
        rules,
        key=lambda r: (len(r["src"]), r["confidence"]),
        reverse=True,
    )

    for rule in sorted_rules:
        src = rule["src"]
        dst = rule["dst"]

        if not src:
            continue

        if src in result:
            result = result.replace(src, dst)

    return result


def translate_word(word, model):
    clean = word.lower()
    direct_dictionary = model["direct_dictionary"]
    rules = model["rules"]

    if clean in direct_dictionary:
        translated = direct_dictionary[clean]
        return preserve_case(word, translated)

    generated = apply_rules_to_word(clean, rules)
    return preserve_case(word, generated)


def translate_sentence(text, model):
    tokens = tokenize(text)
    result = []

    for tok in tokens:
        if re.fullmatch(r"\w+", tok, flags=re.UNICODE):
            result.append(translate_word(tok, model))
        else:
            result.append(tok)

    # saubere Zeichensetzung
    out = ""
    for i, tok in enumerate(result):
        if i == 0:
            out += tok
        elif re.fullmatch(r"[,.!?;:)]", tok):
            out += tok
        elif result[i - 1] == "(":
            out += tok
        else:
            out += " " + tok
    return out


if __name__ == "__main__":
    model = load_model()
    samples = [
        "Der Apfel liegt auf dem Tisch.",
        "Ich spreche heute mit dem alten Mann.",
        "Wir gehen nach Hause und trinken Wasser.",
        "Ein einfacher Satz soll automatisch dialektisiert werden.",
    ]

    for s in samples:
        print("DE:", s)
        print("BI:", translate_sentence(s, model))
        print()
