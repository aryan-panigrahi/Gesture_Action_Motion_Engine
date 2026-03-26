# GestureApp — Distributable Build

> **Package the Gesture Action Motion Engine into a standalone `.exe`** that runs on any
> Windows device — no Python or pip required for end users.

---

## Requirements (build machine only)

| Requirement | Version |
|---|---|
| Python | 3.10 – 3.12 (3.13+ not yet supported by all deps) |
| pip | latest |
| Internet access | required for first build |

> **Note:** The `model/` folder (Vosk English model + `hand_landmarker.task`) must
> already exist in the project root before building.

---

## Building the App

1. Open **File Explorer** and navigate to `GestureApp/`
2. Double-click **`build_app.bat`**
3. Wait — the first build may take 3–10 minutes while downloading dependencies

When the script prints **BUILD SUCCESSFUL**, the app lives at:

```
GestureApp/
└── dist/
    └── GestureApp/          ← This is the app folder
        ├── GestureApp.exe   ← Launch this
        ├── model/           ← Vosk + hand-landmarker bundled
        ├── config.json      ← User-editable key bindings
        └── ...              ← Runtime DLLs and packages
```

---

## Distributing to Other Devices

1. Zip the entire `dist/GestureApp/` folder
2. Send the zip to the target device
3. Extract it anywhere (e.g., Desktop)
4. Run `GestureApp.exe`

No installation required. ✅

---

## Runtime Notes

| Topic | Detail |
|---|---|
| **Camera** | A webcam must be connected for the Gesture Engine |
| **Microphone** | Required for the Voice Engine |
| **Windows Defender** | May warn on first run — click "More info → Run anyway" |
| **Antivirus** | PyInstaller EXEs are sometimes flagged; add a folder exclusion if needed |
| **Config changes** | Edit `config.json` next to the EXE — changes take effect on next engine start |
| **Linux / macOS** | Re-run the build on the target OS; the EXE is Windows-only |

---

## Rebuilding After Code Changes

Just double-click `build_app.bat` again. PyInstaller will overwrite `dist/GestureApp/`.
