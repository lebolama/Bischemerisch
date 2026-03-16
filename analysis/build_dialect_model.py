import json
import re
import sys
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from analysis.phonetic_model import extract_patterns
from analysis.rule_miner import load_dictionary, mine_rules
OUTPUT_DIR = BASE_DIR / "output"
CORPUS_PATH = BASE_DIR / "data" / "baerthel.txt"


def build_direct_dictionary(pairs):
    dictionary = {}
    for hd, bi in pairs:
        if hd not in dictionary:
            dictionary[hd] = bi
    return dictionary


def serialize_rules(rules, top_n=200):
    return [
        {
            "src": r["src"],
            "dst": r["dst"],
            "support": r["support"],
            "confidence": r["confidence"],
        }
        for r in rules[:top_n]
    ]


def serialize_phonetic_patterns(patterns, top_n=200):
    result = []
    for pattern, freq in patterns.most_common(top_n):
        result.append({"pattern": pattern, "frequency": freq})
    return result


def _tokenize(text):
    return re.findall(r"[a-zäöüß]+", text.lower())


def _substring_counter(words, min_len=2, max_len=4):
    counter = Counter()
    for word in words:
        for i in range(len(word)):
            for j in range(i + min_len, min(i + max_len + 1, len(word) + 1)):
                counter[word[i:j]] += 1
    return counter


def extract_corpus_signature_patterns(pairs, top_n=80, min_corpus_freq=15):
    if not CORPUS_PATH.exists():
        return []

    with open(CORPUS_PATH, encoding="utf-8") as f:
        corpus_tokens = _tokenize(f.read())

    corpus_counter = _substring_counter(corpus_tokens)
    hd_words = [hd for hd, _ in pairs]
    hd_counter = _substring_counter(hd_words)

    scored = []
    for pattern, corpus_freq in corpus_counter.items():
        if corpus_freq < min_corpus_freq:
            continue
        hd_freq = hd_counter.get(pattern, 0)
        ratio = corpus_freq / (hd_freq + 1)
        if ratio >= 2.0:
            scored.append(
                {
                    "pattern": pattern,
                    "corpus_frequency": corpus_freq,
                    "hochdeutsch_frequency": hd_freq,
                    "ratio": round(ratio, 3),
                }
            )

    scored.sort(key=lambda item: (item["ratio"], item["corpus_frequency"], len(item["pattern"])), reverse=True)
    return scored[:top_n]


def build_corpus_guided_rewrites(rules, signature_patterns, top_n=40):
    signatures = {item["pattern"]: item["ratio"] for item in signature_patterns}
    rewrites = []

    for rule in rules:
        src = rule["src"]
        dst = rule["dst"]

        if len(src) < 2 or len(dst) < 2:
            continue
        if rule["confidence"] < 0.35 or rule["support"] < 8:
            continue

        signature_score = max((score for pattern, score in signatures.items() if pattern in dst), default=0.0)
        if signature_score <= 0:
            continue

        rewrites.append(
            {
                "src": src,
                "dst": dst,
                "support": rule["support"],
                "confidence": rule["confidence"],
                "signature_score": round(signature_score, 3),
            }
        )

    rewrites.sort(
        key=lambda item: (
            item["signature_score"],
            item["confidence"],
            item["support"],
            len(item["src"]),
        ),
        reverse=True,
    )

    # Deduplicate by src to keep strongest rewrite per source fragment.
    selected = []
    seen_src = set()
    for item in rewrites:
        if item["src"] in seen_src:
            continue
        seen_src.add(item["src"])
        selected.append(item)
        if len(selected) >= top_n:
            break

    return selected


def save_model_json(model, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=False, indent=2)


def save_llm_rules_text(rules, phonetic_patterns, corpus_signatures, out_path, top_n=80):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Büschemerisch-Regeln für LLM-Prompt\n\n")
        f.write("Nutze bekannte Wörter aus dem Wörterbuch immer bevorzugt.\n")
        f.write("Für unbekannte Wörter verwende diese statistisch erkannten Muster:\n\n")

        f.write("Orthographische Regeln:\n")
        for rule in rules[:top_n]:
            f.write(
                f"- {rule['src']} → {rule['dst']} "
                f"(confidence={rule['confidence']}, support={rule['support']})\n"
            )

        f.write("\nPhonetische Muster:\n")
        for pattern in phonetic_patterns[:top_n]:
            f.write(f"- {pattern['pattern']} (frequency={pattern['frequency']})\n")

        f.write("\nDialekt-Signaturen aus dem Korpus:\n")
        for item in corpus_signatures[:40]:
            f.write(
                f"- {item['pattern']} "
                f"(corpus={item['corpus_frequency']}, hd={item['hochdeutsch_frequency']}, ratio={item['ratio']})\n"
            )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pairs = load_dictionary()
    rules = mine_rules()
    phonetic_patterns_counter = extract_patterns()

    direct_dictionary = build_direct_dictionary(pairs)
    phonetic_patterns = serialize_phonetic_patterns(phonetic_patterns_counter)

    corpus_signatures = extract_corpus_signature_patterns(pairs)
    corpus_guided_rewrites = build_corpus_guided_rewrites(rules, corpus_signatures)

    model = {
        "model_name": "bischemerisch_rule_model_v3",
        "dictionary_size": len(direct_dictionary),
        "rule_count": min(len(rules), 200),
        "phonetic_pattern_count": len(phonetic_patterns),
        "corpus_signature_count": len(corpus_signatures),
        "corpus_rewrite_count": len(corpus_guided_rewrites),
        "direct_dictionary": direct_dictionary,
        "rules": serialize_rules(rules, top_n=200),
        "phonetic_patterns": phonetic_patterns,
        "corpus_signatures": corpus_signatures,
        "corpus_guided_rewrites": corpus_guided_rewrites,
    }

    save_model_json(model, OUTPUT_DIR / "dialect_model.json")
    save_llm_rules_text(rules, phonetic_patterns, corpus_signatures, OUTPUT_DIR / "llm_rules.txt")

    print("Dialektmodell erzeugt:")
    print(OUTPUT_DIR / "dialect_model.json")
    print(OUTPUT_DIR / "llm_rules.txt")


if __name__ == "__main__":
    main()
