import os
import queue
import sys
import json
import time
import sounddevice as sd
import pydirectinput
from vosk import Model, KaldiRecognizer

# --- TUNING SETTINGS ---
COOLDOWN = 0.7      # The "Dead Air" time (adjust between 0.5 and 1.0)
BLOCK_SIZE = 4096   # Standard for high-quality external mics
VALID_COMMANDS = '["up", "down", "left", "right", "jump", "start"]'

if not os.path.exists("model"):
    sys.exit("❌ Error: 'model' folder not found!")

Model.log_level = -1
model = Model("model")
rec = KaldiRecognizer(model, 16000, VALID_COMMANDS)
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

print("\n=== 🎤 EXTERNAL MIC CONTROLLER (HARD LOCK) ===")
print("Resetting AI memory after every command to stop double-inputs.")

last_trigger_time = 0

try:
    with sd.RawInputStream(samplerate=16000, blocksize=BLOCK_SIZE, dtype='int16', 
                           channels=1, callback=callback):
        while True:
            data = q.get()
            
            # 1. THE DEAF WINDOW
            # If we recently triggered, we discard the audio entirely
            if time.time() - last_trigger_time < COOLDOWN:
                with q.mutex:
                    q.queue.clear()
                continue 

            if rec.AcceptWaveform(data):
                pass 
            
            # Process partials for speed
            partial = json.loads(rec.PartialResult())
            text = partial.get("partial", "")

            if text:
                action = None
                # Detecting quick word fragments
                if any(x in text for x in ["ju", "up"]): action = "up"
                elif any(x in text for x in ["do", "ow", "sl"]): action = "down"
                elif "le" in text: action = "left"
                elif "ri" in text: action = "right"

                if action:
                    pydirectinput.press(action)
                    print(f"⚡ ACTION: {action.upper()}")
                    
                    # 2. THE NUCLEAR RESET
                    # Wipe the AI's "memory" so it forgets the word immediately
                    rec.Reset() 
                    last_trigger_time = time.time()
                    
                    # 3. PURGE THE REMAINING AUDIO
                    # This deletes the 'tail' of your word still in the mic buffer
                    with q.mutex:
                        q.queue.clear()

except KeyboardInterrupt:
    print("\nStopped.")