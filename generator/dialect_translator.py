import csv


def load_dictionary(path):

    dictionary = {}

    with open(path, encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            dictionary[row["hochdeutsch"].lower()] = row["bischemerisch"]

    return dictionary


def translate_word(word, dictionary):

    w = word.lower()

    if w in dictionary:
        return dictionary[w]

    return word


def translate_sentence(sentence, dictionary):

    words = sentence.split()

    result = []

    for w in words:

        result.append(translate_word(w, dictionary))

    return " ".join(result)


if __name__ == "__main__":

    dictionary = load_dictionary("../data/bischemer_lexikon_master.csv")

    s = "Der Apfel ist rot"

    print(translate_sentence(s, dictionary))
