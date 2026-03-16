import json
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "output" / "dialect_plausibility.json"


def load_model():

    with open(MODEL_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, dict) and "patterns" in raw:
        return raw["patterns"]

    # Rückwärtskompatibilität zu altem Format
    return raw


def score_word(word, model):

    score = 0

    for i in range(len(word)):

        for j in range(i + 2, min(i + 5, len(word))):

            part = word[i:j]

            if part in model:

                score += model[part]

    return score


def is_plausible(word, model, threshold=50):

    return score_word(word, model) >= threshold


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    model = load_model()
    tests = ["krankehaus", "krankenhuus", "bischemerisch", "bischemeresch"]

    for test_word in tests:
        score = score_word(test_word, model)
        logging.info("%s score: %s", test_word, score)
