import json
import re
from pathlib import Path

from analysis.compound_analyzer import translate_compound


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "output" / "dialect_model.json"
GRAMMAR_PATH = BASE_DIR / "output" / "grammar_rules.json"


def load_model():

    with open(MODEL_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_grammar():

    with open(GRAMMAR_PATH, encoding="utf-8") as f:
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

    sorted_rules = sorted(
        rules,
        key=lambda r: (len(r["src"]), r["confidence"]),
        reverse=True
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

    # 1 Wörterbuch
    if clean in direct_dictionary:

        translated = direct_dictionary[clean]

        return preserve_case(word, translated)

    # 2 Kompositum
    compound = translate_compound(clean, model)

    if compound:

        return preserve_case(word, compound)

    # 3 Regelbasierte Umformung
    generated = apply_rules_to_word(clean, rules)

    return preserve_case(word, generated)


def apply_grammar_rules(text):

    grammar = load_grammar()

    words = text.split()

    result = []

    for w in words:

        lw = w.lower()

        if lw in grammar["function_words"]:

            result.append(grammar["function_words"][lw])
            continue

        if lw in grammar["verb_shortening"]:

            result.append(grammar["verb_shortening"][lw])
            continue

        if lw in grammar["typical_replacements"]:

            result.append(grammar["typical_replacements"][lw])
            continue

        result.append(w)

    return " ".join(result)


def translate_sentence(text, model):

    tokens = tokenize(text)

    result = []

    for tok in tokens:

        if re.fullmatch(r"\w+", tok, flags=re.UNICODE):

            result.append(
                translate_word(tok, model)
            )

        else:

            result.append(tok)

    # Zeichensetzung korrekt zusammensetzen
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

    # Grammatikregeln anwenden
    out = apply_grammar_rules(out)

    return out


if __name__ == "__main__":

    model = load_model()

    samples = [

        "Der Apfel liegt auf dem Tisch.",
        "Ich habe das heute gesehen.",
        "Wir gehen nach Hause.",
        "Das Krankenhaus steht am Stadtrand.",
        "Der Bürgermeister besucht das Rathaus.",
        "Der Kindergartenleiter spricht mit den Eltern."

    ]

    for s in samples:

        print("DE:", s)
        print("BI:", translate_sentence(s, model))
        print()
