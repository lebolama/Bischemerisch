import re
from dialect_translator import translate_word, load_dictionary

dictionary = load_dictionary("../data/bischemer_lexikon_master.csv")


def tokenize(sentence):
    return re.findall(r"\w+|[^\w\s]", sentence)


def translate_sentence(sentence):

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

    s = "Der Apfel liegt auf dem Tisch."

    print("Hochdeutsch:", s)
    print("Bischemerisch:", translate_sentence(s))
