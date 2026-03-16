import logging

from analysis.phonetic_patterns import extract_patterns


def generate_rules():

    patterns = extract_patterns()

    rules = []

    for pattern, count in patterns.items():

        if count > 10:

            rules.append(pattern)

    return rules


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    rules = generate_rules()

    for rule in rules:
        logging.info("%s", rule)
