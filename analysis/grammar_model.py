import csv
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from analysis.rule_miner import mine_rules

LOGGER = logging.getLogger(__name__)
OUTPUT_DIR = BASE_DIR / "output"
DICT_PATH = BASE_DIR / "data" / "bischemer_lexikon_master.csv"
CORPUS_PATH = BASE_DIR / "data" / "baerthel.txt"


BASE_GRAMMAR_RULES = {
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
        "haben wir": "ham mir",
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
        "machen": "mache",
    },
    "typical_replacements": {
        "sehr": "sau",
        "wirklich": "wirklich",
        "vielleicht": "vleicht",
        "immer": "immer",
        "jetzt": "etz",
    },
}

FUNCTION_WORD_CANDIDATES = {
    "ich", "du", "er", "sie", "es", "wir", "ihr", "sie",
    "mich", "dich", "uns", "euch", "mir", "dir", "ihm", "ihnen",
    "der", "die", "das", "dem", "den", "des", "ein", "eine", "einer",
    "nicht", "und", "oder", "aber", "auch", "dann", "heute", "jetzt",
    "war", "ist", "sind", "haben", "hat", "habe", "wird", "werden",
    "im", "am", "vom", "zum", "beim", "mit", "auf", "in", "an", "zu",
}

VERB_CANDIDATES = {
    "habe", "hast", "haben", "geht", "gehen", "kommt", "kommen", "macht", "machen",
    "wird", "werden", "bin", "bist", "sind", "war", "waren",
}


def load_dictionary_pairs(path=DICT_PATH):
    if not path.exists():
        raise FileNotFoundError(f"Wörterbuch nicht gefunden: {path}")

    pairs = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hd = row.get("hochdeutsch", "").strip().lower()
            bi = row.get("bischemerisch", "").strip().lower()
            if hd and bi:
                pairs.append((hd, bi))

    return pairs


def load_corpus_counter(path=CORPUS_PATH):
    if not path.exists():
        LOGGER.warning("Korpus nicht gefunden: %s", path)
        return Counter()

    with open(path, encoding="utf-8") as f:
        text = f.read().lower()

    tokens = re.findall(r"[a-zäöüß]+", text)
    return Counter(tokens)


def _collect_best_mappings(pairs, allowed_hd, corpus_counter, min_corpus_freq=2):
    mapping = defaultdict(Counter)

    for hd, bi in pairs:
        if hd not in allowed_hd:
            continue
        if corpus_counter and corpus_counter.get(bi, 0) < min_corpus_freq:
            continue
        if hd == bi:
            continue
        mapping[hd][bi] += 1

    result = {}
    for hd, counts in mapping.items():
        best_bi, _ = counts.most_common(1)[0]
        result[hd] = best_bi

    return result


def build_auto_function_words(pairs, corpus_counter):
    return _collect_best_mappings(
        pairs,
        allowed_hd=FUNCTION_WORD_CANDIDATES,
        corpus_counter=corpus_counter,
        min_corpus_freq=2,
    )


def build_auto_verb_shortening(pairs, corpus_counter):
    return _collect_best_mappings(
        pairs,
        allowed_hd=VERB_CANDIDATES,
        corpus_counter=corpus_counter,
        min_corpus_freq=2,
    )


def build_auto_typical_replacements(pairs, corpus_counter, limit=60):
    candidates = []

    for hd, bi in pairs:
        if hd == bi:
            continue
        if len(hd) < 4:
            continue
        freq = corpus_counter.get(bi, 0)
        if freq < 2:
            continue
        candidates.append((hd, bi, freq))

    candidates.sort(key=lambda x: (x[2], len(x[0])), reverse=True)

    selected = {}
    for hd, bi, _ in candidates:
        if hd in selected:
            continue
        selected[hd] = bi
        if len(selected) >= limit:
            break

    return selected


def build_auto_phonetic_rules(limit=80):
    rules = mine_rules()
    selected = []

    for rule in rules:
        src = rule["src"]
        dst = rule["dst"]

        if not src or src == dst:
            continue
        if len(src) > 4 or len(dst) > 4:
            continue
        if rule["confidence"] < 0.35:
            continue
        if rule["support"] < 8:
            continue

        selected.append(
            {
                "src": src,
                "dst": dst,
                "confidence": rule["confidence"],
                "support": rule["support"],
            }
        )

        if len(selected) >= limit:
            break

    return selected


def build_grammar_rules():
    pairs = load_dictionary_pairs()
    corpus_counter = load_corpus_counter()

    auto_function_words = build_auto_function_words(pairs, corpus_counter)
    auto_verb_shortening = build_auto_verb_shortening(pairs, corpus_counter)
    auto_typical_replacements = build_auto_typical_replacements(pairs, corpus_counter)
    auto_phonetic_rules = build_auto_phonetic_rules()

    merged = {
        "function_words": {**BASE_GRAMMAR_RULES["function_words"], **auto_function_words},
        "verb_shortening": {**BASE_GRAMMAR_RULES["verb_shortening"], **auto_verb_shortening},
        "typical_replacements": {**BASE_GRAMMAR_RULES["typical_replacements"], **auto_typical_replacements},
        "auto_phonetic_rules": auto_phonetic_rules,
        "metadata": {
            "auto_function_words": len(auto_function_words),
            "auto_verb_shortening": len(auto_verb_shortening),
            "auto_typical_replacements": len(auto_typical_replacements),
            "auto_phonetic_rules": len(auto_phonetic_rules),
        },
    }

    return merged


def save_grammar_model():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "grammar_rules.json"

    grammar_rules = build_grammar_rules()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(grammar_rules, f, ensure_ascii=False, indent=2)

    LOGGER.info("Grammatikmodell gespeichert: %s", path)
    LOGGER.info("Lernstatistik: %s", grammar_rules["metadata"])


if __name__ == "__main__":
    save_grammar_model()
