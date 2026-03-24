import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import pydirectinput
import time
import os

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model", "hand_landmarker.task")

WIDTH, HEIGHT = 640, 480
SWIPE_THRESHOLD = 100
COOLDOWN_TIME = 0.5
INDEX_TIP = 8

base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
options = mp_vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.6,
    running_mode=mp_vision.RunningMode.VIDEO
)
landmarker = mp_vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

has_triggered = False
last_action_time = 0
current_message = "Show your hand"
frame_ts = 0

CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (9,10),(10,11),(11,12),
    (13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17)
]

print("Hand Tracking Controller Started!")

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    cx, cy = WIDTH // 2, HEIGHT // 2

    color_box = (0, 0, 255) if has_triggered else (0, 255, 0)
    cv2.rectangle(img,
                  (cx - SWIPE_THRESHOLD, cy - SWIPE_THRESHOLD),
                  (cx + SWIPE_THRESHOLD, cy + SWIPE_THRESHOLD),
                  color_box, 2)

    frame_ts += 1
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    result = landmarker.detect_for_video(mp_image, frame_ts)

    current_time = time.time()
    hand_detected = False

    if result.hand_landmarks:
        hand_detected = True
        landmarks = result.hand_landmarks[0]

        for lm in landmarks:
            cv2.circle(img, (int(lm.x * WIDTH), int(lm.y * HEIGHT)), 4, (0, 200, 255), cv2.FILLED)
        for a, b in CONNECTIONS:
            cv2.line(img,
                     (int(landmarks[a].x * WIDTH), int(landmarks[a].y * HEIGHT)),
                     (int(landmarks[b].x * WIDTH), int(landmarks[b].y * HEIGHT)),
                     (200, 200, 200), 1)

        tip = landmarks[INDEX_TIP]
        x, y = int(tip.x * WIDTH), int(tip.y * HEIGHT)
        cv2.circle(img, (x, y), 12, (0, 255, 255), cv2.FILLED)

        dx = x - cx
        dy = y - cy

        if abs(dx) < SWIPE_THRESHOLD and abs(dy) < SWIPE_THRESHOLD:
            if current_time - last_action_time > COOLDOWN_TIME:
                has_triggered = False
                current_message = "Ready"
        elif not has_triggered and current_time - last_action_time > COOLDOWN_TIME:
            if abs(dx) > abs(dy):
                if dx > 0:
                    pydirectinput.press('right')
                    current_message = "SWIPE RIGHT"
                else:
                    pydirectinput.press('left')
                    current_message = "SWIPE LEFT"
            else:
                if dy > 0:
                    pydirectinput.press('down')
                    current_message = "SWIPE DOWN"
                else:
                    pydirectinput.press('up')
                    current_message = "SWIPE UP"
            has_triggered = True
            last_action_time = current_time

    if not hand_detected:
        current_message = "Show your hand"

    cv2.putText(img, current_message, (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imshow("Hand Tracker", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

landmarker.close()
cap.release()
cv2.destroyAllWindows()