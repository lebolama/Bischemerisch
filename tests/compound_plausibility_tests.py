import unittest

from analysis.compound_analyzer import recursive_split, translate_compound, translate_part
from generator.plausibility_checker import score_word, is_plausible


class CompoundAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.model = {
            "direct_dictionary": {
                "kranken": "gronk",
                "haus": "haus",
                "leiter": "laider",
                "kindergarten": "kindergadde",
            },
            "rules": [
                {"src": "ei", "dst": "ai", "confidence": 0.9},
                {"src": "ch", "dst": "sch", "confidence": 0.7},
            ],
        }

    def test_recursive_split_compound(self):
        parts = recursive_split("krankenhaus", self.model["direct_dictionary"])
        self.assertEqual(parts, ["kranken", "haus"])

    def test_translate_part_dictionary_priority(self):
        self.assertEqual(translate_part("haus", self.model), "haus")

    def test_translate_compound_success(self):
        translated = translate_compound("Krankenhaus", self.model)
        self.assertEqual(translated, "gronkhaus")

    def test_translate_compound_none_for_non_compound(self):
        translated = translate_compound("xyz", self.model)
        self.assertIsNone(translated)


class PlausibilityCheckerTests(unittest.TestCase):
    def setUp(self):
        self.model = {
            "bi": 10,
            "is": 5,
            "sch": 12,
            "er": 8,
        }

    def test_score_word(self):
        self.assertGreater(score_word("bischer", self.model), 0)

    def test_score_word_empty(self):
        self.assertEqual(score_word("", self.model), 0)

    def test_is_plausible(self):
        self.assertTrue(is_plausible("bischer", self.model, threshold=10))
        self.assertFalse(is_plausible("xx", self.model, threshold=5))


if __name__ == "__main__":
    unittest.main()
