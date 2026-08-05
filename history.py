import json
import os


class HistoryManager:
    def __init__(self, history_file="history.json", favorites_file="favorites.json"):
        self.history_file = os.path.join(os.path.dirname(__file__), history_file)
        self.favorites_file = os.path.join(os.path.dirname(__file__), favorites_file)
        self.history = self._load_list(self.history_file)
        self.favorites = self._load_list(self.favorites_file)

    def _load_list(self, file_path):
        if not os.path.exists(file_path):
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, OSError):
            pass

        return []

    def _save_list(self, file_path, items):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(items, file, ensure_ascii=False)

    def add_search(self, word):
        clean_word = str(word).strip()
        if not clean_word:
            return

        normalized = clean_word.lower()
        self.history = [item for item in self.history if item.lower() != normalized]
        self.history.insert(0, clean_word)
        self.history = self.history[:20]
        self._save_list(self.history_file, self.history)

    def add_favorite(self, word):
        clean_word = str(word).strip()
        if not clean_word:
            return

        normalized = clean_word.lower()
        if any(item.lower() == normalized for item in self.favorites):
            return

        self.favorites.append(clean_word)
        self._save_list(self.favorites_file, self.favorites)

    def get_history(self):
        return list(self.history)

    def get_favorites(self):
        return list(self.favorites)

    def clear_history(self):
        self.history = []
        self._save_list(self.history_file, self.history)

    def clear_favorites(self):
        self.favorites = []
        self._save_list(self.favorites_file, self.favorites)
