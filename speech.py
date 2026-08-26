"""
Speech Engine for Text-to-Speech

Handles text-to-speech using Windows SAPI.
Supports female, male, and child voice options.
"""

import os
import subprocess
import sys


class SpeechEngine:
    """Handles text-to-speech using Windows SAPI."""

    VOICE_TYPES = {
        "female",
        "male",
        "child"
    }

    def __init__(self):
        self.available = sys.platform.startswith("win")
        self.current_voice = "female"
        self.process = None

    def set_voice(self, voice_type: str) -> bool:
        """Set the preferred voice."""

        voice_type = str(
            voice_type or ""
        ).strip().lower()

        if voice_type not in self.VOICE_TYPES:
            return False

        self.current_voice = voice_type

        return True

    def get_available_voices(self) -> list:
        """Return the voice options available in the application."""

        return [
            "female",
            "male",
            "child"
        ]

    def speak(self, text: str) -> bool:
        """Read text aloud using Windows SAPI."""

        text = str(
            text or ""
        ).strip()

        if not text:
            return False

        if not self.available:
            print(
                "Text-to-speech is only supported on Windows."
            )
            return False

        try:
            # Store the text safely in environment variables.
            os.environ["AUDIO_DICTIONARY_TEXT"] = text
            os.environ["AUDIO_DICTIONARY_VOICE"] = self.current_voice

            powershell_script = r'''
Add-Type -AssemblyName System.Speech

$text = [Environment]::GetEnvironmentVariable(
    "AUDIO_DICTIONARY_TEXT"
)

$voiceType = [Environment]::GetEnvironmentVariable(
    "AUDIO_DICTIONARY_VOICE"
)

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

$voices = $synth.GetInstalledVoices()

$selectedVoice = $null

foreach ($voice in $voices) {

    $voiceInfo = $voice.VoiceInfo
    $name = $voiceInfo.Name.ToLower()

    if ($voiceType -eq "female") {

        if (
            $name.Contains("female") -or
            $name.Contains("zira") -or
            $name.Contains("samantha") -or
            $name.Contains("hazel")
        ) {
            $selectedVoice = $voiceInfo.Name
            break
        }
    }

    elseif ($voiceType -eq "male") {

        if (
            $name.Contains("male") -or
            $name.Contains("david") -or
            $name.Contains("mark") -or
            $name.Contains("george")
        ) {
            $selectedVoice = $voiceInfo.Name
            break
        }
    }
}

if ($selectedVoice) {
    $synth.SelectVoice($selectedVoice)
}

# Make the child option sound more youthful.
if ($voiceType -eq "child") {
    $synth.Rate = 3
}
else {
    $synth.Rate = 0
}

$synth.Volume = 100

$synth.Speak($text)

$synth.Dispose()
'''

            # Start PowerShell so it can be stopped later.
            self.process = subprocess.Popen(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    powershell_script
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait until speech finishes.
            stdout, stderr = self.process.communicate()

            if self.process.returncode != 0:

                if stderr:
                    print(
                        f"Speech error: {stderr}"
                    )

                return False

            return True

        except Exception as error:

            print(
                f"Speech error: {error}"
            )

            return False

        finally:

            self.process = None

            os.environ.pop(
                "AUDIO_DICTIONARY_TEXT",
                None
            )

            os.environ.pop(
                "AUDIO_DICTIONARY_VOICE",
                None
            )

    def stop(self):
        """Stop speech that is currently playing."""

        if self.process is not None:

            try:
                if self.process.poll() is None:
                    self.process.terminate()

                    try:
                        self.process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        self.process.kill()

            except Exception as error:

                print(
                    f"Error stopping speech: {error}"
                )

            finally:
                self.process = None
                