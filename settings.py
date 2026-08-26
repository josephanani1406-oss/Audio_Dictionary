"""
Settings manager for Audio Dictionary.
Handles saving and loading application settings.
"""

import json
import os
from typing import Dict, Any


class SettingsManager:

    DEFAULT_SETTINGS = {
        "voice": "female",
        "dark_mode": False,
        "window_geometry": "900x700",
        "language": "en"
    }

    def __init__(self, config_file="config/settings.json"):
        self.config_file = config_file
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Load saved settings or return the default settings."""

        try:
            config_directory = os.path.dirname(self.config_file)

            if config_directory:
                os.makedirs(
                    config_directory,
                    exist_ok=True
                )

            if os.path.exists(self.config_file):

                with open(
                    self.config_file,
                    "r",
                    encoding="utf-8"
                ) as file:
                    saved_settings = json.load(file)

                if isinstance(saved_settings, dict):
                    # Keep default values for settings that are
                    # missing from an older configuration file.
                    return {
                        **self.DEFAULT_SETTINGS,
                        **saved_settings
                    }

        except (
            json.JSONDecodeError,
            OSError,
            TypeError
        ) as error:

            print(f"Error loading settings: {error}")

        return self.DEFAULT_SETTINGS.copy()

    def save_settings(self) -> bool:
        """Save the current settings to the JSON file."""

        try:
            config_directory = os.path.dirname(
                self.config_file
            )

            if config_directory:
                os.makedirs(
                    config_directory,
                    exist_ok=True
                )

            with open(
                self.config_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.settings,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return True

        except OSError as error:

            print(f"Error saving settings: {error}")
            return False

    def get(self, key, default=None):
        """Get a setting value."""

        return self.settings.get(
            key,
            default
        )

    def set(self, key, value):
        """Update and save one setting."""

        self.settings[key] = value
        return self.save_settings()

    def update(self, updates):
        """Update and save multiple settings."""

        if not isinstance(updates, dict):
            return False

        self.settings.update(updates)

        return self.save_settings()