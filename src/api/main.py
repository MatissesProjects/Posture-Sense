from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from src.cv.worker import CVWorker
from src.intelligence.report_generator import ReportGenerator
from fastapi.responses import FileResponse
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global worker instance
cv_worker = None

def api_cv_callback(data, frame):
    """ Callback from CVWorker to push data to the API. """
    # Use the global manager to broadcast
    # We use a wrapper to handle the async call from a sync thread
    asyncio.run_coroutine_threadsafe(manager.broadcast(json.dumps(data)), loop)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global cv_worker, loop
    loop = asyncio.get_running_loop()
    
    # Initialize and start the CV worker
    cv_worker = CVWorker(callback=api_cv_callback)
    cv_worker.start()
    logger.info("CV Worker started in API lifespan.")
    
    yield
    
    # Stop the worker on shutdown
    if cv_worker:
        cv_worker.stop()
    logger.info("CV Worker stopped in API lifespan.")

app = FastAPI(title="Posture-Sense API", lifespan=lifespan)

# Enable CORS for the React/Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Connection might be closed
                pass

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "Posture-Sense API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "worker_running": cv_worker.is_running if cv_worker else False}

@app.post("/api/calibrate")
async def calibrate(context: str = "neutral"):
    if cv_worker:
        success = cv_worker.calibrate(context)
        return {"success": success, "context": context}
    return {"success": False, "error": "Worker not initialized"}

@app.post("/api/toggle-mirror")
async def toggle_mirror():
    if cv_worker:
        mirror_mode = cv_worker.toggle_mirror()
        return {"mirror_mode": mirror_mode}
    return {"error": "Worker not initialized"}

@app.post("/api/toggle-privacy")
async def toggle_privacy():
    if cv_worker:
        privacy_mode = cv_worker.toggle_privacy()
        return {"privacy_mode": privacy_mode}
    return {"error": "Worker not initialized"}

@app.post("/api/toggle-auto-align")
async def toggle_auto_align():
    if cv_worker:
        auto_align = cv_worker.toggle_auto_align()
        return {"auto_align": auto_align}
    return {"error": "Worker not initialized"}

@app.delete("/api/delete-all-data")
async def delete_all_data():
    if cv_worker:
        success = cv_worker.stats_manager.db_manager.delete_all_data()
        return {"success": success}
    return {"success": False, "error": "Worker not initialized"}

@app.get("/api/history")
async def get_history(limit: int = 100):
    if cv_worker:
        logs = cv_worker.stats_manager.db_manager.get_recent_history(limit)
        # Convert sqlite rows to list of dicts
        history = []
        for log in logs:
            history.append({
                "id": log[0],
                "timestamp": log[1],
                "score": log[2],
                "is_standing": bool(log[3]),
                "distance_cm": log[4],
                "viewing_angle": log[5],
                "blink_rate": log[6],
                "slouch_duration": log[7],
                "rula_score": log[8],
                "reba_score": log[9],
                "metrics": json.loads(log[10]) if log[10] else {}
            })
        return history
    return []

@app.get("/api/sessions")
async def get_sessions(limit: int = 20):
    if cv_worker:
        cursor = cv_worker.stats_manager.db_manager.conn.cursor()
        cursor.execute('SELECT id, start_time, end_time, avg_score, total_ergonomic_minutes FROM sessions ORDER BY start_time DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        
        sessions = []
        for row in rows:
            sessions.append({
                "id": row[0],
                "start_time": row[1],
                "end_time": row[2],
                "avg_score": row[3],
                "total_ergonomic_minutes": row[4]
            })
        return sessions
    return []

@app.get("/api/generate-report")
async def generate_report():
    if cv_worker:
        # Get data for report (limit to last 500 for performance)
        history = await get_history(limit=500)
        sessions = await get_sessions(limit=50)
        
        generator = ReportGenerator()
        filepath = generator.generate_assessment_report(history, sessions)
        
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type='application/pdf'
        )
    return {"error": "Worker not initialized"}

@app.websocket("/ws/posture")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
