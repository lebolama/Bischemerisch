from pathlib import Path
import json

from analysis.fugenlaut_analyzer import split_compound_with_fugenlaut


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "output" / "dialect_model.json"


def load_model():

    with open(MODEL_PATH, encoding="utf-8") as f:
        return json.load(f)


def recursive_split(word, dictionary):
    """
    Zerlegt ein Kompositum rekursiv in möglichst viele Bestandteile.
    """

    parts = split_compound_with_fugenlaut(word, dictionary)

    if not parts:
        return [word]

    left, right = parts

    result = []

    result.extend(recursive_split(left, dictionary))
    result.extend(recursive_split(right, dictionary))

    return result


def translate_part(part, model):
    """
    Übersetzt einen einzelnen Bestandteil.
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
    Übersetzt ein rekursiv zerlegtes Kompositum.
    """

    dictionary = model["direct_dictionary"]

    parts = recursive_split(word.lower(), dictionary)

    if len(parts) == 1:
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

        "Krankenhausverwaltung",
        "Straßenbahnhaltestelle",
        "Kindergartenleiter",
        "Bürgermeisteramt",
        "Winterabend",
        "Krankenhaus"

    ]

    for w in test_words:

        result = translate_compound(w, model)

        print(w, "->", result)
