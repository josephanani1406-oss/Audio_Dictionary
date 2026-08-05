import unittest
from unittest.mock import Mock, patch

from dictionary import DictionaryEngine


class TestDictionarySearchFlow(unittest.TestCase):
    def test_search_word_handles_empty_api_payload(self):
        engine = DictionaryEngine()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch("requests.get", return_value=mock_response):
            result = engine.search_word("xyzabc")

        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Word not found.")

    def test_set_language_updates_lookup_path(self):
        engine = DictionaryEngine()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "word": "hola",
            "phonetic": "ola",
            "phonetics": [{"audio": "audio.mp3"}],
            "meanings": [{
                "partOfSpeech": "interjection",
                "definitions": [{"definition": "hello", "example": "Hola amigo"}],
                "synonyms": [],
                "antonyms": []
            }]
        }]

        with patch("requests.get", return_value=mock_response) as mock_get:
            engine.set_language("es")
            result = engine.search_word("  Hola  ")

        self.assertTrue(result["success"])
        mock_get.assert_called_once()
        self.assertIn("/es/", mock_get.call_args[0][0])
        self.assertTrue(result["word"].islower())


if __name__ == "__main__":
    unittest.main()
