# dictionary_api.py

import requests


class DictionaryAPI:
    """
    Handles communication with the Free Dictionary API.

    This class sends word searches to the API and processes
    the response into a simple format that the application
    can easily use.
    """

    # Base URL for the English dictionary API.
    BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

    def search(self, word):
        """
        Search for a word in the dictionary.

        Args:
            word: The word the user wants to search for.

        Returns:
            A dictionary containing either the word information
            or an error message.
        """

        # Make sure the input is a string, remove unnecessary
        # spaces, and convert it to lowercase.
        word = str(word or "").strip().lower()

        # Stop the search if the user did not enter a word.
        if not word:
            return {
                "success": False,
                "error": "Please enter a word."
            }

        # Build the complete API URL.
        url = self.BASE_URL + word

        try:
            # Send a GET request to the dictionary API.
            # timeout=10 prevents the application from waiting forever.
            response = requests.get(
                url,
                timeout=10
            )

            # HTTP 404 means that the requested word
            # could not be found.
            if response.status_code == 404:
                return {
                    "success": False,
                    "error": f"Sorry, '{word}' was not found."
                }

            # Raise an exception for other unsuccessful
            # HTTP status codes such as 500 or 503.
            response.raise_for_status()

            # Convert the JSON response into Python data.
            data = response.json()

            # The API normally returns a list of dictionary entries.
            # We use the first entry.
            if not isinstance(data, list) or not data:
                return {
                    "success": False,
                    "error": "The dictionary returned an unexpected response."
                }

            entry = data[0]

            # Make sure the first entry is a dictionary.
            if not isinstance(entry, dict):
                return {
                    "success": False,
                    "error": "The dictionary returned an unexpected response."
                }

            # Get the actual word returned by the API.
            result_word = entry.get("word", word)

            # Get the phonetic pronunciation.
            phonetic = entry.get("phonetic", "")

            # -----------------------------------------
            # Find the audio pronunciation
            # -----------------------------------------

            audio = ""

            # The API may contain several phonetic objects.
            # We use the first one that has an audio URL.
            for phonetic_item in entry.get("phonetics", []):

                if phonetic_item.get("audio"):
                    audio = phonetic_item["audio"]
                    break

            # -----------------------------------------
            # Extract meanings and definitions
            # -----------------------------------------

            meanings = []

            # A word can have multiple meanings.
            for meaning in entry.get("meanings", []):

                # Example: noun, verb, adjective, etc.
                part_of_speech = meaning.get(
                    "partOfSpeech",
                    ""
                )

                # Get all definitions belonging to this
                # particular part of speech.
                definitions = meaning.get(
                    "definitions",
                    []
                )

                # Process each definition separately.
                for definition in definitions:

                    # Get the definition itself.
                    definition_text = definition.get(
                        "definition",
                        ""
                    )

                    # Get an example sentence, if available.
                    example = definition.get(
                        "example",
                        ""
                    )

                    # Get synonyms, if available.
                    synonyms = definition.get(
                        "synonyms",
                        []
                    )

                    # Get antonyms, if available.
                    antonyms = definition.get(
                        "antonyms",
                        []
                    )

                    # Add the processed definition to our list.
                    meanings.append({
                        "part_of_speech": part_of_speech,
                        "definition": definition_text,
                        "example": example,
                        "synonyms": synonyms,
                        "antonyms": antonyms
                    })

            # -----------------------------------------
            # Return the final dictionary result
            # -----------------------------------------

            return {
                "success": True,
                "word": result_word,
                "phonetic": phonetic,
                "audio": audio,
                "meanings": meanings
            }

        # Handle cases where the API takes too long to respond.
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "The dictionary service took too long to respond."
            }

        # Handle situations where there is no internet connection
        # or the API server cannot be reached.
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Unable to connect to the internet."
            }

        # Handle other HTTP or request-related errors.
        except requests.exceptions.RequestException as error:
            return {
                "success": False,
                "error": f"Dictionary service error: {error}"
            }

        # Handle unexpected data returned by the API.
        except (IndexError, KeyError, TypeError, ValueError):
            return {
                "success": False,
                "error": "The dictionary returned an unexpected response."
            }