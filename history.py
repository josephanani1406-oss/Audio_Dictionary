import json
import os
from datetime import date, timedelta


class HistoryManager:
    """Persist search history, favorites, and vocabulary-learning data."""

    def __init__(self, history_file="history.json", favorites_file="favorites.json", learning_file="learning.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.history_file = os.path.join(base_dir, history_file)
        self.favorites_file = os.path.join(base_dir, favorites_file)
        self.learning_file = os.path.join(base_dir, learning_file)
        self.history = self._load_list(self.history_file)
        self.favorites = self._load_list(self.favorites_file)
        self.learning = self._load_learning()

    def _load_list(self, file_path):
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def _save_list(self, file_path, items):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(items, file, ensure_ascii=False, indent=4)

    def _load_learning(self):
        default = {"words": {}, "activity_dates": []}
        if not os.path.exists(self.learning_file):
            return default
        try:
            with open(self.learning_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                return default
            data.setdefault("words", {})
            data.setdefault("activity_dates", [])
            if not isinstance(data["words"], dict):
                data["words"] = {}
            if not isinstance(data["activity_dates"], list):
                data["activity_dates"] = []
            return data
        except (json.JSONDecodeError, OSError):
            return default

    def _save_learning(self):
        with open(self.learning_file, "w", encoding="utf-8") as file:
            json.dump(self.learning, file, ensure_ascii=False, indent=4)

    @staticmethod
    def _normalize_word(word):
        return str(word).strip().lower()

    def _ensure_word(self, word):
        clean_word = str(word).strip()
        if not clean_word:
            return None
        normalized = self._normalize_word(clean_word)
        self.learning["words"].setdefault(
            normalized,
            {"word": clean_word, "note": "", "learned": False, "review_later": False},
        )
        return normalized

    # -------------------- History --------------------
    def add_search(self, word):
        clean_word = str(word).strip()
        if not clean_word:
            return
        normalized = self._normalize_word(clean_word)
        self.history = [item for item in self.history if self._normalize_word(item) != normalized]
        self.history.insert(0, clean_word)
        self.history = self.history[:20]
        self._save_list(self.history_file, self.history)

    def get_history(self):
        return list(self.history)

    def clear_history(self):
        self.history = []
        self._save_list(self.history_file, self.history)

    # -------------------- Favorites --------------------
    def add_favorite(self, word):
        clean_word = str(word).strip()
        if not clean_word:
            return
        normalized = self._normalize_word(clean_word)
        if not any(self._normalize_word(item) == normalized for item in self.favorites):
            self.favorites.append(clean_word)
            self._save_list(self.favorites_file, self.favorites)

    def remove_favorite(self, word):
        normalized = self._normalize_word(word)
        self.favorites = [item for item in self.favorites if self._normalize_word(item) != normalized]
        self._save_list(self.favorites_file, self.favorites)

    def is_favorite(self, word):
        normalized = self._normalize_word(word)
        return any(self._normalize_word(item) == normalized for item in self.favorites)

    def get_favorites(self):
        return list(self.favorites)

    def clear_favorites(self):
        self.favorites = []
        self._save_list(self.favorites_file, self.favorites)

    # -------------------- Notes --------------------
    def add_note(self, word, note):
        normalized = self._ensure_word(word)
        if normalized is None:
            return
        self.learning["words"][normalized]["note"] = str(note).strip()
        self._save_learning()

    def get_note(self, word):
        data = self.learning["words"].get(self._normalize_word(word))
        return data.get("note", "") if data else ""

    # -------------------- Learned --------------------
    def mark_learned(self, word):
        normalized = self._ensure_word(word)
        if normalized is None:
            return
        self.learning["words"][normalized]["learned"] = True
        today = date.today().isoformat()
        self.learning["words"][normalized]["learned_date"] = today
        if today not in self.learning["activity_dates"]:
            self.learning["activity_dates"].append(today)
        self._save_learning()

    def unmark_learned(self, word):
        normalized = self._normalize_word(word)
        if normalized in self.learning["words"]:
            self.learning["words"][normalized]["learned"] = False
            self._save_learning()

    def is_learned(self, word):
        data = self.learning["words"].get(self._normalize_word(word))
        return bool(data and data.get("learned", False))

    def get_learned_words(self):
        return [d.get("word", "") for d in self.learning["words"].values() if d.get("learned", False)]

    # -------------------- Review Later --------------------
    def mark_review_later(self, word):
        normalized = self._ensure_word(word)
        if normalized is None:
            return
        self.learning["words"][normalized]["review_later"] = True
        self._save_learning()

    def remove_review_later(self, word):
        normalized = self._normalize_word(word)
        if normalized in self.learning["words"]:
            self.learning["words"][normalized]["review_later"] = False
            self._save_learning()

    def is_review_later(self, word):
        data = self.learning["words"].get(self._normalize_word(word))
        return bool(data and data.get("review_later", False))

    def get_review_words(self):
        return [d.get("word", "") for d in self.learning["words"].values() if d.get("review_later", False)]

    # -------------------- Statistics --------------------
    def get_learned_count(self):
        return len(self.get_learned_words())

    def get_review_count(self):
        return len(self.get_review_words())

    def get_total_learning_words(self):
        return len(self.learning["words"])

    def get_today_learned_count(self):
        # Activity dates track days on which a word was marked learned.
        # For the daily goal we use the number of words whose learning record
        # was created/marked today when that metadata exists, and otherwise
        # fall back to 0 rather than guessing from the existing data.
        today = date.today().isoformat()
        return sum(1 for d in self.learning["words"].values() if d.get("learned_date") == today)

    def get_learning_streak(self):
        activity = set(self.learning.get("activity_dates", []))
        streak = 0
        current = date.today()
        while current.isoformat() in activity:
            streak += 1
            current -= timedelta(days=1)
        return streak

    def get_longest_streak(self):
        dates = sorted({date.fromisoformat(d) for d in self.learning.get("activity_dates", []) if self._valid_date(d)})
        if not dates:
            return 0
        longest = current = 1
        for previous, following in zip(dates, dates[1:]):
            if following == previous + timedelta(days=1):
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return longest

    @staticmethod
    def _valid_date(value):
        try:
            date.fromisoformat(value)
            return True
        except (TypeError, ValueError):
            return False

    def clear_learning(self):
        self.learning = {"words": {}, "activity_dates": []}
        self._save_learning()

