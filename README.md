# Gesture Action Motion Engine

A unified Python application that lets you control games or applications using **MediaPipe Hand Tracking** and voice commands — concurrently, in real time.

## Features

1. **Unified Engine Launcher (`main.py`)**  
   A graphical Tkinter interface to launch and stop the Voice and Gesture engines simultaneously.

2. **Hand Tracking Gesture Controller (`engines/gesture_game.py`)**  
   Uses your webcam and **MediaPipe** to track your **index finger tip** in real time.  
   - Moving your finger far enough Up, Down, Left, or Right from the center neutral zone triggers a directional action.
   - No colored object needed — just your bare hand.

3. **Standalone Hand Tracker (`scripts/hand_tracker.py`)**  
   A simple, dependency-light standalone version of the gesture controller — useful for quick testing without launching the full engine.

4. **Voice Controller (`engines/voice_314.py`)**  
   Uses your microphone for local, offline speech recognition via Vosk. Evaluates partial phonemes for ultra-fast input response.

5. **Settings UI (`Settings / Calibration` button)**  
   - **Hand Tracking tab**: sliders for box size, cooldown/sensitivity, and all three MediaPipe confidence thresholds.
   - **Preview tab**: opens a live camera overlay to verify hand detection before running.
   - **Keybinds tab**: remap all voice and gesture actions.

6. **Custom Keybinds (`config.json`)**  
   Map swipes and voice commands to any keyboard key via `pydirectinput`.

## Requirements

- Python 3.10+ (tested on 3.14)
- Windows OS (`pydirectinput` is Windows-specific)
- A webcam and microphone

## Installation

1. Clone or download this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Download the Hand Landmark Model:**  
   The gesture engine requires a MediaPipe `.task` model file.
   ```bash
   python -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', 'model/hand_landmarker.task'); print('Downloaded!')"
   ```
   *(The `model/` folder is gitignored — you must run this once after cloning.)*

4. **Download the Vosk Voice Model** *(optional, for voice engine)*:  
   Download a model from [Vosk Models](https://alphacephei.com/vosk/models) (e.g., `vosk-model-small-en-us-0.15`), extract it, and place the folder as `model/` in the project root.

## Configuration

Edit `config.json` or use the Settings UI in `main.py`. Example:
```json
{
  "gesture_controls": {
    "swipe_up": "w",
    "swipe_down": "s",
    "swipe_left": "a",
    "swipe_right": "d"
  },
  "hand_tracking": {
    "swipe_threshold": 100,
    "cooldown_time": 0.5,
    "detection_confidence": 0.7,
    "presence_confidence": 0.7,
    "tracking_confidence": 0.6
  }
}
```

## Usage

```bash
python main.py
```
1. Check the engines you want to enable.
2. Click **START ENGINE**.
3. Show your hand to the camera — move your index finger past the green box to swipe.
4. Click **STOP ENGINE** or close the window to safely terminate all processes.

## License

MIT License. See the [LICENSE](LICENSE) file for more details.