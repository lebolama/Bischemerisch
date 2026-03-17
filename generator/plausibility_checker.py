import json
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "output" / "dialect_plausibility.json"


def load_model(path=MODEL_PATH):
    if not path.exists():
        raise FileNotFoundError(f"Plausibilitätsmodell nicht gefunden: {path}")

    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, dict) and "patterns" in raw:
        return raw["patterns"]

    # Rückwärtskompatibilität zu altem Format
    return raw


def score_word(word, model, min_ngram_len=2, max_ngram_len=4):
    if not word:
        return 0

    score = 0
    lower_word = word.lower()

    for i in range(len(lower_word)):
        for j in range(i + min_ngram_len, min(i + max_ngram_len + 1, len(lower_word) + 1)):
            part = lower_word[i:j]
            score += model.get(part, 0)

    return score


def is_plausible(word, model, threshold=50):
    word_score = score_word(word, model)
    is_ok = word_score >= threshold
    LOGGER.debug("Plausibilitätscheck %s: score=%s threshold=%s", word, word_score, threshold)
    return is_ok


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    model = load_model()
    tests = ["krankehaus", "krankenhuus", "bischemerisch", "bischemeresch"]

    for test_word in tests:
        score = score_word(test_word, model)
        LOGGER.info("%s score: %s", test_word, score)


if __name__ == "__main__":
    main()
