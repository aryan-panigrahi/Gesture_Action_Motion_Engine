import cv2
import numpy as np
import pydirectinput
import time

# --- CONFIGURATION ---
WIDTH, HEIGHT = 640, 480
SWIPE_THRESHOLD = 100
# COLOR RANGE (HSV) - Default is "Blue"
# Use a tool like specific color pickers to find exact ranges for your object
LOWER_COLOR = np.array([100, 150, 0]) 
UPPER_COLOR = np.array([140, 255, 255])

cap = cv2.VideoCapture(0)
cap.set(3, WIDTH)
cap.set(4, HEIGHT)

has_triggered = False
current_message = "Show Blue Object"

print("Color Controller Started on Python 3.14!")

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    
    # 1. Convert to HSV Color Space (Easier for computer to see color)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 2. Create a "Mask" (Black & White image where White = The Color)
    mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
    
    # Clean up noise (remove tiny specks of color)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # 3. Find Contours (Shapes) in the mask
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    center = None
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Draw Neutral Zone
    color_box = (0, 0, 255) if has_triggered else (0, 255, 0)
    cv2.rectangle(img, (cx - SWIPE_THRESHOLD, cy - SWIPE_THRESHOLD), 
                  (cx + SWIPE_THRESHOLD, cy + SWIPE_THRESHOLD), color_box, 2)

    if len(contours) > 0:
        # Get the biggest blue object (ignore small background noise)
        c = max(contours, key=cv2.contourArea)
        ((x_float, y_float), radius) = cv2.minEnclosingCircle(c)
        
        # Only track if the object is big enough
        if radius > 10:
            # Draw circle around the object
            cv2.circle(img, (int(x_float), int(y_float)), int(radius), (0, 255, 255), 2)
            
            x = int(x_float)
            y = int(y_float)

            # --- SWIPE LOGIC (Same as before) ---
            dx = x - cx
            dy = y - cy

            if abs(dx) < SWIPE_THRESHOLD and abs(dy) < SWIPE_THRESHOLD:
                has_triggered = False
                current_message = "Ready"
            elif not has_triggered:
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

    cv2.putText(img, current_message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imshow("Color Tracker (Py 3.14)", img)
    # Show the mask too so you can debug the color detection
    cv2.imshow("Mask Debug", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()