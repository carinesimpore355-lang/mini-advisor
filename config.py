"""
config.py — Configuration centrale du mini-advisor.

Tout ce qui est "réglable" (seuils, clés API, chemins) vit ici.
Règle d'or : jamais de "magic numbers" éparpillés dans le code.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charge les variables du fichier .env (email, telegram, etc.)
load_dotenv()

# ===== CHEMINS =====
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"

# ===== APIS =====
# CoinGecko est gratuit, sans clé requise (rate limit: 10-30 appels/min)
COINGECKO_API = "https://api.coingecko.com/api/v3"

# ===== SEUILS DE L'AGENT IA =====
# Ces seuils déterminent les recommandations. Tu peux les ajuster.
THRESHOLDS = {
    # Concentration : si un actif > 40% du portfolio → risque
    "max_allocation_pct": 40.0,

    # Volatilité : au-dessus = risqué (volatilité journalière sur 30j)
    "high_volatility_pct": 8.0,

    # Variation 24h pour alerte marché
    "market_alert_pct": 10.0,

    # Si un actif a chuté de X% sur 30j → signal de vente à étudier
    "stop_loss_pct": -25.0,

    # Si un actif a monté de X% sur 30j → prendre profits ?
    "take_profit_pct": 50.0,

    # Diversification minimale (nb d'actifs)
    "min_assets_diversified": 4,
}

# ===== NOTIFICATIONS =====
EMAIL_CONFIG = {
    "sender": os.getenv("EMAIL_SENDER", ""),
    "password": os.getenv("EMAIL_PASSWORD", ""),  # Mot de passe d'application Gmail
    "receiver": os.getenv("EMAIL_RECEIVER", ""),
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
}

TELEGRAM_CONFIG = {
    "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
}

# ===== UI =====
APP_TITLE = "🚀 Mini Advisor — Votre conseiller IA"
CURRENCY = "usd"  # usd, eur, cad...
