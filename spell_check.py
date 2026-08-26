from spellchecker import SpellChecker


class SpellCheckerEngine:
    """
    Handles spell checking and word suggestions.
    """

    def __init__(self):
        self.spell = SpellChecker()

    def check_word(self, word):
        """
        Check whether a word is spelled correctly.

        Returns:
            dict: Contains the spelling result, suggestion,
                  and message.
        """

        # Safely convert the input to a string.
        word = str(word or "").strip().lower()

        # Make sure the user entered something.
        if not word:
            return {
                "correct": False,
                "word": "",
                "suggestion": None,
                "message": "Please enter a word."
            }

        try:
            # Check whether the word exists in the
            # spell checker's dictionary.
            if word in self.spell:
                return {
                    "correct": True,
                    "word": word,
                    "suggestion": None,
                    "message": ""
                }

            # Try to find the closest spelling.
            suggestion = self.spell.correction(word)

            # No useful suggestion was found.
            if not suggestion or suggestion == word:
                return {
                    "correct": False,
                    "word": word,
                    "suggestion": None,
                    "message": "Word not found."
                }

            # Return the suggested spelling.
            return {
                "correct": False,
                "word": word,
                "suggestion": suggestion,
                "message": ""
            }

        except Exception as error:
            print(f"Spell checking error: {error}")

            return {
                "correct": False,
                "word": word,
                "suggestion": None,
                "message": "Unable to check spelling."
            }
        