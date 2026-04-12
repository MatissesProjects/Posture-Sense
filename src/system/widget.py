import tkinter as tk
import json
import threading
import websocket
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostureWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Posture-Sense Mini")
        
        # Transparent and Always on Top
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True) # Frameless
        self.root.attributes("-alpha", 0.8) # Semi-transparent
        self.root.configure(bg='#0f172a') # Slate-900

        # Position in top right corner
        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"180x80+{screen_w-200}+50")

        # UI Components
        self.score_label = tk.Label(self.root, text="--%", font=("Helvetica", 24, "bold"), fg="#4ade80", bg='#0f172a')
        self.score_label.pack(pady=(10, 0))

        self.status_label = tk.Label(self.root, text="Connecting...", font=("Helvetica", 8, "bold"), fg="#94a3b8", bg='#0f172a')
        self.status_label.pack()

        # Draggable logic
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

        # Close button (tiny X)
        self.close_btn = tk.Label(self.root, text="✕", font=("Helvetica", 8), fg="#475569", bg='#0f172a', cursor="hand2")
        self.close_btn.place(x=160, y=5)
        self.close_btn.bind("<Button-1>", lambda e: self.root.destroy())

        self.running = True
        self.ws_thread = threading.Thread(target=self.listen_ws, daemon=True)
        self.ws_thread.start()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def update_ui(self, data):
        try:
            analysis = data.get('analysis', {})
            score = analysis.get('score', 0)
            feedback = analysis.get('feedback', "Tracking")
            
            # Simple color logic
            color = "#4ade80" # Green
            if score < 85: color = "#fbbf24" # Amber
            if score < 65: color = "#f43f5e" # Rose

            self.score_label.config(text=f"{int(score)}%", fg=color)
            
            # Shorten feedback for widget
            short_feedback = feedback.split('|')[0].strip()[:20]
            self.status_label.config(text=short_feedback)
        except Exception as e:
            logger.error(f"UI Update error: {e}")

    def listen_ws(self):
        while self.running:
            try:
                ws = websocket.WebSocketApp("ws://127.0.0.1:8000/ws/posture",
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close)
                ws.run_forever()
            except Exception as e:
                logger.error(f"WS Connection failed: {e}")
            time.sleep(5) # Retry interval

    def on_message(self, ws, message):
        data = json.loads(message)
        self.root.after(0, self.update_ui, data)

    def on_error(self, ws, error):
        logger.error(f"WS Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logger.info("WS Closed")
        self.root.after(0, lambda: self.status_label.config(text="Reconnecting..."))

    def run(self):
        self.root.mainloop()
        self.running = False

if __name__ == "__main__":
    widget = PostureWidget()
    widget.run()
