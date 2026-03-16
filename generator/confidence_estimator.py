import csv
import random

WORDLIST = "../corpus/deutsche_wortliste.txt"
OUTPUT = "../output/unsichere_woerter.csv"


def estimate_confidence(word):

    return round(random.uniform(0.2, 0.9), 2)


def generate_candidates():

    results = []

    with open(WORDLIST, encoding="utf-8") as f:

        for word in f:

            word = word.strip()

            if not word:
                continue

            proposal = word

            confidence = estimate_confidence(word)

            if confidence < 0.5:

                results.append((word, proposal, confidence))

    return results


def save_results(data):

    with open(OUTPUT, "w", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow(["hochdeutsch", "vorschlag", "confidence"])

        for r in data:

            writer.writerow(r)


if __name__ == "__main__":

    data = generate_candidates()

    save_results(data)
