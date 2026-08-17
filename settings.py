"""
Settings manager for Audio Dictionary
Handles configuration persistence
"""

import json
import os
from typing import Dict, Any


class SettingsManager:
    """Manages application settings and configuration"""
    
    DEFAULT_SETTINGS = {
        "voice": "female",
        "dark_mode": False,
        "window_geometry": "900x700",
        "language": "en",
    }
    
    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = config_file
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from config file"""
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults to handle new keys
                    return {**self.DEFAULT_SETTINGS, **settings}
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self) -> bool:
        """Save settings to config file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple settings"""
        self.settings.update(updates)
        self.save_settings()
