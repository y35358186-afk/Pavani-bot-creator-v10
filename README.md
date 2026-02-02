# 🚀 Pavani Bot Creator V10

**Professional Bot Management Platform** - Enterprise-grade deployment, monitoring, and management.

[![Railway](https://img.shields.io/badge/Deploy%20on-Railway-0B0D0E?style=for-the-badge&logo=railway)](https://railway.app)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

---

## ✨ V10 Features

### 🎯 Core Features
- ✅ **Real Bot Deployment** - Actual subprocess execution
- ✅ **Telegram-Style Console** - Professional log viewer
- ✅ **Real-Time Monitoring** - WebSocket live updates
- ✅ **Process Management** - CPU/Memory tracking with psutil
- ✅ **Auto-Restart** - Crash detection and recovery
- ✅ **Rate Limiting** - Login attempt protection
- ✅ **Session Management** - 24-hour sessions
- ✅ **JSONL Logging** - Structured log files
- ✅ **Railway Ready** - One-click deployment
- ✅ **PWA Support** - Install as mobile app

### 💼 Professional Features
- ⚡ **Production Architecture** - Modular, clean code
- 📊 **Metrics & Analytics** - Messages, errors, uptime
- 🔒 **Enterprise Security** - Password hashing, session tokens
- 🎨 **Premium UI** - Modern gradient design
- 📱 **Mobile Optimized** - Touch-friendly interface
- 🔄 **Graceful Shutdown** - Proper cleanup on exit
- 📝 **API Documentation** - FastAPI auto-docs at `/api/docs`
- 🚨 **Health Checks** - `/health` endpoint for monitoring

---

## 🚀 Quick Deploy to Railway

### Method 1: One-Click Deploy

1. **Fork this repository**
2. **Go to [Railway](https://railway.app)**
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your fork**
6. **Add environment variable:**
   ```
   ADMIN_PASSWORD = @Xavier1
   ```
7. **Deploy!**

Railway will:
- ✅ Detect Python automatically
- ✅ Install dependencies
- ✅ Start the app
- ✅ Provide HTTPS URL

### Method 2: Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway init

# Set password
railway variables set ADMIN_PASSWORD=@Xavier1

# Deploy
railway up
```

---

## 💻 Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/pavani-bot-creator-v10.git
cd pavani-bot-creator-v10

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set password
export ADMIN_PASSWORD="@Xavier1"  # On Windows: set ADMIN_PASSWORD=@Xavier1

# Run
python app.py
```

Visit `http://localhost:8000`

---

## 📱 Mobile Development (Pydroid 3)

Perfect for Android development:

```bash
# In Pydroid 3 terminal
pip install fastapi uvicorn python-multipart websockets psutil pydantic

# Run
python app.py
```

---

## 🤖 Creating Your Bot

### 1. Create Bot File (my_bot.py)

```python
import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.running = True
        logger.info("🤖 Bot initialized")
    
    async def run(self):
        """Main bot loop"""
        logger.info("🚀 Bot starting...")
        
        while self.running:
            try:
                # Your bot logic here
                logger.info("📊 Processing messages...")
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                logger.info("⏹️  Shutdown signal received")
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                await asyncio.sleep(10)
        
        logger.info("✅ Bot stopped")

if __name__ == "__main__":
    bot = TelegramBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
```

### 2. Create Requirements (requirements.txt)

```txt
python-telegram-bot==20.7
requests==2.31.0
aiohttp==3.9.1
```

### 3. Deploy via Dashboard

1. **Login** to dashboard
2. **Click "Deploy New Bot"**
3. **Upload bot.py** (native file picker)
4. **Upload requirements.txt**
5. **Enter bot name**
6. **Click "Deploy"**
7. **Bot starts automatically!**

---

## 🎨 Dashboard Features

### Main Dashboard
- **📊 Statistics Panel** - Total bots, running, stopped, errors
- **🤖 Bot Cards** - Individual bot controls
- **📈 Metrics** - Messages, errors, uptime, CPU, memory
- **⚡ Quick Actions** - Deploy, restart, stop, delete

### Bot Console (Telegram-Style)
```
[2025-02-01 10:30:15] 🚀 Bot starting...
[2025-02-01 10:30:16] 📦 Installing dependencies...
[2025-02-01 10:30:20] ✅ Dependencies installed
[2025-02-01 10:30:20] ✅ Running (PID: 12345)
[2025-02-01 10:30:21] 📊 Processing messages...
```

Color-coded logs:
- 🟢 **Green** - System messages
- 🔵 **Blue** - Output
- 🟡 **Yellow** - Warnings
- 🔴 **Red** - Errors

### Real-Time Updates
- ⚡ WebSocket connection
- 📊 Live metrics
- 🔄 Auto-refresh every 5s
- 🎯 No page reload needed

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ADMIN_PASSWORD` | Dashboard password | `@Xavier1` |
| `SECRET_KEY` | Session encryption | Auto-generated |
| `PORT` | Server port | `8000` |
| `PYTHON_VERSION` | Python version | `3.11` |

### Railway Specific

Railway automatically sets:
- `PORT` - Application port
- `RAILWAY_STATIC_URL` - Public URL
- `RAILWAY_ENVIRONMENT` - Environment name

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `GET /api/auth/logout` - Logout

### Bots
- `POST /api/bots` - Deploy bot
- `GET /api/bots` - List all bots
- `GET /api/bots/{id}` - Get bot details
- `POST /api/bots/{id}/restart` - Restart bot
- `POST /api/bots/{id}/stop` - Stop bot
- `DELETE /api/bots/{id}` - Delete bot
- `GET /api/bots/{id}/logs` - Get logs

### WebSocket
- `WS /ws/{id}` - Real-time logs

### System
- `GET /api/stats` - Platform statistics
- `GET /health` - Health check
- `GET /api/docs` - API documentation

---

## 🏗️ Architecture

### Project Structure
```
pavani-bot-creator-v10/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── railway.json          # Railway config
├── railway.toml          # Railway settings
├── README.md             # This file
├── templates/            # HTML templates (auto-created)
├── static/               # Static files (auto-created)
├── bots/                 # Deployed bots (auto-created)
└── logs/                 # Bot logs (auto-created)
```

### Technology Stack
- **Backend:** FastAPI 0.109
- **ASGI Server:** Uvicorn with workers
- **WebSocket:** Native WebSockets
- **Process Management:** asyncio subprocess + psutil
- **Logging:** Python logging + JSONL
- **Auth:** SHA-256 + session tokens
- **Deployment:** Railway (Nixpacks)

---

## 🔒 Security Features

### Authentication
- ✅ Password hashing (SHA-256)
- ✅ Session tokens (UUID)
- ✅ HttpOnly cookies
- ✅ 24-hour session timeout
- ✅ Rate limiting (5 attempts/5 minutes)

### Bot Isolation
- ✅ Separate processes
- ✅ Independent file systems
- ✅ Resource limits (psutil monitoring)
- ✅ Graceful shutdown
- ✅ Crash detection

---

## 📈 Performance

### Limits
- **Max Bots:** 50 (configurable in `Config.MAX_BOTS`)
- **Max Log Lines:** 10,000 per bot
- **Session Timeout:** 24 hours
- **Log Retention:** 7 days

### Optimization
- ✅ Async I/O throughout
- ✅ Efficient log rotation
- ✅ WebSocket for real-time (no polling)
- ✅ Background tasks for monitoring
- ✅ Rate limiting on login

---

## 🐛 Troubleshooting

### Bot Won't Start
**Issue:** Bot shows "error" status

**Solutions:**
1. Check logs for error messages
2. Verify `requirements.txt` syntax
3. Test bot locally first
4. Ensure Python 3.11+ compatible

### WebSocket Not Connecting
**Issue:** Logs not updating in real-time

**Solutions:**
1. Check browser console for errors
2. Ensure HTTPS (Railway auto-provides)
3. Verify firewall/proxy settings

### Railway Deployment Fails
**Issue:** Build or deploy errors

**Solutions:**
1. Check Railway build logs
2. Verify `requirements.txt` is valid
3. Ensure `ADMIN_PASSWORD` is set
4. Check Python version compatibility

### High Memory Usage
**Issue:** Platform using too much RAM

**Solutions:**
1. Reduce `MAX_LOG_LINES` in Config
2. Stop unused bots
3. Implement log rotation (already included)
4. Upgrade Railway plan if needed

---

## 📝 Changelog

### V10.0.0 (Current)
- ✨ Complete rewrite with professional architecture
- ✨ Real subprocess management with psutil
- ✨ Telegram-style console
- ✨ Railway deployment support
- ✨ Auto-restart on crash
- ✨ Rate limiting
- ✨ JSONL structured logging
- ✨ WebSocket real-time updates
- ✨ Health check endpoint
- ✨ API documentation
- ✨ Session management
- ✨ Metrics dashboard

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/Amazing`)
3. Commit changes (`git commit -m 'Add Amazing'`)
4. Push to branch (`git push origin feature/Amazing`)
5. Open Pull Request

---

## 📄 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com)
- Deployed on [Railway](https://railway.app)
- Process management via [psutil](https://github.com/giampaolo/psutil)

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/pavani-bot-creator-v10/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/pavani-bot-creator-v10/discussions)
- **Documentation:** This README + `/api/docs` endpoint

---

<div align="center">

**Made with ❤️ for professional bot developers**

[🚀 Deploy on Railway](https://railway.app) • [📖 View Docs](/api/docs) • [⭐ Star on GitHub](https://github.com/yourusername/pavani-bot-creator-v10)

**Pavani Bot Creator V10** - Enterprise-grade bot management

</div>

