from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
GENERATOR_DIR = BASE_DIR / "generator"
sys.path.insert(0, str(GENERATOR_DIR))

from novel_word_generator import load_model, generate_candidate
from confidence_estimator import score_candidate, classify_confidence


def run_tests():
    model = load_model()

    test_words = [
        "Telefon",
        "Krankenhaus",
        "Winterabend",
        "Malermeister",
        "Schlüssel",
        "Zahnarzt",
        "Bürgerhaus",
        "Schneefall",
        "Kleiderkasten",
        "Wanderweg",
    ]

    for word in test_words:
        result = generate_candidate(word, model)
        score = score_candidate(
            result["input_word"],
            result["candidate"],
            result["applied_rules"],
        )
        label = classify_confidence(score)

        print("DE:", result["input_word"])
        print("BI:", result["candidate"])
        print("Bekannt:", result["known_word"])
        print("Score:", score, "| Klasse:", label)

        if result["applied_rules"]:
            print("Regeln:")
            for r in result["applied_rules"][:8]:
                print(
                    f"  - {r['src']} -> {r['dst']} "
                    f"(conf={r['confidence']}, support={r['support']}, n={r['count']})"
                )
        print("-" * 50)


if __name__ == "__main__":
    run_tests()
