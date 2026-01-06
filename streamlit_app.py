import streamlit as st
import json
from datetime import datetime

st.set_page_config(page_title="Trading AI Signals", layout="centered")
st.title("📊 Trading AI – Live Signals")

@st.cache_data(ttl=300)
def load_signals():
    try:
        with open("signals.json", "r") as f:
            return json.load(f)
    except:
        return []

signals = load_signals()

if not signals:
    st.info("⏳ Aktuálně nejsou žádné silné signály.")
else:
    st.success(f"🔥 Aktivní silné signály: {len(signals)}")

    for s in signals[:5]:
        st.markdown("---")
        st.subheader(f"{s['name']} – {s['signal']}")

        st.write(f"**Confidence:** {int(s['confidence']*100)} %")
        st.write(f"**SL:** {round(s['sl_pct']*100,2)} %")
        st.write(f"**TP:** {round(s['tp_pct']*100,2)} %")

        if "profit_czk" in s:
            st.write(f"💰 Potenciál: {int(s['profit_czk'])} CZK")
        if "risk_czk" in s:
            st.write(f"⚠️ Riziko: {int(s['risk_czk'])} CZK")

st.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")
