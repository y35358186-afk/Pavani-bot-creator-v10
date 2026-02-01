"""
Pavani Bot Creator V10 - Main Application
Modular, clean, easy to read on mobile
"""
from fastapi import FastAPI, Request, Form, File, UploadFile, WebSocket, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import hashlib, logging

# Import modules
from config import Config
from auth import SessionManager
from bot_manager import BotRegistry

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("pavani.v10")

# FastAPI app
app = FastAPI(title=Config.APP_NAME, version=Config.VERSION, docs_url="/api/docs", redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Initialize managers
session_mgr = SessionManager()
registry = BotRegistry()

# Load templates
with open(Config.TEMPLATES_DIR / "login.html") as f:
    LOGIN_HTML = f.read()
with open(Config.TEMPLATES_DIR / "dashboard.html") as f:
    DASHBOARD_HTML = f.read()

# Auth dependency
def require_auth(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_mgr.verify_session(session_id):
        raise HTTPException(401, "Unauthorized")

# ═══════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return RedirectResponse("/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return LOGIN_HTML

@app.post("/api/auth/login")
async def login(request: Request, password: str = Form(...)):
    ip = request.client.host
    if not session_mgr.check_rate_limit(ip):
        return JSONResponse({"error": "Too many attempts"}, 429)
    if hashlib.sha256(password.encode()).hexdigest() == Config.PASSWORD_HASH:
        sid = session_mgr.create_session(ip)
        resp = JSONResponse({"success": True})
        resp.set_cookie("session_id", sid, httponly=True, max_age=86400)
        return resp
    return JSONResponse({"error": "Invalid password"}, 401)

@app.post("/api/auth/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        session_mgr.delete_session(session_id)
    resp = JSONResponse({"success": True})
    resp.delete_cookie("session_id")
    return resp

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(_: str = Depends(require_auth)):
    return DASHBOARD_HTML

@app.post("/api/bots")
async def create_bot(
    name: str = Form(...),
    bot_file: UploadFile = File(...),
    req_file: UploadFile = File(...),
    _: str = Depends(require_auth)
):
    bot_id = await registry.deploy(name, await bot_file.read(), await req_file.read())
    return {"bot_id": bot_id}

@app.get("/api/bots")
async def list_bots(_: str = Depends(require_auth)):
    return registry.all()

@app.get("/api/bots/{bot_id}")
async def get_bot(bot_id: str, _: str = Depends(require_auth)):
    bot = registry.get(bot_id)
    if not bot:
        raise HTTPException(404)
    return bot.to_dict()

@app.post("/api/bots/{bot_id}/restart")
async def restart_bot(bot_id: str, _: str = Depends(require_auth)):
    bot = registry.get(bot_id)
    if not bot:
        raise HTTPException(404)
    await bot.restart()
    return {"success": True}

@app.post("/api/bots/{bot_id}/stop")
async def stop_bot(bot_id: str, _: str = Depends(require_auth)):
    bot = registry.get(bot_id)
    if not bot:
        raise HTTPException(404)
    await bot.stop()
    return {"success": True}

@app.delete("/api/bots/{bot_id}")
async def delete_bot(bot_id: str, _: str = Depends(require_auth)):
    await registry.delete(bot_id)
    return {"success": True}

@app.get("/api/bots/{bot_id}/logs")
async def get_logs(bot_id: str, limit: int = 100, _: str = Depends(require_auth)):
    bot = registry.get(bot_id)
    if not bot:
        raise HTTPException(404)
    return {"logs": bot.logs[-limit:]}

@app.websocket("/ws/{bot_id}")
async def ws(websocket: WebSocket, bot_id: str):
    await websocket.accept()
    bot = registry.get(bot_id)
    if not bot:
        await websocket.close()
        return
    bot.ws_clients.add(websocket)
    try:
        await websocket.send_json({"type": "init", "logs": bot.logs[-50:]})
        while True:
            await websocket.receive_text()
    except:
        pass
    finally:
        bot.ws_clients.discard(websocket)

@app.get("/api/stats")
async def stats(_: str = Depends(require_auth)):
    return registry.stats()

@app.get("/manifest.json")
async def manifest():
    return {
        "name": "Pavani Bot Creator V10", "short_name": "Pavani V10",
        "start_url": "/dashboard", "display": "standalone",
        "background_color": "#0F172A", "theme_color": "#6366F1",
        "icons": [
            {"src": "/static/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icon-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    }

@app.get("/sw.js")
async def service_worker():
    from fastapi.responses import FileResponse
    return FileResponse(Config.STATIC_DIR / "sw.js", media_type="application/javascript")

@app.get("/health")
async def health():
    return {"status": "healthy", "version": Config.VERSION}

@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 Shutting down...")
    for bot in registry.bots.values():
        await bot.stop()

# Mount static files
app.mount("/static", StaticFiles(directory=str(Config.STATIC_DIR)), name="static")

# Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
