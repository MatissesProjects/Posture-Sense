import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    def __init__(self, static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_hands(self, img):
        """ Processes the image and finds hand landmarks. """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_rgb = np.ascontiguousarray(img_rgb)
        self.results = self.hands.process(img_rgb)
        return self.results

    def get_hand_landmarks(self, img_w, img_h):
        """ Returns normalized landmarks for detected hands. """
        hands_data = []
        if self.results and self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                lms = []
                for lm in hand_lms.landmark:
                    lms.append({
                        "x": lm.x,
                        "y": lm.y,
                        "z": lm.z
                    })
                hands_data.append(lms)
        return hands_data

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    while True:
        success, img = cap.read()
        if not success: break
        tracker.find_hands(img)
        print(f"Hands Detected: {len(tracker.get_hand_landmarks(640, 480))}")
        cv2.imshow("Hand Test", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
