# dictionary_api.py

import requests


class DictionaryAPI:
    """Handles communication with the Free Dictionary API."""

    BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

    def search(self, word):
        """
        Search for a word and return useful dictionary information.
        """

        # Remove unnecessary spaces
        word = word.strip()

        # Make sure the user entered something
        if not word:
            return {
                "success": False,
                "error": "Please enter a word."
            }

        # Create the complete API URL
        url = self.BASE_URL + word

        try:
            # Send a request to the API
            response = requests.get(url, timeout=10)

            # Check whether the API request was successful
            if response.status_code == 404:
                return {
                    "success": False,
                    "error": f"Sorry, '{word}' was not found."
                }

            response.raise_for_status()

            # Convert the API response from JSON into Python data
            data = response.json()

            # Extract the first dictionary entry
            entry = data[0]

            # Get the word
            result_word = entry.get("word", word)

            # Get phonetic information
            phonetic = entry.get("phonetic", "")

            # Get phonetic audio
            audio = ""

            for phonetic_item in entry.get("phonetics", []):
                if phonetic_item.get("audio"):
                    audio = phonetic_item["audio"]
                    break

            # Store meanings
            meanings = []

            for meaning in entry.get("meanings", []):

                part_of_speech = meaning.get(
                    "partOfSpeech",
                    ""
                )

                definitions = meaning.get(
                    "definitions",
                    []
                )

                for definition in definitions:

                    definition_text = definition.get(
                        "definition",
                        ""
                    )

                    example = definition.get(
                        "example",
                        ""
                    )

                    synonyms = definition.get(
                        "synonyms",
                        []
                    )

                    antonyms = definition.get(
                        "antonyms",
                        []
                    )

                    meanings.append({
                        "part_of_speech": part_of_speech,
                        "definition": definition_text,
                        "example": example,
                        "synonyms": synonyms,
                        "antonyms": antonyms
                    })

            # Return everything in a clean format
            return {
                "success": True,
                "word": result_word,
                "phonetic": phonetic,
                "audio": audio,
                "meanings": meanings
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "The dictionary service took too long to respond."
            }

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Unable to connect to the internet."
            }

        except requests.exceptions.RequestException as error:
            return {
                "success": False,
                "error": f"Dictionary service error: {error}"
            }

        except (IndexError, KeyError, TypeError, ValueError):
            return {
                "success": False,
                "error": "The dictionary returned an unexpected response."
            }

        