import cv2
import sys
import os

# Ensure the 'src' directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from cv.pipeline import CVPipeline
except ImportError as e:
    print(f"Error: Could not import CVPipeline. Ensure 'src' is in the PYTHONPATH. {e}")
    sys.exit(1)

def main():
    """ Main entry point for testing the Posture-Sense CV Engine. """
    print("--- Posture-Sense CV Engine Test ---")
    print("Controls:")
    print("  'q' : Quit")
    print("  'c' : Calibrate (Sit in your neutral/good posture)")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    pipeline = CVPipeline()
    
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture image from webcam.")
            break
        
        # Process the frame
        data = pipeline.process_frame(img)
        analysis = data.get('analysis', {})
        
        # Drawing Pose landmarks
        if data['pose']:
            for name, lm in data['pose'].items():
                cx, cy = int(lm['x'] * img.shape[1]), int(lm['y'] * img.shape[0])
                color = (0, 255, 0) if analysis.get('score', 0) > 80 else (0, 165, 255)
                cv2.circle(img, (cx, cy), 5, color, cv2.FILLED)
        
        # UI Overlays
        score = analysis.get('score', 0)
        feedback = analysis.get('feedback', "Detecting...")
        is_standing = analysis.get('is_standing', False)
        calibrated = analysis.get('calibrated', False)
        
        # Background for text
        cv2.rectangle(img, (10, 10), (450, 120), (0, 0, 0), -1)
        
        # Score Text
        score_color = (0, 255, 0) if score > 85 else (0, 255, 255) if score > 65 else (0, 0, 255)
        cv2.putText(img, f"Score: {score}%", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.2, score_color, 2)
        
        # Status Text
        mode = "Standing" if is_standing else "Sitting"
        cal_status = "Calibrated" if calibrated else "NOT CALIBRATED ('c' to calibrate)"
        cv2.putText(img, f"Mode: {mode} | {cal_status}", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Feedback Text
        cv2.putText(img, feedback, (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 200), 1)

        # Show the result
        cv2.imshow("Posture-Sense - Track 002 Test", img)
        
        # Key Handling
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            if data['pose']:
                success = pipeline.posture_analyzer.calibrate(data['pose'])
                if success:
                    print("Calibration complete!")
                else:
                    print("Calibration failed. Ensure you are in frame.")
    
    cap.release()
    cv2.destroyAllWindows()
    print("--- CV Engine Closed ---")

if __name__ == "__main__":
    main()
