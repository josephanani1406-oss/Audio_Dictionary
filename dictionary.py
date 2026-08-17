import requests


class DictionaryEngine:

    def __init__(self, language="en"):
        self.language = self._normalize_language(language)
        self.base_url = f"https://api.dictionaryapi.dev/api/v2/entries/{self.language}/"

    @staticmethod
    def _normalize_language(language_code):
        code = (language_code or "en").strip().lower()
        mapping = {
            "en": "en",
            "es": "es",
            "fr": "fr",
            "de": "de",
            "it": "it",
            "pt": "pt",
            "ru": "ru",
            "tr": "tr",
            "ja": "ja",
            "zh": "zh",
            "ko": "ko",
            "ar": "ar"
        }
        return mapping.get(code, "en")

    def set_language(self, language_code):
        self.language = self._normalize_language(language_code)
        self.base_url = f"https://api.dictionaryapi.dev/api/v2/entries/{self.language}/"

    def search_word(self, word):
        word = str(word or "").strip().lower()
        if not word:
            return {
                "success": False,
                "message": "Please enter a word."
            }

        try:
            response = requests.get(self.base_url + word, timeout=10)

            if response.status_code != 200:
                return {
                    "success": False,
                    "message": "Word not found."
                }

            payload = response.json()
            # print(payload)
            if not isinstance(payload, list) or not payload:
                return {
                    "success": False,
                    "message": "Word not found."
                }

            data = payload[0]
            # print(data)
            if not isinstance(data, dict):
                return {
                    "success": False,
                    "message": "Word not found."
                }

            phonetic = data.get("phonetic", "")
            meanings = []
            audio = ""

            for phonetic_data in data.get("phonetics", []):
                if phonetic_data.get("audio"):
                    audio = phonetic_data["audio"]
                    break

            for meaning in data.get("meanings", []):
                definitions = []
                for definition in meaning.get("definitions", []):
                    definitions.append({
                        "definition": definition.get("definition", ""),
                        "example": definition.get("example", "")
                    })

                meanings.append({
                    "partOfSpeech": meaning.get("partOfSpeech", ""),
                    "definitions": definitions,
                    "synonyms": meaning.get("synonyms", []),
                    "antonyms": meaning.get("antonyms", [])
                })

            return {
                "success": True,
                "word": data.get("word", word),
                "phonetic": phonetic,
                "audio": audio,
                "meanings": meanings,
                "language": self.language
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }