import streamlit as st
from signals import get_all_signals

st.set_page_config(
    page_title="Trading Signals",
    page_icon="📈",
    layout="centered"
)

st.title("📊 AI Trading Signals")

st.markdown("""
Tato aplikace zobrazuje aktuální silné signály pro vybrané indexy a komodity.
Signály generuje Random Forest model s EMA, MACD a RSI indikátory.
SL = Stop Loss, TP = Take Profit, Profit = odhadovaný zisk v CZK.
""")

# ============================
# Získání aktuálních signálů
# ============================
with st.spinner("Generuji signály..."):
    signals = get_all_signals()

if not signals:
    st.info("Momentálně nejsou žádné silné signály podle nastavené pravděpodobnosti.")
else:
    # Převod na DataFrame pro hezké zobrazení
    df = st.dataframe(signals)

    st.markdown(f"Celkem silných signálů: **{len(signals)}**")

    # Doporučený top signál (nejvyšší pravděpodobnost)
    top_signal = max(signals, key=lambda x: x.get("probability", 0))
    st.subheader("💡 Nejpravděpodobnější obchod")
    st.write(f"Instrument: **{top_signal['instrument']}**")
    st.write(f"Signál: **{top_signal['signal']}**")
    st.write(f"Cena: {top_signal['price']:.2f}")
    st.write(f"SL: {top_signal['SL']:.2f}, TP: {top_signal['TP']:.2f}")
    st.write(f"Pravděpodobnost: {top_signal['probability']:.2f}%")
    st.write(f"Odhadovaný profit: {top_signal['profit_CZK']:.2f} CZK")
