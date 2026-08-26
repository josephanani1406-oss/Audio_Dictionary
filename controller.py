from dictionary import DictionaryEngine
from spell_check import SpellCheckerEngine
from audio import AudioPlayer
from history import HistoryManager


class DictionaryController:
    """Application controller for dictionary, audio, history and learning."""

    def __init__(self, language="en"):
        self.language = (language or "en").strip().lower()
        self.dictionary = DictionaryEngine(self.language)
        self.spell_check = SpellCheckerEngine()
        self.audio_player = AudioPlayer()
        self.history_manager = HistoryManager()

    def set_language(self, language_code):
        self.language = (language_code or "en").strip().lower()
        self.dictionary.set_language(self.language)

    def search(self, word):
        word = str(word or "").strip().lower()
        if not word:
            return {"success": False, "message": "Please enter a word."}
        spell = self.spell_check.check_word(word)
        if not spell["correct"]:
            if spell.get("suggestion"):
                return {"success": False, "message": f"Did you mean '{spell['suggestion']}'?"}
            return {"success": False, "message": spell.get("message", "Word not found.")}
        result = self.dictionary.search_word(word)
        if result.get("success"):
            self.history_manager.add_search(word)
        return result

    def pronounce(self, audio_url):
        return self.audio_player.play_audio(audio_url)

    def get_history(self): return self.history_manager.get_history()
    def clear_history(self): self.history_manager.clear_history()
    def add_favorite(self, word): self.history_manager.add_favorite(word)
    def remove_favorite(self, word): self.history_manager.remove_favorite(word)
    def is_favorite(self, word): return self.history_manager.is_favorite(word)
    def get_favorites(self): return self.history_manager.get_favorites()
    def clear_favorites(self): self.history_manager.clear_favorites()
    def add_note(self, word, note): self.history_manager.add_note(word, note)
    def get_note(self, word): return self.history_manager.get_note(word)
    def mark_learned(self, word): self.history_manager.mark_learned(word)
    def unmark_learned(self, word): self.history_manager.unmark_learned(word)
    def is_learned(self, word): return self.history_manager.is_learned(word)
    def get_learned_words(self): return self.history_manager.get_learned_words()
    def mark_review_later(self, word): self.history_manager.mark_review_later(word)
    def remove_review_later(self, word): self.history_manager.remove_review_later(word)
    def is_review_later(self, word): return self.history_manager.is_review_later(word)
    def get_review_words(self): return self.history_manager.get_review_words()
    def get_learned_count(self): return self.history_manager.get_learned_count()
    def get_review_count(self): return self.history_manager.get_review_count()
    def get_total_learning_words(self): return self.history_manager.get_total_learning_words()
    def get_today_learned_count(self): return self.history_manager.get_today_learned_count()
    def get_learning_streak(self): return self.history_manager.get_learning_streak()
    def get_longest_streak(self): return self.history_manager.get_longest_streak()
    def clear_learning(self): self.history_manager.clear_learning()
    