import json
import logging
from pathlib import Path

from analysis.fugenlaut_analyzer import split_compound_with_fugenlaut

LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "output" / "dialect_model.json"


def load_model(path=MODEL_PATH):
    if not path.exists():
        raise FileNotFoundError(f"Dialektmodell nicht gefunden: {path}")

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def recursive_split(word, dictionary, max_depth=10, _depth=0):
    """
    Zerlegt ein Kompositum rekursiv in möglichst viele Bestandteile.
    Schutz gegen Endlosschleifen über max_depth.
    """
    if _depth >= max_depth:
        LOGGER.debug("Maximale Rekursionstiefe erreicht für Wort: %s", word)
        return [word]

    parts = split_compound_with_fugenlaut(word, dictionary)

    if not parts:
        return [word]

    left, right = parts

    result = []
    result.extend(recursive_split(left, dictionary, max_depth=max_depth, _depth=_depth + 1))
    result.extend(recursive_split(right, dictionary, max_depth=max_depth, _depth=_depth + 1))

    return result


def _sorted_rules(model):
    rules = model.get("rules", [])
    return sorted(rules, key=lambda r: (len(r["src"]), r.get("confidence", 0)), reverse=True)


def translate_part(part, model):
    """
    Übersetzt einen einzelnen Bestandteil.
    """

    dictionary = model.get("direct_dictionary", {})
    rules = _sorted_rules(model)

    if part in dictionary:
        return dictionary[part]

    result = part

    for rule in rules:
        src = rule["src"]
        dst = rule["dst"]

        if src in result:
            result = result.replace(src, dst)

    return result


def translate_compound(word, model):
    """
    Übersetzt ein rekursiv zerlegtes Kompositum.
    Gibt None zurück, wenn keine Zerlegung möglich ist.
    """
    if not word:
        return None

    dictionary = model.get("direct_dictionary", {})

    parts = recursive_split(word.lower(), dictionary)

    if len(parts) == 1:
        return None

    translated = [translate_part(part, model) for part in parts]

    result = "".join(translated)
    LOGGER.debug("Kompositum übersetzt: %s -> %s (parts=%s)", word, result, parts)
    return result


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    model = load_model()

    test_words = [
        "Krankenhausverwaltung",
        "Straßenbahnhaltestelle",
        "Kindergartenleiter",
        "Bürgermeisteramt",
        "Winterabend",
        "Krankenhaus",
    ]

    for word in test_words:
        result = translate_compound(word, model)
        LOGGER.info("%s -> %s", word, result)


if __name__ == "__main__":
    main()
