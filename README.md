# Keyboard Input Detection with Haptic and Speech Feedback

## Overview
This Python program detects user input from two keyboard buttons and processes different types of key presses: short presses, long presses, and multiple successive presses. The system provides auditory feedback using text-to-speech and haptic feedback using beeps. It is designed for accessibility, particularly for users with visual impairments.

## Features
- Detects **short presses, long presses, and multiple quick presses**.
- Uses **threading** to ensure responsiveness.
- Provides **haptic feedback** via `winsound.Beep()`.
- Implements **text-to-speech** with `pyttsx3`.
- Uses a **queue system** for speech requests to ensure only the latest request is processed.
- Logs detected keypresses for debugging and monitoring.

## Requirements
- Python 3.x
- `pynput` for keyboard input handling
- `pyttsx3` for text-to-speech
- `winsound` (built-in for Windows, alternatives needed for other OS)

## Installation
```sh
pip install pynput pyttsx3
```

## Usage
Run the script:
```sh
python main.py
```
By default, the program listens for two keys (`'a'` and `'s'`).

## Key Detection Logic
- **Short press**: Press duration between `0.3s` and `1.0s`.
- **Long press**: Press duration `>= 1.0s`.
- **Multiple quick presses**: Two or more presses within `0.5s`.

## How It Works
1. The `KeyListener` class detects key presses and releases.
2. The `FeedbackManager` handles text-to-speech and haptic feedback.
3. The `MainLoop` runs the listener and ensures smooth operation.

## Logging
The program logs keypress events to the console at the `INFO` level:
```
2025-03-01 12:34:56 - INFO - Short press detected for 'a'
2025-03-01 12:34:58 - INFO - 2 presses detected for 's'
```

## Notes
- Ensure your sound system is working for speech feedback.
- The script is designed for Windows (`winsound`), but can be adapted for other OS.

## License
MIT License

