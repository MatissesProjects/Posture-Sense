from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from src.cv.worker import CVWorker

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
async def calibrate():
    if cv_worker:
        success = cv_worker.calibrate()
        return {"success": success}
    return {"success": False, "error": "Worker not initialized"}

@app.post("/api/toggle-mirror")
async def toggle_mirror():
    if cv_worker:
        mirror_mode = cv_worker.toggle_mirror()
        return {"mirror_mode": mirror_mode}
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
