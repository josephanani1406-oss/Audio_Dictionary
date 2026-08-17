import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from dictionary import DictionaryEngine
from gui import AudioDictionaryGUI


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


class TestGUIAudioStop(unittest.TestCase):
    def make_gui(self):
        gui = AudioDictionaryGUI.__new__(AudioDictionaryGUI)
        gui.controller = SimpleNamespace(audio_player=Mock())
        gui.word_entry = Mock()
        gui.meaning_box = Mock()
        gui.word_image_label = Mock()
        gui.status = Mock()
        gui.search_btn = Mock()
        gui.audio_url = "old"
        gui.word_image = "old"
        gui.current_read_text = "old"
        gui.search_running = False
        return gui

    def test_clear_search_stops_current_audio(self):
        gui = self.make_gui()

        gui.clear_search()

        gui.controller.audio_player.stop_audio.assert_called_once()

    @patch("gui.threading.Thread")
    def test_search_word_stops_current_audio_before_search(self, mock_thread):
        gui = self.make_gui()
        gui.word_entry.get.return_value = "hello"

        gui.search_word()

        gui.controller.audio_player.stop_audio.assert_called_once()
        mock_thread.assert_called_once()


if __name__ == "__main__":
    unittest.main()
