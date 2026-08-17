"""
Audio Dictionary Application
Main entry point for the application
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import after path is set
from gui import AudioDictionaryGUI


def create_directories():
    """Ensure required directories exist"""
    directories = ['data', 'config', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def main():
    """Main entry point for the Audio Dictionary application"""
    try:
        # Create necessary directories
        create_directories()
        
        # Initialize and run the GUI
        app = AudioDictionaryGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()