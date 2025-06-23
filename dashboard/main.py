from fastapi import FastAPI, Request, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import json
import asyncio
from pathlib import Path
from typing import List, Dict
from metrics import metrics_collector
from config import config
from .auth import (
    Token, User, authenticate_user, create_access_token,
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create FastAPI app
app = FastAPI(title="Mirror.exe Dashboard")

# Setup static files and templates
dashboard_dir = Path(__file__).parent
static_dir = dashboard_dir / "static"
templates = Jinja2Templates(directory=str(dashboard_dir / "templates"))

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                self.disconnect(connection)

manager = ConnectionManager()

# Authentication endpoints
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render the login page."""
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Main routes
@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request, current_user: User = Depends(get_current_active_user)):
    """Render the main dashboard page."""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": current_user}
    )

@app.get("/api/metrics/summary")
async def get_metrics_summary(current_user: User = Depends(get_current_active_user)):
    """Get current metrics summary."""
    return metrics_collector.get_summary()

@app.get("/api/metrics/history")
async def get_metrics_history(current_user: User = Depends(get_current_active_user)):
    """Get historical metrics for the past 24 hours."""
    metrics_dir = Path("metrics")
    metrics_data = []
    
    try:
        for metrics_file in metrics_dir.glob("metrics_*.json"):
            with open(metrics_file) as f:
                metrics_data.append(json.loads(f.read()))
    except Exception as e:
        return {"error": str(e)}
        
    return {"metrics": metrics_data}

@app.get("/api/config")
async def get_config(current_user: User = Depends(get_current_active_user)):
    """Get current configuration (excluding sensitive data)."""
    return {
        "audio": {
            "cache_dir": str(config.audio.cache_dir),
            "output_dir": str(config.audio.output_dir),
            "max_cache_size_mb": config.audio.max_cache_size_mb
        },
        "chat": {
            "max_retry_attempts": config.chat.max_retry_attempts,
            "retry_delay_seconds": config.chat.retry_delay_seconds,
            "connection_timeout": config.chat.connection_timeout
        },
        "gpt": {
            "model": config.gpt.model,
            "temperature": config.gpt.temperature,
            "max_tokens": config.gpt.max_tokens
        }
    }

@app.get("/api/status")
async def get_status(current_user: User = Depends(get_current_active_user)):
    """Get current application status."""
    from chat_listener import chat_listener
    return {
        "is_connected": chat_listener.is_connected,
        "uptime": metrics_collector.get_uptime(),
        "total_users": len(metrics_collector.chat_metrics.unique_users),
        "total_responses": metrics_collector.chat_metrics.total_responses
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send real-time updates every second
            status_data = await get_status(None)
            metrics_data = metrics_collector.get_summary()
            await websocket.send_json({
                "type": "update",
                "status": status_data,
                "metrics": metrics_data
            })
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task to broadcast metrics updates
@app.on_event("startup")
async def start_metrics_broadcast():
    async def broadcast_metrics():
        while True:
            try:
                status_data = await get_status(None)
                metrics_data = metrics_collector.get_summary()
                await manager.broadcast({
                    "type": "update",
                    "status": status_data,
                    "metrics": metrics_data
                })
            except Exception as e:
                print(f"Error broadcasting metrics: {e}")
            await asyncio.sleep(1)

    asyncio.create_task(broadcast_metrics()) 