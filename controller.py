from dictionary import DictionaryEngine
from spell_check import SpellCheckerEngine
from audio import AudioPlayer


class DictionaryController:

    def __init__(self, language="en"):
        self.language = language
        self.dictionary = DictionaryEngine(language)
        self.spell_check = SpellCheckerEngine()
        self.audio_player = AudioPlayer()

    def set_language(self, language_code):
        self.language = (language_code or "en").strip().lower()
        self.dictionary.set_language(self.language)

    def search(self, word):
        word = str(word or "").strip().lower()

        if not word:
            return {
                "success": False,
                "message": "Please enter a word."
            }

        spell = self.spell_check.check_word(word)

        if not spell["correct"]:
            if spell.get("suggestion"):
                return {
                    "success": False,
                    "message": f"Did you mean '{spell['suggestion']}'?"
                }
            return {
                "success": False,
                "message": spell.get("message", "Word not found.")
            }

        return self.dictionary.search_word(word)

    def pronounce(self, audio_url):
        return self.audio_player.play_audio(audio_url)
