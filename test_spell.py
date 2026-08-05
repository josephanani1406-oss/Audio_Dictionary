import unittest

from spell_check import SpellCheckerEngine


class TestSpellCheckerEngine(unittest.TestCase):
    def setUp(self):
        self.checker = SpellCheckerEngine()

    def test_correct_word(self):
        result = self.checker.check_word("hello")
        self.assertTrue(result["correct"])
        self.assertIsNone(result["suggestion"])

    def test_misspelled_word_returns_suggestion(self):
        result = self.checker.check_word("teh")
        self.assertFalse(result["correct"])
        self.assertIsNotNone(result["suggestion"])

    def test_empty_word_is_invalid(self):
        result = self.checker.check_word("   ")
        self.assertFalse(result["correct"])
        self.assertEqual(result["message"], "Please enter a word.")


if __name__ == "__main__":
    unittest.main()
