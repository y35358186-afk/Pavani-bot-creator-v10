"""Bot Process Manager for V10"""
import asyncio, datetime, json, sys, os, psutil
from pathlib import Path
from typing import Optional, Set
from fastapi import WebSocket
from config import Config

class BotProcess:
    """Manages individual bot process"""
    
    def __init__(self, bot_id: str, name: str, bot_path: Path, req_path: Path):
        self.bot_id = bot_id
        self.name = name
        self.bot_path = bot_path
        self.req_path = req_path
        self.process: Optional[asyncio.subprocess.Process] = None
        self.pid: Optional[int] = None
        self.status = "initializing"
        self.created_at = datetime.datetime.now()
        self.started_at: Optional[datetime.datetime] = None
        self.logs = []
        self.log_file = Config.LOGS_DIR / f"{bot_id}.jsonl"
        self.metrics = {"messages": 0, "errors": 0, "warnings": 0, "restarts": 0}
        self.ws_clients: Set[WebSocket] = set()
        self.monitor_task: Optional[asyncio.Task] = None
    
    async def install_deps(self) -> bool:
        """Install requirements"""
        try:
            self.log("system", "📦 Installing dependencies...")
            if not self.req_path.exists():
                self.log("system", "ℹ️  No requirements.txt")
                return True
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "install", "-q", "-r", str(self.req_path),
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await proc.communicate()
            if proc.returncode == 0:
                self.log("system", "✅ Dependencies installed")
                return True
            else:
                self.log("error", f"❌ Install failed: {stderr.decode()[:200]}")
                return False
        except Exception as e:
            self.log("error", f"❌ Exception: {str(e)[:200]}")
            return False
    
    async def start(self) -> bool:
        """Start bot"""
        try:
            if not await self.install_deps():
                self.status = "error"
                return False
            self.log("system", f"🚀 Starting '{self.name}'...")
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, str(self.bot_path),
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                cwd=str(self.bot_path.parent)
            )
            self.pid = self.process.pid
            self.status = "running"
            self.started_at = datetime.datetime.now()
            self.log("system", f"✅ Running (PID: {self.pid})")
            asyncio.create_task(self._monitor_stdout())
            asyncio.create_task(self._monitor_stderr())
            self.monitor_task = asyncio.create_task(self._monitor_health())
            return True
        except Exception as e:
            self.status = "error"
            self.log("error", f"❌ Start failed: {str(e)[:200]}")
            return False
    
    async def _monitor_stdout(self):
        """Monitor output"""
        while self.process and self.process.returncode is None:
            line = await self.process.stdout.readline()
            if line:
                msg = line.decode('utf-8', errors='ignore').strip()
                if msg:
                    self.metrics["messages"] += 1
                    self.log("output", msg)
            else:
                break
    
    async def _monitor_stderr(self):
        """Monitor errors"""
        while self.process and self.process.returncode is None:
            line = await self.process.stderr.readline()
            if line:
                msg = line.decode('utf-8', errors='ignore').strip()
                if msg:
                    if "error" in msg.lower():
                        self.metrics["errors"] += 1
                        self.log("error", msg)
                    elif "warning" in msg.lower():
                        self.metrics["warnings"] += 1
                        self.log("warning", msg)
                    else:
                        self.log("info", msg)
            else:
                break
    
    async def _monitor_health(self):
        """Health monitoring"""
        while self.process and self.process.returncode is None:
            await asyncio.sleep(5)
            if self.process.returncode is not None:
                self.status = "crashed"
                self.log("error", "💀 Process crashed")
                if Config.ENABLE_AUTO_RESTART:
                    self.log("system", "🔄 Auto-restarting...")
                    await asyncio.sleep(3)
                    await self.start()
                break
    
    async def stop(self) -> bool:
        """Stop bot"""
        try:
            if not self.process or self.process.returncode is not None:
                return True
            self.log("system", "⏹️  Stopping...")
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=10)
            except asyncio.TimeoutError:
                self.log("warning", "⚠️  Force killing...")
                self.process.kill()
                await self.process.wait()
            self.status = "stopped"
            self.log("system", "✅ Stopped")
            if self.monitor_task:
                self.monitor_task.cancel()
            return True
        except Exception as e:
            self.log("error", f"❌ Stop error: {str(e)}")
            return False
    
    async def restart(self) -> bool:
        """Restart bot"""
        self.metrics["restarts"] += 1
        self.log("system", "🔄 Restarting...")
        await self.stop()
        await asyncio.sleep(2)
        return await self.start()
    
    def log(self, level: str, message: str):
        """Add log entry"""
        entry = {"ts": datetime.datetime.now().isoformat(), "level": level, "msg": message}
        self.logs.append(entry)
        if len(self.logs) > Config.MAX_LOG_LINES:
            self.logs = self.logs[-Config.MAX_LOG_LINES:]
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        asyncio.create_task(self._broadcast(entry))
    
    async def _broadcast(self, entry: dict):
        """Broadcast to WebSocket clients"""
        dead = set()
        for ws in self.ws_clients:
            try:
                await ws.send_json({"type": "log", "data": entry})
            except:
                dead.add(ws)
        self.ws_clients -= dead
    
    def get_uptime(self) -> str:
        """Format uptime"""
        if not self.started_at or self.status != "running":
            return "00:00:00"
        delta = datetime.datetime.now() - self.started_at
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def to_dict(self) -> dict:
        """Export status"""
        return {
            "bot_id": self.bot_id, "name": self.name, "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "uptime": self.get_uptime(), "pid": self.pid,
            "metrics": self.metrics, "log_count": len(self.logs),
            "ws_clients": len(self.ws_clients)
        }

class BotRegistry:
    """Central bot management"""
    
    def __init__(self):
        self.bots = {}
    
    async def deploy(self, name: str, bot_content: bytes, req_content: bytes) -> str:
        """Deploy new bot"""
        from fastapi import HTTPException
        if len(self.bots) >= Config.MAX_BOTS:
            raise HTTPException(400, f"Maximum {Config.MAX_BOTS} bots allowed")
        bot_id = os.urandom(4).hex()
        bot_path = Config.BOTS_DIR / f"{bot_id}_{name}.py"
        req_path = Config.BOTS_DIR / f"{bot_id}_requirements.txt"
        bot_path.write_bytes(bot_content)
        req_path.write_bytes(req_content)
        bot = BotProcess(bot_id, name, bot_path, req_path)
        if await bot.start():
            self.bots[bot_id] = bot
            return bot_id
        else:
            bot_path.unlink(missing_ok=True)
            req_path.unlink(missing_ok=True)
            raise HTTPException(500, "Failed to start bot")
    
    def get(self, bot_id: str):
        return self.bots.get(bot_id)
    
    def all(self):
        return [bot.to_dict() for bot in self.bots.values()]
    
    async def delete(self, bot_id: str):
        from fastapi import HTTPException
        bot = self.bots.get(bot_id)
        if not bot:
            raise HTTPException(404, "Bot not found")
        await bot.stop()
        bot.bot_path.unlink(missing_ok=True)
        bot.req_path.unlink(missing_ok=True)
        bot.log_file.unlink(missing_ok=True)
        del self.bots[bot_id]
    
    def stats(self):
        total = len(self.bots)
        running = sum(1 for b in self.bots.values() if b.status == "running")
        stopped = sum(1 for b in self.bots.values() if b.status == "stopped")
        error = sum(1 for b in self.bots.values() if b.status in ("error", "crashed"))
        return {"total": total, "running": running, "stopped": stopped, "error": error, "version": Config.VERSION}
