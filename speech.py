import subprocess
import sys


class SpeechEngine:
    def __init__(self):
        self.available = sys.platform.startswith("win")

    def speak(self, text):
        text = str(text or "").strip()
        if not text or not self.available:
            return False

        try:
            safe_text = text.replace('"', '\\"')
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f'$voice = New-Object -ComObject SAPI.SpVoice; $voice.Speak("{safe_text}")'
                ],
                check=False,
                capture_output=True,
                text=True
            )
            return True
        except Exception:
            return False
