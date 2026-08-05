import time
import vlc


class AudioPlayer:
    def __init__(self):
        self.player = None

    def play_audio(self, audio_url):
        """
        Plays the pronunciation audio from the DictionaryAPI URL.
        """

        if not audio_url:
            return False

        try:
            # Stop any audio already playing
            if self.player:
                self.player.stop()

            self.player = vlc.MediaPlayer(audio_url)
            self.player.play()

            # Give VLC a moment to start playback
            time.sleep(0.5)

            return True

        except Exception as e:
            print(f"Audio Error: {e}")
            return False

    def stop_audio(self):
        if self.player:
            self.player.stop()