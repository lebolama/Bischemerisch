from analysis.compound_analyzer import translate_compound
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "output" / "dialect_model.json"


def load_model():

    with open(MODEL_PATH, encoding="utf-8") as f:
        return json.load(f)


model = load_model()

tests = [

    "Kindergarten",
    "Straßenlampe",
    "Arbeitsamt",
    "Herzarzt",
    "Winterabend",
    "Krankenhaus"

]

for t in tests:

    result = translate_compound(t, model)

    print(t, "->", result)
