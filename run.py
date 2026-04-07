import cv2
import sys
import os
import time

# Ensure the 'src' directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from cv.worker import CVWorker
except ImportError as e:
    print(f"Error: Could not import CVWorker. Ensure 'src' is in the PYTHONPATH. {e}")
    sys.exit(1)

class RunnerUI:
    def __init__(self):
        self.worker = CVWorker(callback=self.on_frame)
        self.last_data = None
        self.last_frame = None

    def on_frame(self, data, frame):
        """ Callback from the worker thread. """
        self.last_data = data
        self.last_frame = frame

    def run(self):
        print("--- Posture-Sense CV Engine Test ---")
        print("Controls:")
        print("  'q' : Quit")
        print("  'c' : Calibrate")
        print("  'm' : Toggle Mirror Mode")

        if not self.worker.start():
            return

        while True:
            if self.last_frame is None or self.last_data is None:
                time.sleep(0.01)
                continue

            img = self.last_frame.copy()
            data = self.last_data
            analysis = data.get('analysis', {})
            
            # Drawing Pose landmarks
            if data['pose']:
                for name, lm in data['pose'].items():
                    cx, cy = int(lm['x'] * img.shape[1]), int(lm['y'] * img.shape[0])
                    color = (0, 255, 0) if analysis.get('score', 0) > 80 else (0, 165, 255)
                    cv2.circle(img, (cx, cy), 5, color, cv2.FILLED)
            
            # Drawing Iris landmarks
            if data['iris']:
                for eye in ['left', 'right']:
                    for lm in data['iris'][eye]:
                        cx, cy = int(lm['x']), int(lm['y'])
                        cv2.circle(img, (cx, cy), 1, (255, 0, 0), cv2.FILLED)
            
            # UI Overlays
            score = analysis.get('score', 0)
            feedback = analysis.get('feedback', "Detecting...")
            is_standing = analysis.get('is_standing', False)
            calibrated = analysis.get('calibrated', False)
            
            # Background for text
            cv2.rectangle(img, (10, 10), (500, 130), (0, 0, 0), -1)
            
            # Score Text
            score_color = (0, 255, 0) if score > 85 else (0, 255, 255) if score > 65 else (0, 0, 255)
            cv2.putText(img, f"Score: {score}%", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.2, score_color, 2)
            
            # Status Text
            mode = "Standing" if is_standing else "Sitting"
            mirror_status = "Mirrored" if self.worker.mirror_mode else "Standard"
            cal_status = "Calibrated" if calibrated else "NOT CALIBRATED ('c')"
            cv2.putText(img, f"Mode: {mode} | {mirror_status} | {cal_status}", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Feedback Text
            cv2.putText(img, feedback, (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 200), 1)

            cv2.imshow("Posture-Sense CLI Runner", img)
            
            # Key Handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                if self.worker.calibrate():
                    print("Calibration complete!")
                else:
                    print("Calibration failed.")
            elif key == ord('m'):
                self.worker.toggle_mirror()

        self.worker.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    ui = RunnerUI()
    ui.run()
