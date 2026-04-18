# 🚀 Mini Advisor — Conseiller IA pour Petit Portefeuille Crypto

Plateforme légère pour suivre, analyser et recevoir des recommandations sur un portefeuille crypto. Pensée pour un investisseur avec ~1000$ qui veut apprendre.

## ✨ Fonctionnalités

- 📊 **Dashboard interactif** (Streamlit) avec allocation, P&L, métriques clés
- 🤖 **Agent IA** qui recommande BUY/SELL/HOLD/REBALANCE basé sur 5 règles métier
- ❤️ **Score de santé** (0-100) du portefeuille
- 🎲 **Simulateur** "si j'avais investi X$ il y a 30 jours"
- 🔔 **Notifications** email (Gmail) + Telegram
- 📡 **Données live** via CoinGecko (gratuit, sans clé API)

## 🛠️ Stack

- **Backend** : Python 3.10+
- **Frontend** : Streamlit
- **Data** : CoinGecko API (gratuit)
- **Storage** : JSON local
- **Graphiques** : Plotly

## 🚀 Installation (5 minutes)

```bash
# 1. Cloner / télécharger le projet
cd mini-advisor

# 2. Environnement virtuel
python -m venv venv
source venv/bin/activate          # Mac/Linux
# venv\Scripts\activate           # Windows

# 3. Dépendances
pip install -r requirements.txt

# 4. (Optionnel) Configurer les notifications
cp .env.example .env
# Puis éditer .env avec tes credentials

# 5. Lancer
streamlit run app.py
```

L'app s'ouvre sur `http://localhost:8501`.

## 🔔 Configuration des notifications

### Telegram (recommandé — plus simple)
1. Ouvrir Telegram → chercher `@BotFather`
2. Commande `/newbot` → suivre les instructions → récupérer le **token**
3. Envoyer un message à ton bot
4. Aller sur `https://api.telegram.org/bot<TOKEN>/getUpdates` → noter ton `chat.id`
5. Mettre `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID` dans `.env`

### Gmail
1. Activer la 2FA : https://myaccount.google.com/security
2. Créer un mot de passe d'application : https://myaccount.google.com/apppasswords
3. Mettre `EMAIL_SENDER`, `EMAIL_PASSWORD`, `EMAIL_RECEIVER` dans `.env`

## 📂 Structure

```
mini-advisor/
├── app.py              # Interface Streamlit
├── config.py           # Seuils et config
├── requirements.txt
├── .env                # Tes secrets (ne pas commit)
├── modules/
│   ├── data_fetcher.py # API CoinGecko
│   ├── portfolio.py    # CRUD portefeuille
│   ├── analyzer.py     # Métriques financières
│   ├── ai_agent.py     # Recommandations IA
│   └── notifier.py     # Email + Telegram
└── data/
    └── portfolio.json  # Tes holdings (auto-généré)
```

## ⚙️ Personnaliser l'IA

Tous les seuils sont dans `config.py` :

```python
THRESHOLDS = {
    "max_allocation_pct": 40.0,      # Alerte si 1 actif > 40%
    "high_volatility_pct": 8.0,      # Volatilité "élevée"
    "stop_loss_pct": -25.0,          # Signal vente si -25% sur 30j
    "take_profit_pct": 50.0,         # Signal prise de profit si +50%
    ...
}
```

## 🌐 Déploiement gratuit

1. Pousser le code sur GitHub (sans `.env` !)
2. Aller sur https://share.streamlit.io
3. Connecter ton repo
4. Ajouter tes secrets dans l'onglet "Secrets"
5. Déploiement automatique ✅

## 📅 Notifications automatiques quotidiennes

Sur Linux/Mac, ajoute dans ton crontab (`crontab -e`) :

```bash
# Tous les jours à 9h
0 9 * * * cd /chemin/vers/mini-advisor && venv/bin/python -c "from modules.portfolio import Portfolio; from modules.analyzer import Analyzer; from modules.ai_agent import AIAgent; from modules.notifier import Notifier; p=Portfolio(); a=Analyzer(p.get_all()); ag=AIAgent(a); Notifier.send_telegram(Notifier.format_recommendations(ag.analyze(), a.get_health_score()))"
```

Ou plus simple : un script `daily_report.py` (voir section Améliorations).

## 🗺️ Roadmap

- [ ] Connexion wallet MetaMask (via web3.py)
- [ ] Support des actions/ETF (via Yahoo Finance)
- [ ] Intégration OpenAI pour conseils en langage naturel
- [ ] Backtesting de stratégies
- [ ] Historique de performance du portefeuille
- [ ] Export PDF des rapports

## ⚠️ Disclaimer

Outil **éducatif**. Pas de conseil en investissement. DYOR (Do Your Own Research).

## 📄 Licence

MIT
