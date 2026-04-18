"""
app.py — Interface Streamlit du Mini Advisor.

Lancer avec :  streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import APP_TITLE, CURRENCY
from modules.portfolio import Portfolio
from modules.data_fetcher import DataFetcher
from modules.analyzer import Analyzer
from modules.ai_agent import AIAgent
from modules.notifier import Notifier


# ===== CONFIG PAGE =====
st.set_page_config(
    page_title="Mini Advisor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===== INIT =====
portfolio = Portfolio()
fetcher = DataFetcher()


# ===== SIDEBAR : Gestion du portefeuille =====
with st.sidebar:
    st.title("💼 Portefeuille")

    # --- Ajouter un actif ---
    with st.expander("➕ Ajouter un actif", expanded=True):
        # Dropdown avec les top 50 cryptos (plus simple que de taper l'ID)
        top_coins = fetcher.get_top_coins(50)

        if top_coins:
            coin_options = {f"{c['name']} ({c['symbol'].upper()})": c for c in top_coins}
            selection = st.selectbox(
                "Actif",
                options=list(coin_options.keys()),
                help="Choisissez parmi le top 50 crypto"
            )
            selected_coin = coin_options[selection]

            quantity = st.number_input(
                "Quantité", min_value=0.0, step=0.001, format="%.6f"
            )
            buy_price = st.number_input(
                f"Prix d'achat moyen ({CURRENCY.upper()})",
                min_value=0.0,
                value=float(selected_coin.get("current_price", 0)),
                step=0.01,
            )

            if st.button("✅ Ajouter", use_container_width=True):
                if quantity > 0 and buy_price > 0:
                    portfolio.add(
                        coin_id=selected_coin["id"],
                        symbol=selected_coin["symbol"],
                        quantity=quantity,
                        buy_price=buy_price,
                    )
                    st.success(f"{selected_coin['symbol'].upper()} ajouté !")
                    st.rerun()
                else:
                    st.error("Quantité et prix doivent être > 0")
        else:
            st.warning("API CoinGecko indisponible. Réessayez.")

    # --- Supprimer un actif ---
    holdings = portfolio.get_all()
    if holdings:
        with st.expander("🗑️ Supprimer un actif"):
            to_remove = st.selectbox(
                "Actif à retirer",
                options=[h["symbol"] for h in holdings],
                key="remove_select"
            )
            if st.button("Supprimer", use_container_width=True):
                coin_id = next(h["coin_id"] for h in holdings if h["symbol"] == to_remove)
                portfolio.remove(coin_id)
                st.rerun()

        if st.button("⚠️ Reset complet", use_container_width=True):
            portfolio.clear()
            st.rerun()


# ===== MAIN =====
st.title(APP_TITLE)
st.caption("Votre conseiller IA pour petits portefeuilles crypto 🤖")

holdings = portfolio.get_all()

if not holdings:
    st.info("👈 Commencez par ajouter des actifs dans la barre latérale !")
    st.markdown("""
    ### 🎯 Comment ça marche ?
    1. **Ajoutez vos actifs** crypto dans la sidebar (ceux que vous possédez déjà)
    2. L'app **récupère les prix en temps réel** via CoinGecko
    3. L'**agent IA analyse** votre portefeuille et vous recommande des actions
    4. Vous pouvez **recevoir des notifications** par Telegram/Email

    💡 *Pour tester, ajoutez par exemple 0.01 BTC et 0.1 ETH.*
    """)
    st.stop()

# Si on a des holdings, on analyse
analyzer = Analyzer(holdings)
agent = AIAgent(analyzer)
enriched = analyzer.get_enriched_holdings()

# ===== SECTION 1 : MÉTRIQUES CLÉS =====
st.header("📊 Vue d'ensemble")

total_value = analyzer.get_total_value()
total_invested = analyzer.get_total_invested()
pnl, pnl_pct = analyzer.get_total_pnl()
health = analyzer.get_health_score()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Valeur actuelle", f"${total_value:,.2f}")
with col2:
    st.metric("📥 Capital investi", f"${total_invested:,.2f}")
with col3:
    st.metric(
        "📈 P&L total",
        f"${pnl:+,.2f}",
        delta=f"{pnl_pct:+.2f}%",
        delta_color="normal" if pnl >= 0 else "inverse",
    )
with col4:
    st.metric(f"❤️ Santé {health['grade']}", f"{health['score']}/100")


# ===== SECTION 2 : HEALTH SCORE DÉTAILLÉ =====
with st.expander("🔍 Détails du score de santé", expanded=False):
    sub = health["subscores"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Diversification", f"{sub['diversification']}/40")
    c2.metric("Performance", f"{sub['performance']}/30")
    c3.metric("Volatilité", f"{sub['volatility']}/30")

    st.markdown("**Analyse détaillée :**")
    for d in health["details"]:
        st.write(d)


# ===== SECTION 3 : RECOMMANDATIONS IA =====
st.header("🤖 Recommandations de l'agent IA")

recos = agent.analyze()
severity_colors = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
action_icons = {
    "BUY": "🟢", "SELL": "🔴", "HOLD": "⚪",
    "REBALANCE": "⚖️", "ALERT": "⚠️", "INFO": "ℹ️"
}

for r in recos:
    icon = action_icons.get(r["action"], "•")
    sev = severity_colors.get(r["severity"], "")
    with st.container(border=True):
        st.markdown(f"{sev} {icon} **{r['action']} — {r['asset']}**")
        st.write(r["reason"])


# ===== SECTION 4 : TABLE DES HOLDINGS =====
st.header("💼 Mes actifs")

df = pd.DataFrame(enriched)
df_display = df[[
    "symbol", "quantity", "buy_price", "current_price",
    "invested", "current_value", "pnl", "pnl_pct", "change_24h"
]].copy()
df_display.columns = [
    "Symbole", "Quantité", "Prix achat", "Prix actuel",
    "Investi ($)", "Valeur ($)", "P&L ($)", "P&L %", "24h %"
]

# Format propre
st.dataframe(
    df_display.style.format({
        "Quantité": "{:.6f}",
        "Prix achat": "${:.2f}",
        "Prix actuel": "${:.2f}",
        "Investi ($)": "${:.2f}",
        "Valeur ($)": "${:.2f}",
        "P&L ($)": "${:+.2f}",
        "P&L %": "{:+.2f}%",
        "24h %": "{:+.2f}%",
    }).map(
        lambda v: "color: green" if isinstance(v, (int, float)) and v > 0 else "color: red",
        subset=["P&L ($)", "P&L %", "24h %"]
    ),
    use_container_width=True,
    hide_index=True,
)


# ===== SECTION 5 : GRAPHIQUES =====
st.header("📈 Visualisations")

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Allocation du portefeuille")
    allocation = analyzer.get_allocation()
    if allocation:
        fig_pie = px.pie(
            values=[a["value"] for a in allocation],
            names=[a["symbol"] for a in allocation],
            hole=0.4,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

with col_g2:
    st.subheader("P&L par actif")
    fig_bar = go.Figure(data=[
        go.Bar(
            x=df["symbol"],
            y=df["pnl"],
            marker_color=["green" if v >= 0 else "red" for v in df["pnl"]],
            text=[f"{v:+.0f}$" for v in df["pnl"]],
            textposition="outside",
        )
    ])
    fig_bar.update_layout(yaxis_title=f"P&L ({CURRENCY.upper()})", xaxis_title="")
    st.plotly_chart(fig_bar, use_container_width=True)


# ===== SECTION 6 : SIMULATION "WHAT IF" =====
st.header("🎲 Simulation : si j'avais investi...")

col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
with col_s1:
    sim_options = {f"{c['name']} ({c['symbol'].upper()})": c["id"] for c in fetcher.get_top_coins(20)}
    sim_coin = st.selectbox("Crypto", options=list(sim_options.keys()), key="sim_coin")
with col_s2:
    sim_amount = st.number_input("Montant ($)", min_value=10.0, value=100.0, step=10.0)
with col_s3:
    st.write("")
    st.write("")
    run_sim = st.button("Simuler", use_container_width=True)

if run_sim:
    result = analyzer.simulate_investment(sim_options[sim_coin], sim_amount)
    if "error" in result:
        st.error(result["error"])
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Investi il y a 30j", f"${result['invested']:.2f}")
        c2.metric("Valeur aujourd'hui", f"${result['final_value']:.2f}")
        c3.metric(
            "Gain/Perte",
            f"${result['pnl']:+.2f}",
            delta=f"{result['pnl_pct']:+.2f}%"
        )


# ===== SECTION 7 : NOTIFICATIONS =====
st.header("🔔 Notifications")

col_n1, col_n2 = st.columns(2)
with col_n1:
    if st.button("📧 Envoyer rapport par email", use_container_width=True):
        body = Notifier.format_recommendations(recos, health)
        ok, msg = Notifier.send_email("🚀 Mini Advisor — Rapport du jour", body)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

with col_n2:
    if st.button("📲 Envoyer rapport sur Telegram", use_container_width=True):
        body = Notifier.format_recommendations(recos, health)
        ok, msg = Notifier.send_telegram(body)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

st.caption(
    "💡 Configurez vos credentials dans le fichier `.env` (voir `.env.example`). "
    "Vous pouvez aussi planifier un envoi quotidien via `cron` ou GitHub Actions."
)

# ===== FOOTER =====
st.divider()
st.caption(
    "⚠️ **Disclaimer** : Cet outil fournit des analyses automatisées à titre éducatif uniquement. "
    "Ce n'est pas un conseil en investissement. Faites toujours vos propres recherches (DYOR)."
)
