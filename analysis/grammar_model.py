from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"


GRAMMAR_RULES = {

    "function_words": {

        "das": "des",
        "nicht": "net",
        "etwas": "ebbes",
        "auch": "aa",
        "ich": "ich",
        "wir": "mir",
        "ihr": "ihr",
        "sie": "se",
        "ist": "is",
        "sind": "sin",
        "war": "wor",
        "haben": "ham",
        "hat": "hat",
        "haben wir": "ham mir"
    },

    "verb_shortening": {

        "habe": "hab",
        "hast": "haschd",
        "haben": "ham",
        "geht": "geht",
        "gehen": "gehn",
        "kommt": "kommt",
        "kommen": "komme",
        "macht": "macht",
        "machen": "mache"

    },

    "typical_replacements": {

        "sehr": "sau",
        "wirklich": "wirklich",
        "vielleicht": "vleicht",
        "immer": "immer",
        "jetzt": "etz"

    }

}


def save_grammar_model():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    path = OUTPUT_DIR / "grammar_rules.json"

    with open(path, "w", encoding="utf-8") as f:

        json.dump(GRAMMAR_RULES, f, ensure_ascii=False, indent=2)

    print("Grammatikmodell gespeichert:")
    print(path)


if __name__ == "__main__":

    save_grammar_model()
