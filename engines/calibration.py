import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import os

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model", "hand_landmarker.task")

CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (9,10),(10,11),(11,12),
    (13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17)
]
import json

def run_calibration():
    """
    Open a live camera preview with hand landmark overlay so the user can
    verify that hand tracking is working correctly before starting the engine.
    Press 'q' or close the window to exit.
    """
    print("Opening Hand Tracking Preview...")
    print("Verify that your hand landmarks are drawn correctly, then press 'q' to close.")

    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    camera_index = 0
    detect_conf = 0.5
    presence_conf = 0.5
    track_conf = 0.5
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            ht = config.get("hand_tracking", {})
            camera_index = ht.get("camera_index", 0)
            detect_conf = float(ht.get("detection_confidence", 0.5))
            presence_conf = float(ht.get("presence_confidence", 0.5))
            track_conf = float(ht.get("tracking_confidence", 0.5))
    except Exception:
        pass

    base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    options = mp_vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        min_hand_detection_confidence=detect_conf,
        min_hand_presence_confidence=presence_conf,
        min_tracking_confidence=track_conf,
        running_mode=mp_vision.RunningMode.VIDEO
    )
    landmarker = mp_vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(camera_index)
    frame_ts = 0

    while cap.isOpened():
        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1)
        h, w, _ = img.shape

        frame_ts += 1
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        result = landmarker.detect_for_video(mp_image, frame_ts)

        hand_count = 0
        if result.hand_landmarks:
            hand_count = len(result.hand_landmarks)
            for landmarks in result.hand_landmarks:
                for lm in landmarks:
                    cv2.circle(img, (int(lm.x * w), int(lm.y * h)), 4, (0, 200, 255), cv2.FILLED)
                for a, b in CONNECTIONS:
                    cv2.line(img,
                             (int(landmarks[a].x * w), int(landmarks[a].y * h)),
                             (int(landmarks[b].x * w), int(landmarks[b].y * h)),
                             (200, 200, 200), 1)
                # Highlight index tip
                tip = landmarks[8]
                cv2.circle(img, (int(tip.x * w), int(tip.y * h)), 12, (0, 255, 255), cv2.FILLED)

        status = f"Hands detected: {hand_count}" if hand_count else "No Hand Detected"
        color = (0, 255, 0) if hand_count else (0, 0, 255)
        cv2.putText(img, status, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(img, "Press 'q' to close", (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow("Hand Tracking Preview", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    landmarker.close()
    cap.release()
    cv2.destroyAllWindows()
    return True


if __name__ == "__main__":
    run_calibration()
