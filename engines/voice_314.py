import os
import queue
import sys
import json
import sounddevice as sd
import pydirectinput
import traceback
from vosk import Model, KaldiRecognizer
import threading

# --- CONFIGURATION ---
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    with open(CONFIG_PATH, 'r') as f:
         config = json.load(f)
         voice_controls = config.get("voice_controls", {})
except FileNotFoundError:
    print(f"Warning: Configuration file not found at {CONFIG_PATH}. Using defaults.")
    voice_controls = {
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
        "jump": "space",
        "start": "enter"
    }

# --- TUNING SETTINGS ---
BLOCK_SIZE = 4096   # Standard for high-quality external mics
# Provide valid commands to vosk to improve accuracy (Vosk expects a JSON list string)
valid_words = list(voice_controls.keys()) + ["[unk]"]
VALID_COMMANDS = json.dumps(valid_words)

MODEL_PATH = os.path.join(PROJECT_ROOT, "model")
if not os.path.exists(MODEL_PATH):
    sys.exit("❌ Error: 'model' folder not found!")

Model.log_level = -1
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, 16000, VALID_COMMANDS)
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"⚠️ Audio Status Warning: {status}", file=sys.stderr)
    q.put(bytes(indata))

def run_voice(stop_event=None):
    if not os.path.exists(MODEL_PATH):
        print("❌ Error: 'model' folder not found!")
        return

    print("\n=== 🎤 EXTERNAL MIC CONTROLLER (SMART PARTIALS) ===")
    print("Tracking word chains to prevent double-inputs without sacrificing speed.")
    print("Say commands cleanly and distinctly.")
    print("\n🚨 TIP: If running in Windows Command Prompt, DO NOT CLICK inside the terminal.")
    print("Clicking text selects it and PAUSES the script. Press ESC or ENTER if it freezes! 🚨\n")

    # Track how many words we've successfully parsed in the current breath/utterance
    words_processed = 0 

    try:
        device_index = config.get("voice_settings", {}).get("microphone_index", "")
        if isinstance(device_index, str) and device_index.isdigit():
            device_index = int(device_index)
        elif device_index == "":
            device_index = None
            
        with sd.RawInputStream(samplerate=16000, blocksize=BLOCK_SIZE, dtype='int16', 
                               channels=1, callback=callback, device=device_index) as stream:
            
            while True:
                if stop_event and stop_event.is_set():
                    print("Received stop signal. Stopping Voice Engine.")
                    break
                    
                try:
                    # Add a timeout so we can periodically check if the audio stream died
                    data = q.get(timeout=1.0)
                except queue.Empty:
                    if not stream.active:
                        print("❌ Error: Audio stream disconnected or stopped unexpectedly!")
                        break
                    continue
                
                # 1. AcceptWaveform is True when there's silence (the speaker paused)
                if rec.AcceptWaveform(data):
                    # Consume the final result to clear the recognizer's internal buffers
                    rec.Result() 
                    # The utterance has finished, so we reset our processed word count
                    words_processed = 0
                    continue 
                
                # 2. Process partials for blistering fast speed
                partial = json.loads(rec.PartialResult())
                text = partial.get("partial", "").strip()

                if not text:
                    continue

                words = text.split()
                
                # 3. If the recognizer is starting to form a NEW word in the sentence...
                if len(words) > words_processed:
                    current_word = words[-1] # Look at ONLY the new word being formed
                    
                    action = None
                    
                    # Detecting quick phonetic word fragments matching configured keys
                    for cmd_key, mapped_key in voice_controls.items():
                        # We use simple string inclusion since some Vosk outputs are partial phonemes
                        if len(cmd_key) >= 2:
                            # Match if start of the word matches start of the command
                            # e.g "ju" for "jump", "do" for "down"
                            if current_word.startswith(cmd_key[:2]):
                                action = mapped_key
                                break
                        elif cmd_key in current_word:
                            action = mapped_key
                            break

                    # If we found a valid command fragment
                    if action:
                        if isinstance(action, str):
                            pydirectinput.press(action)
                            print(f"⚡ ACTION: {action.upper()} (from '{current_word}')")
                        
                        # Lock out any further checks for THIS specific word
                        # until a new word (separated by a space) appears
                        words_processed = len(words)

    except KeyboardInterrupt:
        print("\nStopped by User.")
    except Exception as e:
        print(f"\n❌ CRITICAL CRASH: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_voice()