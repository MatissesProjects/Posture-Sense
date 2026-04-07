from win10toast import ToastNotifier
import threading
import time
import logging

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        self.toaster = ToastNotifier()
        self.last_notification_time = {}
        self.throttle_seconds = 300 # Default: 5 minutes between same-type notifications

    def notify(self, title, message, alert_type="general", duration=5):
        """
        Sends a Windows toast notification with throttling.
        """
        now = time.time()
        if alert_type in self.last_notification_time:
            if now - self.last_notification_time[alert_type] < self.throttle_seconds:
                return False # Throttled

        self.last_notification_time[alert_type] = now
        
        # Run in a separate thread to not block the CV Engine
        thread = threading.Thread(
            target=self._show_toast, 
            args=(title, message, duration),
            daemon=True
        )
        thread.start()
        return True

    def _show_toast(self, title, message, duration):
        try:
            self.toaster.show_toast(
                title,
                message,
                icon_path=None, # Future: Add a custom icon
                duration=duration,
                threaded=True
            )
        except Exception as e:
            logger.error(f"Failed to show toast: {e}")

if __name__ == "__main__":
    nm = NotificationManager()
    nm.notify("Posture-Sense", "This is a test notification!", "general")
    time.sleep(2)
