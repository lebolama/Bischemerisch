import json
import logging
import re
from pathlib import Path

from analysis.compound_analyzer import translate_compound

LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "output" / "dialect_model.json"
GRAMMAR_PATH = BASE_DIR / "output" / "grammar_rules.json"

_GRAMMAR_CACHE = None


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Dialektmodell fehlt: {MODEL_PATH}")

    with open(MODEL_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_grammar():
    if not GRAMMAR_PATH.exists():
        raise FileNotFoundError(f"Grammatikmodell fehlt: {GRAMMAR_PATH}")

    with open(GRAMMAR_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_grammar():
    global _GRAMMAR_CACHE
    if _GRAMMAR_CACHE is None:
        _GRAMMAR_CACHE = load_grammar()
    return _GRAMMAR_CACHE


def preserve_case(source, target):
    if not source:
        return target
    if source.isupper():
        return target.upper()
    if source[0].isupper():
        return target[:1].upper() + target[1:]
    return target


def tokenize(text):
    return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)


def apply_rules_to_word(word, rules):
    result = word.lower()

    sorted_rules = sorted(
        rules,
        key=lambda r: (len(r["src"]), r["confidence"]),
        reverse=True,
    )

    for rule in sorted_rules:
        src = rule["src"]
        dst = rule["dst"]

        if not src:
            continue

        if src in result:
            result = result.replace(src, dst)

    return result


def apply_corpus_guided_rewrites(word, model):
    rewrites = model.get("corpus_guided_rewrites", [])
    if not rewrites:
        return word

    result = word
    for rewrite in rewrites:
        src = rewrite.get("src", "")
        dst = rewrite.get("dst", "")
        if not src or src == dst:
            continue
        if src in result:
            result = result.replace(src, dst)

    return result


def translate_word(word, model):
    clean = word.lower()

    direct_dictionary = model["direct_dictionary"]
    rules = model["rules"]

    # 1 Wörterbuch
    if clean in direct_dictionary:
        translated = direct_dictionary[clean]
        return preserve_case(word, translated)

    # 2 Kompositum
    compound = translate_compound(clean, model)
    if compound:
        return preserve_case(word, compound)

    # 3 Regelbasierte Umformung
    generated = apply_rules_to_word(clean, rules)

    # 4 Zusätzliche korpusgestützte Dialektmuster
    generated = apply_corpus_guided_rewrites(generated, model)

    return preserve_case(word, generated)




def apply_auto_phonetic_rules(word, grammar):
    rules = grammar.get("auto_phonetic_rules", [])
    if not rules:
        return word

    result = word
    for rule in rules:
        src = rule.get("src", "")
        dst = rule.get("dst", "")
        if not src or src == dst:
            continue
        if src in result:
            result = result.replace(src, dst)

    return result

def apply_grammar_rules(text):
    grammar = get_grammar()

    function_words = grammar.get("function_words", {})
    verb_shortening = grammar.get("verb_shortening", {})
    typical_replacements = grammar.get("typical_replacements", {})

    # zuerst Mehrwortregeln
    for src, dst in function_words.items():
        if " " in src:
            text = re.sub(rf"\b{re.escape(src)}\b", dst, text, flags=re.IGNORECASE)

    words = text.split()
    result = []

    for w in words:
        lw = w.lower()

        if lw in function_words:
            result.append(function_words[lw])
            continue

        if lw in verb_shortening:
            result.append(verb_shortening[lw])
            continue

        if lw in typical_replacements:
            result.append(typical_replacements[lw])
            continue

        result.append(apply_auto_phonetic_rules(w, grammar))

    return " ".join(result)


def translate_sentence(text, model):
    tokens = tokenize(text)
    result = []

    for tok in tokens:
        if re.fullmatch(r"\w+", tok, flags=re.UNICODE):
            result.append(translate_word(tok, model))
        else:
            result.append(tok)

    # Zeichensetzung korrekt zusammensetzen
    out = ""

    for i, tok in enumerate(result):
        if i == 0:
            out += tok
        elif re.fullmatch(r"[,.!?;:)]", tok):
            out += tok
        elif result[i - 1] == "(":
            out += tok
        else:
            out += " " + tok

    # Grammatikregeln anwenden
    out = apply_grammar_rules(out)

    return out


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    model = load_model()
    samples = [
        "Der Apfel liegt auf dem Tisch.",
        "Ich habe das heute gesehen.",
        "Wir gehen nach Hause.",
        "Das Krankenhaus steht am Stadtrand.",
        "Der Bürgermeister besucht das Rathaus.",
        "Der Kindergartenleiter spricht mit den Eltern.",
    ]

    for sample in samples:
        LOGGER.info("DE: %s", sample)
        LOGGER.info("BI: %s", translate_sentence(sample, model))


if __name__ == "__main__":
    main()
