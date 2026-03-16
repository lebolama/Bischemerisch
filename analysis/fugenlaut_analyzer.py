from pathlib import Path


FUGENLAUTE = [
    "s",
    "n",
    "en",
    "er",
    "es"
]


def split_compound_with_fugenlaut(word, dictionary):
    """
    Versucht ein Kompositum zu zerlegen, auch wenn ein Fugenlaut vorhanden ist.
    """

    word = word.lower()

    for i in range(3, len(word) - 2):

        left = word[:i]
        right = word[i:]

        # Fall 1: direkte Zerlegung
        if left in dictionary and right in dictionary:
            return [left, right]

        # Fall 2: Fugenlaut prüfen
        for f in FUGENLAUTE:

            if right.startswith(f):

                right_without = right[len(f):]

                if left in dictionary and right_without in dictionary:

                    return [left, right_without]

    return None
