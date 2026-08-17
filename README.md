# Audio Dictionary

A professional-grade desktop audio dictionary application built with Python and Tkinter. Provides word definitions, pronunciation guides, visual references, and text-to-speech capabilities.

## Features

- 🔍 **Word Search** - Powered by Free Dictionary API
- 🔊 **Pronunciation** - Hear word pronunciations
- 📖 **Text-to-Speech** - Read definitions aloud
- 📜 **Search History** - Track your searches
- ⭐ **Favorites** - Save favorite words
- 🖼️ **Visual Reference** - Images from Wikimedia Commons
- 📚 **Comprehensive Definitions** - Parts of speech, examples, synonyms, antonyms

## Project Structure

```
Audio_Dictionary/
├── src/                    # Main application code
│   ├── __init__.py
│   ├── gui.py             # Tkinter GUI interface
│   ├── controller.py      # Application logic controller
│   ├── history.py         # Search history management
│   ├── speech.py          # Text-to-speech engine
│   ├── dictionary_api.py  # Dictionary API client
│   ├── dictionary.py      # Dictionary core logic
│   └── audio.py           # Audio file handling
├── tests/                 # Test files
│   ├── test_dictionary.py
│   ├── test_search_flow.py
│   └── test_spell.py
├── data/                  # User data (history, favorites)
│   ├── history.json
│   └── favorites.json
├── config/                # Configuration files
├── assets/                # UI assets and images
│   ├── word_placeholder.png
│   └── audio_dictionary_icon.ico
├── docs/                  # Documentation
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Audio_Dictionary
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python main.py
```

### Using the GUI

1. **Search for a word** - Enter a word in the search box and click 🔍 or press Enter
2. **Pronounce** - Click 🔊 to hear the pronunciation
3. **Read Definition** - Click 📖 to hear the definition read aloud
4. **Save to Favorites** - Click ❤️ to add to favorites
5. **View History** - Click 📜 to see recent searches
6. **Clear** - Click 🗑️ to clear the current search

## Dependencies

- **Pillow** - Image processing for display
- **pyttsx3** - Text-to-speech functionality
- **requests** - HTTP client for API calls
- **tkinter** - GUI framework (included with Python)

## API Reference

The application uses the **Free Dictionary API** for word definitions:
- Endpoint: `https://api.dictionaryapi.dev/api/v2/entries/en/`
- No API key required

## Testing

Run the test suite:
```bash
python -m pytest tests/
# or run individual tests
python tests/test_dictionary.py
python tests/test_search_flow.py
python tests/test_spell.py
```

## Features Overview

### GUI Components
- **Search Interface** - Clean, intuitive word search
- **Definition Panel** - Detailed word meanings with examples
- **Visual Reference** - Auto-fetches images from Wikimedia
- **Control Buttons** - Emoji-based interface with tooltips
- **Status Bar** - Real-time feedback on operations
- **Sidebar** - Quick access to history and favorites

### Backend Architecture
- **MVC Pattern** - Model-View-Controller separation
- **Threading** - Non-blocking UI operations
- **Error Handling** - Graceful error recovery
- **Data Persistence** - JSON-based storage

## Configuration

User data is stored in `data/` folder:
- `history.json` - Search history
- `favorites.json` - Saved favorite words

## Building an Executable

To convert to a Windows .exe file:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "AudioDictionary" --add-data "assets:assets" --icon assets/audio_dictionary_icon.ico main.py
```

The executable will be created in the `dist/` folder.

## Troubleshooting

### No sound on Pronounce button
- Check if your system volume is not muted
- Ensure pyttsx3 is installed and working
- Try the Read button instead (text-to-speech)

### Images not loading
- Check your internet connection
- Wikimedia Commons might be temporarily unavailable
- The fallback placeholder image will be shown

### History/Favorites not saving
- Ensure write permissions in the `data/` folder
- Check if JSON files are not corrupted

## Development

### Adding New Features
1. Update the appropriate module in `src/`
2. Add tests in `tests/`
3. Update documentation
4. Test thoroughly before deployment

### Code Style
- Follow PEP 8 guidelines
- Use descriptive variable names
- Add comments for complex logic

## License

This project is open source. Please check the LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue or contact the development team.

## Version History

- **v1.0** - Initial release with core features

---

Made with ❤️ for language learners and dictionary enthusiasts
