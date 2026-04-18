"""
daily_report.py — Script autonome pour envoi quotidien du rapport.

Peut être lancé via cron (Linux/Mac), Task Scheduler (Windows),
ou GitHub Actions (gratuit, voir .github/workflows/daily.yml).

Exemple cron (tous les jours à 9h) :
    0 9 * * * cd /chemin/mini-advisor && venv/bin/python daily_report.py
"""
from modules.portfolio import Portfolio
from modules.analyzer import Analyzer
from modules.ai_agent import AIAgent
from modules.notifier import Notifier


def run_daily_report():
    portfolio = Portfolio()
    holdings = portfolio.get_all()

    if not holdings:
        print("Portefeuille vide — rien à envoyer.")
        return

    analyzer = Analyzer(holdings)
    agent = AIAgent(analyzer)

    recos = agent.analyze()
    health = analyzer.get_health_score()

    body = Notifier.format_recommendations(recos, health)

    # Ajoute un filtre : on n'envoie QUE s'il y a des alertes importantes
    has_urgent = any(r["severity"] == "HIGH" for r in recos)

    subject = "🚨 Mini Advisor — ALERTE" if has_urgent else "📊 Mini Advisor — Rapport du jour"

    results = Notifier.send_all(subject, body)
    for channel, result in results.items():
        status = "✅" if result["ok"] else "❌"
        print(f"{status} {channel}: {result['msg']}")


if __name__ == "__main__":
    run_daily_report()
