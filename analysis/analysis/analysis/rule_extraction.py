from phonetic_patterns import extract_patterns


def generate_rules():

    patterns = extract_patterns()

    rules = []

    for pattern, count in patterns.items():

        if count > 10:

            rules.append(pattern)

    return rules


if __name__ == "__main__":

    rules = generate_rules()

    for r in rules:

        print(r)
