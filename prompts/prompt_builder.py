import csv

RULES_FILE = "../output/phonetic_rules.csv"
TEMPLATE = "bischemer_prompt_template.txt"
OUTPUT = "../output/generated_prompt.txt"


def load_rules():

    rules = []

    with open(RULES_FILE, encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            rules.append(f"{row['hochdeutsch']} → {row['dialekt']}")

    return rules


def build_prompt():

    with open(TEMPLATE, encoding="utf-8") as f:

        template = f.read()

    rules = "\n".join(load_rules())

    prompt = template.replace("{{DIALEKTREGELN}}", rules)

    with open(OUTPUT, "w", encoding="utf-8") as f:

        f.write(prompt)


if __name__ == "__main__":

    build_prompt()
