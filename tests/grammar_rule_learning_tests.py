import unittest
from collections import Counter

from analysis.grammar_model import (
    build_auto_function_words,
    build_auto_typical_replacements,
    build_auto_verb_shortening,
)


class GrammarRuleLearningTests(unittest.TestCase):
    def setUp(self):
        self.pairs = [
            ("wir", "mer"),
            ("wir", "mir"),
            ("wir", "mer"),
            ("nicht", "net"),
            ("nicht", "ned"),
            ("haben", "ham"),
            ("haben", "häwwe"),
            ("gehen", "gehn"),
            ("gehen", "gen"),
            ("kühlschrank", "kühlschroank"),
            ("nochmal", "nomool"),
        ]
        self.corpus_counter = Counter({
            "mer": 8,
            "mir": 2,
            "net": 10,
            "ham": 7,
            "gehn": 6,
            "kühlschroank": 4,
            "nomool": 3,
        })

    def test_build_auto_function_words(self):
        rules = build_auto_function_words(self.pairs, self.corpus_counter)
        self.assertEqual(rules.get("wir"), "mer")
        self.assertEqual(rules.get("nicht"), "net")

    def test_build_auto_verb_shortening(self):
        rules = build_auto_verb_shortening(self.pairs, self.corpus_counter)
        self.assertEqual(rules.get("haben"), "ham")
        self.assertEqual(rules.get("gehen"), "gehn")

    def test_build_auto_typical_replacements(self):
        rules = build_auto_typical_replacements(self.pairs, self.corpus_counter, limit=10)
        self.assertEqual(rules.get("kühlschrank"), "kühlschroank")
        self.assertEqual(rules.get("nochmal"), "nomool")


if __name__ == "__main__":
    unittest.main()
