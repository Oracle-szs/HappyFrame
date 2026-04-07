# HappyFrame

A tkinter-based full-screen image and sound display application with voice-activated triggers using Vosk speech recognition.

## File Structure

```
Happyframe/
├── Frame-1.py              # Main application
├── config.py               # Configuration manager
├── setup.py                # Setup GUI wizard
├── config.json             # Generated config file (auto-created on setup)
├── models/
│   └── vosk-model-nl-spraakherkenning-0.6/  # Speech recognition model
├── images/                 # User-uploaded images for triggers
├── sounds/                 # User-uploaded audio files for triggers
└── README.md               # This file
```

## Getting Started

### Prerequisites

The application will automatically download the required Vosk speech recognition model (Dutch) on first run if it doesn't exist. This requires an internet connection for the initial setup.

### First Run

When you run the application for the first time (or if `config.json` is missing/empty), a setup wizard will launch automatically:

1. **Add a Word**: Enter a word/command (e.g., "energie", "blij", "rustig")
2. **Add Images**: Upload one or more images for that word
3. **Add Sounds**: Upload one or more audio files for that word
4. **Repeat**: Add more words with their images and sounds

### Running the Application

```bash
python3 Frame-1.py
```

The application will:
- Load your configuration
- Display random idle images in fullscreen
- Listen for voice commands using the microphone
- When a configured word is recognized, display the associated images and play sounds

## Features

- **Automatic Model Download**: Downloads the Dutch Vosk speech recognition model automatically on first run
- **Voice Activation**: Uses Vosk for offline speech recognition in Dutch
- **Relative Paths**: All paths are relative to the project directory, works on any device/user
- **GUI Configuration**: Easy setup wizard for adding words, images, and sounds
- **Fullscreen Display**: Shows images in fullscreen mode
- **Audio Playback**: Plays random sound from the word's audio pool

## Configuration

The `config.json` file stores your words:

```json
{
  "triggers": [
    {
      "id": "energie",
      "images": ["energie1.jpg", "energie2.jpg"],
      "sounds": ["energie.ogg", "cheer.wav"],
      "phrases": ["energie"]
    }
  ]
}
```

You can edit this directly or use the setup GUI.

## Audio/Image Formats

**Images**: JPG, JPEG, PNG, BMP, GIF

**Audio**: OGG, WAV, MP3, FLAC

## Requirements

- Python 3.7+
- tkinter
- Pillow (PIL)
- pygame
- PyAudio
- vosk
- A working microphone

## Troubleshooting

### "No microphone found"
Check that your microphone is properly connected and recognized by your system.

### "Failed to create a model"
Ensure the Vosk model is properly extracted in the `models/` directory.

### Setup GUI not appearing
To manually reconfigure:

```bash
python3 setup.py
```

## Manual Setup

To manually reconfigure words anytime:

```bash
python3 setup.py
```
