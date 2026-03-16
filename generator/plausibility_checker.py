import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

MODEL_PATH = BASE_DIR / "output" / "dialect_plausibility.json"


def load_model():

    with open(MODEL_PATH, encoding="utf-8") as f:
        return json.load(f)


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

    model = load_model()

    tests = [

        "krankehaus",
        "krankenhuus",
        "bischemerisch",
        "bischemeresch"

    ]

    for t in tests:

        score = score_word(t, model)

        print(t, "score:", score)
