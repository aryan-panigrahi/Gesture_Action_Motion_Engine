# Gesture Action Motion Engine

A collection of Python scripts that allow you to control games or applications using computer vision (gestures/motion tracking) and voice commands.

## Features

1. **Color Controller (`color_game.py`)**
   Uses your webcam to track a specific colored object (default: Blue). Swiping the object Up, Down, Left, or Right triggers the corresponding arrow key inputs on your keyboard using `pydirectinput`.

2. **Voice Controller (`voice_314.py`)**
   Uses your microphone to listen for specific commands (`up`, `down`, `left`, `right`, `jump`, `start`). It processes speech partially for ultra-fast response times and triggers corresponding keyboard inputs.

## Requirements

- Python 3.x
- Windows OS (due to `pydirectinput` which is Windows-specific for sending DirectX key pulses).

## Installation

1. Clone or download this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Download the Voice Model:**
   The `voice_314.py` script requires a Vosk acoustic model to run. 
   - Download a lightweight English model from [Vosk Models](https://alphacephei.com/vosk/models) (e.g., `vosk-model-small-en-us-0.15`).
   - Extract the downloaded ZIP file.
   - Rename the extracted folder to `model` and place it in the root directory of this project.

## Usage

### Color Controller
Run the color tracking script:
```bash
python color_game.py
```
- Hold a blue object in front of your webcam.
- Swipe it past the center 'neutral zone' to trigger arrow key events.
- Press `q` to quit the windows.

### Voice Controller
Run the voice control script:
```bash
python voice_314.py
```
- Speak the commands clearly into your microphone: "up", "down", "left", "right", "jump", "start".
- Note: If you run this in the Windows Command Prompt, **do not click inside the terminal window**, as it will pause the background execution. Press ESC or ENTER if the script freezes.

## License

MIT License. See the [LICENSE](LICENSE) file for more details.