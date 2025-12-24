"""Configuration and constants."""

import os
from pathlib import Path

# Paths
BASE_DIR = Path("/app") if Path("/app").exists() else Path(".")
TOKENS_DIR = BASE_DIR / "tokens"
OUTPUT_DIR = BASE_DIR / "output"
TOKENS_FILE = TOKENS_DIR / "tokens.json"

# Ensure dirs exist
TOKENS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Azure App credentials
CLIENT_ID = os.environ.get("XBOX_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("XBOX_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:8080/auth/callback"

# OAuth URLs
OAUTH_AUTHORIZE = "https://login.live.com/oauth20_authorize.srf"
OAUTH_TOKEN = "https://login.live.com/oauth20_token.srf"
XBOX_USER_AUTH = "https://user.auth.xboxlive.com/user/authenticate"
XBOX_XSTS_AUTH = "https://xsts.auth.xboxlive.com/xsts/authorize"
SCOPES = "Xboxlive.signin Xboxlive.offline_access"

# Xbox API URLs
API_PROFILE = "https://profile.xboxlive.com"
API_TITLEHUB = "https://titlehub.xboxlive.com"
API_USERSTATS = "https://userstats.xboxlive.com"
API_ACHIEVEMENTS = "https://achievements.xboxlive.com"

# Defaults
DEFAULT_TIMEOUT = 60.0
DEFAULT_BATCH_SIZE = 50
DEFAULT_MAX_GAMES = 100

