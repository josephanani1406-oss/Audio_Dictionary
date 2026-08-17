"""
Speech Engine for Text-to-Speech
Supports different voice types (male, female, child)
"""

import subprocess
import sys


class SpeechEngine:
    """Text-to-speech engine with voice selection"""
    
    VOICE_MAPPING = {
        "female": 0,      # Default female voice
        "male": 1,        # Male voice
        "child": 2,       # Child voice (if available)
    }
    
    def __init__(self):
        self.available = sys.platform.startswith("win")
        self.current_voice = "female"
    
    def set_voice(self, voice_type: str) -> bool:
        """
        Set the voice type for speech synthesis
        
        Args:
            voice_type: "female", "male", or "child"
            
        Returns:
            True if voice type is supported, False otherwise
        """
        if voice_type in self.VOICE_MAPPING:
            self.current_voice = voice_type
            return True
        return False
    
    def get_available_voices(self) -> list:
        """Get list of available voice types"""
        return list(self.VOICE_MAPPING.keys())
    
    def speak(self, text: str) -> bool:
        """
        Speak the given text using selected voice
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        text = str(text or "").strip()
        if not text or not self.available:
            return False

        try:
            safe_text = text.replace('"', '\\"')
            voice_index = self.VOICE_MAPPING.get(self.current_voice, 0)
            
            # PowerShell script to use SAPI with voice selection
            ps_command = (
                f'$voice = New-Object -ComObject SAPI.SpVoice; '
                f'$voice.Voice = $voice.GetVoices()[[{voice_index}]]; '
                f'$voice.Speak("{safe_text}")'
            )
            
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    ps_command
                ],
                check=False,
                capture_output=True,
                text=True
            )
            return True
        except Exception as e:
            print(f"Speech error: {e}")
            return False
