import requests


class DictionaryEngine:
    """
    Handles communication with the Free Dictionary API
    and processes dictionary results.
    """

    def __init__(self, language="en"):
        # Normalize the language code and set the API URL.
        self.language = self._normalize_language(language)
        self.base_url = (
            f"https://api.dictionaryapi.dev/api/v2/entries/{self.language}/"
        )

    @staticmethod
    def _normalize_language(language_code):

        # Make sure the value is a string, remove spaces,
        # and convert it to lowercase.
        code = (language_code or "en").strip().lower()

        # Languages supported by the application.
        supported_languages = {
            "en": "en",  # English
            "es": "es",  # Spanish
            "fr": "fr",  # French
            "de": "de",  # German
            "it": "it",  # Italian
            "pt": "pt",  # Portuguese
            "ru": "ru",  # Russian
            "tr": "tr",  # Turkish
            "ja": "ja",  # Japanese
            "zh": "zh",  # Chinese
            "ko": "ko",  # Korean
            "ar": "ar"   # Arabic
        }

        # Return the selected language.
        # If it is not supported, use English.
        return supported_languages.get(code, "en")

    def set_language(self, language_code):
        """
        Changes the dictionary language and updates
        the API URL accordingly.
        """

        # Normalize the new language code.
        self.language = self._normalize_language(language_code)

        # Rebuild the API URL using the new language.
        self.base_url = (
            f"https://api.dictionaryapi.dev/api/v2/entries/{self.language}/"
        )

    def search_word(self, word):
        """
        Searches for a word using the Dictionary API.

        Returns a dictionary containing the result.
        """

        # Convert the input to a string, remove unnecessary spaces,
        # and convert it to lowercase.
        word = str(word or "").strip().lower()

        # Make sure the user entered something.
        if not word:
            return {
                "success": False,
                "message": "Please enter a word."
            }

        try:
            # Send a GET request to the Dictionary API.
            response = requests.get(
                self.base_url + word,
                timeout=10
            )

            # A status code other than 200 means the request
            # did not return a valid dictionary result.
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": "Word not found."
                }

            # Convert the API response from JSON into Python data.
            payload = response.json()

            # The API normally returns a list containing
            # dictionary entries.
            if not isinstance(payload, list) or not payload:
                return {
                    "success": False,
                    "message": "Word not found."
                }

            # Get the first dictionary entry.
            data = payload[0]

            # Make sure the entry is a dictionary.
            if not isinstance(data, dict):
                return {
                    "success": False,
                    "message": "Word not found."
                }

            # Get the phonetic pronunciation.
            phonetic = data.get("phonetic", "")

            # This will store the audio pronunciation URL.
            audio = ""

            # Look through the phonetics list and use
            # the first available audio URL.
            for phonetic_data in data.get("phonetics", []):
                if phonetic_data.get("audio"):
                    audio = phonetic_data["audio"]
                    break

            # This list will contain all meanings of the word.
            meanings = []

            # Loop through each meaning returned by the API.
            for meaning in data.get("meanings", []):

                # Store definitions belonging to this meaning.
                definitions = []

                # Loop through each definition.
                for definition in meaning.get("definitions", []):

                    definitions.append({
                        "definition": definition.get("definition", ""),
                        "example": definition.get("example", "")
                    })

                # Store the part of speech, definitions,
                # synonyms, and antonyms.
                meanings.append({
                    "partOfSpeech": meaning.get("partOfSpeech", ""),
                    "definitions": definitions,
                    "synonyms": meaning.get("synonyms", []),
                    "antonyms": meaning.get("antonyms", [])
                })

            # Return the processed dictionary information.
            return {
                "success": True,
                "word": data.get("word", word),
                "phonetic": phonetic,
                "audio": audio,
                "meanings": meanings,
                "language": self.language
            }

        except requests.exceptions.Timeout:
            # Handle cases where the API takes too long to respond.
            return {
                "success": False,
                "message": "The request timed out. Please try again."
            }

        except requests.exceptions.RequestException as e:
            # Handle other network-related errors.
            return {
                "success": False,
                "message": f"Network error: {str(e)}"
            }

        except Exception as e:
            # Catch unexpected errors so the application
            # does not crash.
            return {
                "success": False,
                "message": str(e)
            }