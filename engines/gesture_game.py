import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import pydirectinput
import json
import time
import os

# --- LOAD CONFIGURATION ---
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
MODEL_PATH  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model", "hand_landmarker.task")

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: config.json not found, using defaults.")
        return {}

config = load_config()
controls = config.get("gesture_controls", {
    "swipe_up": "up", "swipe_down": "down",
    "swipe_left": "left", "swipe_right": "right"
})

ht = config.get("hand_tracking", {})
SWIPE_THRESHOLD      = int(ht.get("swipe_threshold", 100))
COOLDOWN_TIME        = float(ht.get("cooldown_time", 0.5))
DETECT_CONF          = float(ht.get("detection_confidence", 0.7))
PRESENCE_CONF        = float(ht.get("presence_confidence", 0.7))
TRACK_CONF           = float(ht.get("tracking_confidence", 0.6))

INDEX_TIP = 8  # MediaPipe landmark index for index finger tip

CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (9,10),(10,11),(11,12),
    (13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17)
]

def process_gestures():
    print("Hand Tracking Gesture Engine Started!")
    print(f"  Box size (threshold): {SWIPE_THRESHOLD}px  |  Cooldown: {COOLDOWN_TIME}s")
    print(f"  Detection conf: {DETECT_CONF}  |  Presence conf: {PRESENCE_CONF}  |  Tracking conf: {TRACK_CONF}")

    base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    options = mp_vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=DETECT_CONF,
        min_hand_presence_confidence=PRESENCE_CONF,
        min_tracking_confidence=TRACK_CONF,
        running_mode=mp_vision.RunningMode.VIDEO
    )
    landmarker = mp_vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    last_action_time = 0
    has_triggered    = False
    current_message  = "Show your hand"
    frame_ts         = 0

    while cap.isOpened():
        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        cx, cy = w // 2, h // 2

        # Draw neutral zone box
        color_box = (0, 0, 255) if has_triggered else (0, 255, 0)
        cv2.rectangle(img,
                      (cx - SWIPE_THRESHOLD, cy - SWIPE_THRESHOLD),
                      (cx + SWIPE_THRESHOLD, cy + SWIPE_THRESHOLD),
                      color_box, 2)

        frame_ts += 1
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                          data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        result = landmarker.detect_for_video(mp_img, frame_ts)

        current_time = time.time()
        hand_detected = False

        if result.hand_landmarks:
            hand_detected = True
            landmarks = result.hand_landmarks[0]

            # Draw skeleton
            for lm in landmarks:
                cv2.circle(img, (int(lm.x * w), int(lm.y * h)), 4, (0, 200, 255), cv2.FILLED)
            for a, b in CONNECTIONS:
                cv2.line(img,
                         (int(landmarks[a].x * w), int(landmarks[a].y * h)),
                         (int(landmarks[b].x * w), int(landmarks[b].y * h)),
                         (200, 200, 200), 1)

            # Track index fingertip
            tip = landmarks[INDEX_TIP]
            x, y = int(tip.x * w), int(tip.y * h)
            cv2.circle(img, (x, y), 12, (0, 255, 255), cv2.FILLED)

            dx = x - cx
            dy = y - cy

            if abs(dx) < SWIPE_THRESHOLD and abs(dy) < SWIPE_THRESHOLD:
                if current_time - last_action_time > COOLDOWN_TIME:
                    has_triggered   = False
                    current_message = "Ready"
            elif not has_triggered and current_time - last_action_time > COOLDOWN_TIME:
                if abs(dx) > abs(dy):
                    if dx > 0:
                        key = controls.get("swipe_right")
                        current_message = f"SWIPE RIGHT ({key})"
                    else:
                        key = controls.get("swipe_left")
                        current_message = f"SWIPE LEFT ({key})"
                else:
                    if dy > 0:
                        key = controls.get("swipe_down")
                        current_message = f"SWIPE DOWN ({key})"
                    else:
                        key = controls.get("swipe_up")
                        current_message = f"SWIPE UP ({key})"

                if key:
                    pydirectinput.press(key)
                has_triggered   = True
                last_action_time = current_time

        if not hand_detected:
            current_message = "Show your hand"

        cv2.putText(img, current_message, (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow("Hand Tracking Gesture Engine", img)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    landmarker.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    process_gestures()
