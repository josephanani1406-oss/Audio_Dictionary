import time
import vlc


class AudioPlayer:
    """
    Handles playing and stopping pronunciation audio.

    VLC is used to play the audio URL returned by
    the Dictionary API.
    """

    def __init__(self):
        # Store the VLC media player instance.
        # It starts as None because no audio is playing yet.
        self.player = None

    def play_audio(self, audio_url):
        """
        Play pronunciation audio from the provided URL.

        Args:
            audio_url: URL of the pronunciation audio.

        Returns:
            True if playback starts successfully,
            otherwise False.
        """

        # There is nothing to play if no audio URL
        # was provided by the dictionary API.
        if not audio_url:
            return False

        try:
            # Stop any audio that is currently playing.
            if self.player:
                self.player.stop()

            # Create a new VLC media player using
            # the pronunciation audio URL.
            self.player = vlc.MediaPlayer(audio_url)

            # Start playing the audio.
            self.player.play()

            # Give VLC a short moment to initialize
            # the audio playback.
            time.sleep(0.5)

            return True

        except Exception as error:
            # Handle any VLC or playback-related error
            # without crashing the application.
            print(f"Audio Error: {error}")
            return False

    def stop_audio(self):
        """
        Stop the currently playing pronunciation.
        """

        # Only attempt to stop the player if
        # a VLC player has already been created.
        if self.player:
            self.player.stop()