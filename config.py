"""Configuration for Pavani Bot Creator V10"""
import os, hashlib, uuid
from pathlib import Path

class Config:
    VERSION = "10.0.0"
    APP_NAME = "Pavani Bot Creator V10"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", str(uuid.uuid4()))
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "@Xavier1")
    PASSWORD_HASH = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()
    
    # Paths
    BASE_DIR = Path(__file__).parent
    BOTS_DIR = BASE_DIR / "bots"
    LOGS_DIR = BASE_DIR / "logs"
    STATIC_DIR = BASE_DIR / "static"
    TEMPLATES_DIR = BASE_DIR / "templates"
    
    # Limits
    MAX_BOTS = 50
    MAX_LOG_LINES = 10000
    SESSION_TIMEOUT_HOURS = 24
    
    # Features
    ENABLE_METRICS = True
    ENABLE_AUTO_RESTART = True
    LOG_ROTATION_DAYS = 7

# Create directories
for dir_path in [Config.BOTS_DIR, Config.LOGS_DIR, Config.STATIC_DIR, Config.TEMPLATES_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)
