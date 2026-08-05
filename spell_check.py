from spellchecker import SpellChecker


class SpellCheckerEngine:
    "Handles spell checking and word suggestions."

    def __init__(self):
        self.spell = SpellChecker()

    def check_word(self, word):
        """Checks whether a word is spelled correctly.
        Returns a dictionary with the result."""

        word = word.lower().strip()
        if not word:
            return {
                "correct": False,
                "word": word,
                "suggestion": None,
                "message": "Please enter a word."
            }

        if word in self.spell:
            return {
                "correct": True,
                "word": word,
                "suggestion": None,
                "message": "" 
            }

        suggestion = self.spell.correction(word)
        if suggestion is None or suggestion == word:
            return {
                "correct": False,
                "word": word,
                "suggestion": None,
                "message": "Word not found."
            }

        return {
            "correct": False,
            "word": word,
            "suggestion": suggestion,
            "message": ""
        }
