import cv2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebcamTester:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None

    def test_connection(self):
        """Tests if the webcam can be opened."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logger.error(f"Could not open webcam with index {self.camera_index}")
            return False
        
        ret, frame = self.cap.read()
        if not ret:
            logger.error("Could not read frame from webcam")
            self.cap.release()
            return False
        
        logger.info(f"Successfully connected to webcam {self.camera_index}")
        self.cap.release()
        return True

    def show_feed(self):
        """Opens a window showing the webcam feed."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logger.error("Could not open webcam")
            return

        logger.info("Starting webcam feed. Press 'q' to quit.")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                logger.error("Failed to grab frame")
                break
            
            cv2.imshow("Webcam Test", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Webcam feed closed.")

if __name__ == "__main__":
    tester = WebcamTester()
    if tester.test_connection():
        tester.show_feed()
