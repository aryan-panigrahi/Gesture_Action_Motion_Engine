import os
import queue
import sys
import json
import sounddevice as sd
import pydirectinput
import traceback
from vosk import Model, KaldiRecognizer

# --- TUNING SETTINGS ---
BLOCK_SIZE = 4096   # Standard for high-quality external mics
VALID_COMMANDS = '["up", "down", "left", "right", "jump", "start", "[unk]"]'

if not os.path.exists("model"):
    sys.exit("❌ Error: 'model' folder not found!")

Model.log_level = -1
model = Model("model")
rec = KaldiRecognizer(model, 16000, VALID_COMMANDS)
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"⚠️ Audio Status Warning: {status}", file=sys.stderr)
    q.put(bytes(indata))

print("\n=== 🎤 EXTERNAL MIC CONTROLLER (SMART PARTIALS) ===")
print("Tracking word chains to prevent double-inputs without sacrificing speed.")
print("Say commands cleanly and distinctly.")
print("\n🚨 TIP: If running in Windows Command Prompt, DO NOT CLICK inside the terminal.")
print("Clicking text selects it and PAUSES the script. Press ESC or ENTER if it freezes! 🚨\n")

# Track how many words we've successfully parsed in the current breath/utterance
words_processed = 0 

try:
    with sd.RawInputStream(samplerate=16000, blocksize=BLOCK_SIZE, dtype='int16', 
                           channels=1, callback=callback) as stream:
        
        while True:
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
                
                # Detecting quick phonetic word fragments
                if any(x in current_word for x in ["ju", "up"]): action = "up"
                elif any(x in current_word for x in ["do", "ow", "sl"]): action = "down"
                elif "le" in current_word: action = "left"
                elif "ri" in current_word: action = "right"
                elif "st" in current_word: action = "enter"  # Mapping start to enter

                # If we found a valid command fragment
                if action:
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
    input("Press Enter to exit...")