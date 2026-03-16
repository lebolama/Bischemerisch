from pathlib import Path
import json

from analysis.fugenlaut_analyzer import split_compound_with_fugenlaut


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "output" / "dialect_model.json"


def load_model():

    with open(MODEL_PATH, encoding="utf-8") as f:
        return json.load(f)


def split_compound(word, dictionary):
    """
    Zerlegt ein deutsches Kompositum mithilfe des
    Fugenlaut-Analyzers.
    """

    parts = split_compound_with_fugenlaut(word, dictionary)

    return parts


def translate_part(part, model):
    """
    Übersetzt einen einzelnen Bestandteil eines Kompositums.
    """

    dictionary = model["direct_dictionary"]
    rules = model["rules"]

    if part in dictionary:
        return dictionary[part]

    result = part

    for r in rules:

        src = r["src"]
        dst = r["dst"]

        if src in result:
            result = result.replace(src, dst)

    return result


def translate_compound(word, model):
    """
    Versucht ein Kompositum zu übersetzen.
    """

    dictionary = model["direct_dictionary"]

    parts = split_compound(word, dictionary)

    if not parts:
        return None

    translated = []

    for p in parts:

        translated.append(
            translate_part(p, model)
        )

    return "".join(translated)


if __name__ == "__main__":

    model = load_model()

    test_words = [

        "Krankenhaus",
        "Winterabend",
        "Straßenlampe",
        "Kindergarten",
        "Bürgermeister",
        "Arbeitsamt",
        "Herzarzt"

    ]

    for w in test_words:

        result = translate_compound(w, model)

        print(w, "->", result)
