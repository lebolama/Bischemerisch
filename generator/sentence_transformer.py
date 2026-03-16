import logging
import re
from pathlib import Path

from generator.dialect_translator import translate_word, load_dictionary

BASE_DIR = Path(__file__).resolve().parent.parent
DICTIONARY_PATH = BASE_DIR / "data" / "bischemer_lexikon_master.csv"


def tokenize(sentence):
    return re.findall(r"\w+|[^\w\s]", sentence)


def translate_sentence(sentence):

    dictionary = load_dictionary(DICTIONARY_PATH)
    tokens = tokenize(sentence)

    result = []

    for t in tokens:

        if re.match(r"\w+", t):

            translated = translate_word(t, dictionary)

            result.append(translated)

        else:
            result.append(t)

    return " ".join(result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    s = "Der Apfel liegt auf dem Tisch."
    logging.info("Hochdeutsch: %s", s)
    logging.info("Bischemerisch: %s", translate_sentence(s))
