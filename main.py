import tkinter as tk
from tkinter import ttk, messagebox
import threading
import multiprocessing
import os
import sys

# Import engine modules
from engines import gesture_game
from engines import voice_314

class EngineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gesture Action Motion Engine")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variables
        self.voice_enabled = tk.BooleanVar(value=True)
        self.gesture_enabled = tk.BooleanVar(value=True)
        
        self.voice_thread = None
        self.gesture_process = None
        self.voice_stop_event = threading.Event()
        
        self.is_running = False

        self.create_widgets()

    def create_widgets(self):
        # Header
        header = ttk.Label(self.root, text="Engine Control Panel", font=("Helvetica", 16, "bold"))
        header.pack(pady=20)

        # Toggles
        frame_toggles = ttk.Frame(self.root)
        frame_toggles.pack(pady=10)

        chk_voice = ttk.Checkbutton(frame_toggles, text="Enable Voice Engine", variable=self.voice_enabled)
        chk_voice.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        chk_gesture = ttk.Checkbutton(frame_toggles, text="Enable Gesture Engine", variable=self.gesture_enabled)
        chk_gesture.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Start / Stop Buttons
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.pack(pady=20)

        self.btn_start = ttk.Button(frame_buttons, text="START ENGINE", command=self.start_engine)
        self.btn_start.grid(row=0, column=0, padx=10)

        self.btn_stop = ttk.Button(frame_buttons, text="STOP ENGINE", command=self.stop_engine, state=tk.DISABLED)
        self.btn_stop.grid(row=0, column=1, padx=10)

        # Settings Button
        self.btn_settings = ttk.Button(self.root, text="Settings / Calibration", command=self.open_settings)
        self.btn_settings.pack(pady=5)

        # Status
        self.lbl_status = ttk.Label(self.root, text="Status: Ready", font=("Helvetica", 10), foreground="gray")
        self.lbl_status.pack(side=tk.BOTTOM, pady=10)
        
    def open_settings(self):
        import json

        settings_win = tk.Toplevel(self.root)
        settings_win.title("Engine Settings")
        settings_win.geometry("430x620")
        settings_win.resizable(False, False)
        settings_win.transient(self.root)
        settings_win.grab_set()

        # Load Current Config
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config.json: {e}")
            settings_win.destroy()
            return

        notebook = ttk.Notebook(settings_win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ── TAB 1: Keybinds & Voice ──────────────────────────────────
        frame_keys = ttk.Frame(notebook)
        notebook.add(frame_keys, text="Keybinds & Voice")

        ttk.Label(frame_keys, text="Voice Settings", font=("Helvetica", 10, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(10, 4))
            
        v_cfg = config.get("voice_settings", {})
        mic_var = tk.StringVar(value=str(v_cfg.get("microphone_index", "")))
        ttk.Label(frame_keys, text="Mic Index/Name:").grid(row=1, column=0, padx=10, pady=2, sticky="e")
        mic_entry = ttk.Entry(frame_keys, textvariable=mic_var, width=15)
        mic_entry.grid(row=1, column=1, padx=10, pady=2, sticky="w")

        ttk.Label(frame_keys, text="Voice Controls", font=("Helvetica", 10, "bold")).grid(
            row=2, column=0, columnspan=2, pady=(10, 4))

        voice_entries = {}
        row_idx = 3
        for key, val in config.get("voice_controls", {}).items():
            ttk.Label(frame_keys, text=key.capitalize()).grid(row=row_idx, column=0, padx=10, pady=2, sticky="e")
            entry = ttk.Entry(frame_keys, width=15)
            entry.insert(0, val)
            entry.grid(row=row_idx, column=1, padx=10, pady=2, sticky="w")
            voice_entries[key] = entry
            row_idx += 1

        ttk.Label(frame_keys, text="Gesture Controls", font=("Helvetica", 10, "bold")).grid(
            row=row_idx, column=0, columnspan=2, pady=(10, 4))
        row_idx += 1

        gesture_entries = {}
        for key, val in config.get("gesture_controls", {}).items():
            ttk.Label(frame_keys, text=key.replace("_", " ").title()).grid(row=row_idx, column=0, padx=10, pady=2, sticky="e")
            entry = ttk.Entry(frame_keys, width=15)
            entry.insert(0, val)
            entry.grid(row=row_idx, column=1, padx=10, pady=2, sticky="w")
            gesture_entries[key] = entry
            row_idx += 1

        # ── TAB 2: Hand Tracking ──────────────────────────────────────
        frame_ht = ttk.Frame(notebook)
        notebook.add(frame_ht, text="Hand Tracking")

        ht_cfg = config.get("hand_tracking", {})

        # Helper: labeled slider row
        # Returns a DoubleVar (or IntVar) linked to the slider
        ht_vars = {}

        def add_slider(parent, row, label, key, from_, to, resolution, fmt, default):
            val = ht_cfg.get(key, default)
            var = tk.DoubleVar(value=float(val))
            ht_vars[key] = var

            ttk.Label(parent, text=label, anchor="w").grid(row=row, column=0, padx=10, pady=(10, 0), sticky="w", columnspan=2)

            lbl_val = ttk.Label(parent, text=fmt.format(float(val)), width=6, anchor="e")
            lbl_val.grid(row=row, column=2, padx=(0, 10), pady=(10, 0), sticky="e")

            def on_change(v, lv=lbl_val, f=fmt):
                lv.config(text=f.format(float(v)))

            slider = tk.Scale(
                parent, variable=var, from_=from_, to=to,
                resolution=resolution, orient=tk.HORIZONTAL,
                length=260, showvalue=False,
                command=on_change
            )
            slider.grid(row=row + 1, column=0, columnspan=3, padx=10, pady=(0, 4), sticky="ew")

        ttk.Label(frame_ht, text="Detection & Sensitivity",
                  font=("Helvetica", 10, "bold")).grid(row=0, column=0, columnspan=3, pady=(12, 2), padx=10, sticky="w")

        add_slider(frame_ht, 1,  "Box Size (neutral zone radius px)",
                   "swipe_threshold", 30, 300, 5,  "{:.0f} px", 100)
        add_slider(frame_ht, 3,  "Cooldown between swipes (s)",
                   "cooldown_time",   0.1, 3.0, 0.05, "{:.2f} s", 0.5)

        ttk.Separator(frame_ht, orient="horizontal").grid(
            row=5, column=0, columnspan=3, sticky="ew", padx=10, pady=6)
        ttk.Label(frame_ht, text="MediaPipe Confidence Thresholds",
                  font=("Helvetica", 10, "bold")).grid(row=6, column=0, columnspan=3, pady=(2, 2), padx=10, sticky="w")

        add_slider(frame_ht, 7,  "Detection Confidence",
                   "detection_confidence",  0.1, 1.0, 0.05, "{:.2f}", 0.5)
        add_slider(frame_ht, 9,  "Presence Confidence",
                   "presence_confidence",   0.1, 1.0, 0.05, "{:.2f}", 0.5)
        add_slider(frame_ht, 11, "Tracking Confidence",
                   "tracking_confidence",   0.1, 1.0, 0.05, "{:.2f}", 0.5)

        ttk.Label(frame_ht,
                  text="Tip: Lower confidence = easier detection but more false positives.\n"
                       "Higher cooldown = fewer accidental double-swipes.",
                  foreground="gray", justify="left").grid(
            row=13, column=0, columnspan=3, padx=12, pady=(8, 0), sticky="w")

        ttk.Separator(frame_ht, orient="horizontal").grid(
            row=14, column=0, columnspan=3, sticky="ew", padx=10, pady=6)
        ttk.Label(frame_ht, text="Input Source",
                  font=("Helvetica", 10, "bold")).grid(row=15, column=0, columnspan=3, pady=(2, 2), padx=10, sticky="w")
                  
        cam_var = tk.StringVar(value=str(ht_cfg.get("camera_index", "0")))
        ttk.Label(frame_ht, text="Camera Index or URL:").grid(row=16, column=0, padx=10, pady=2, sticky="w")
        cam_entry = ttk.Entry(frame_ht, textvariable=cam_var, width=15)
        cam_entry.grid(row=16, column=1, padx=10, pady=2, sticky="w")

        # ── TAB 3: Preview ───────────────────────────────────────────
        frame_prev = ttk.Frame(notebook)
        notebook.add(frame_prev, text="Preview")

        ttk.Label(frame_prev,
                  text="Open a live camera preview to verify\nhand tracking is working correctly.",
                  justify=tk.CENTER).pack(pady=30)

        def run_preview():
            settings_win.destroy()
            from engines import calibration
            calibration.run_calibration()

        ttk.Button(frame_prev, text="▶  Launch Hand Tracking Preview", command=run_preview).pack(pady=5)

        # ── Save ──────────────────────────────────────────────────────
        def save_settings():
            v_set = {}
            mic_val = mic_var.get().strip()
            v_set["microphone_index"] = int(mic_val) if mic_val.isdigit() else mic_val
            config["voice_settings"] = v_set

            vc = {k: ent.get() for k, ent in voice_entries.items()}
            config["voice_controls"] = vc

            gc = {k: ent.get() for k, ent in gesture_entries.items()}
            config["gesture_controls"] = gc

            ht_new = {}
            for k, var in ht_vars.items():
                raw = var.get()
                # swipe_threshold should be stored as int
                ht_new[k] = int(round(raw)) if k == "swipe_threshold" else round(raw, 3)
            
            cam_val = cam_var.get()
            ht_new["camera_index"] = int(cam_val) if cam_val.isdigit() else cam_val

            config["hand_tracking"] = ht_new

            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            messagebox.showinfo("Saved",
                "Settings saved!\nRestart the Gesture Engine to apply changes.")
            settings_win.destroy()

        ttk.Button(settings_win, text="💾  Save Settings", command=save_settings).pack(
            side=tk.BOTTOM, pady=10)

    def start_engine(self):
        if not self.voice_enabled.get() and not self.gesture_enabled.get():
            messagebox.showwarning("Warning", "Please enable at least one engine.")
            return

        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.lbl_status.config(text="Status: RUNNING", foreground="green")
        self.voice_stop_event.clear()

        # Start Voice Engine
        if self.voice_enabled.get():
            print("Starting Voice Engine Thread...")
            self.voice_thread = threading.Thread(target=voice_314.run_voice, args=(self.voice_stop_event,), daemon=True)
            self.voice_thread.start()

        # Start Gesture Engine (Run in multiprocessing because OpenCV needs main thread on some OS)
        if self.gesture_enabled.get():
            print("Starting Gesture Engine Process...")
            # OpenCV and MediaPipe sometimes crash if run purely in a python daemon thread
            # Multiprocessing ensures it runs safely.
            self.gesture_process = multiprocessing.Process(target=gesture_game.process_gestures)
            self.gesture_process.start()

    def stop_engine(self):
        if not self.is_running:
            return

        self.lbl_status.config(text="Status: STOPPING...", foreground="orange")
        self.root.update()

        # Stop Voice Engine
        if self.voice_thread and self.voice_thread.is_alive():
            print("Signaling Voice Engine to stop...")
            self.voice_stop_event.set()
            # We don't necessarily need to join() blocking the GUI, it will die gracefully.

        # Stop Gesture Engine
        if self.gesture_process and self.gesture_process.is_alive():
            print("Terminating Gesture Engine Process...")
            self.gesture_process.terminate()
            self.gesture_process.join()

        self.is_running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.lbl_status.config(text="Status: Stopped", foreground="red")
        print("Engines Stopped.")

    def on_closing(self):
        self.stop_engine()
        self.root.destroy()

if __name__ == "__main__":
    multiprocessing.freeze_support() # Needed for Windows multiprocessing
    root = tk.Tk()
    app = EngineApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
