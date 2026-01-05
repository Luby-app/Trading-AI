# streamlit_app.py
import streamlit as st
import pandas as pd
from trading_signal import get_all_signals

# ============================
# Nastavení stránky
# ============================
st.set_page_config(page_title="AI Trading Signals", layout="wide")
st.title("AI Trading Signals - CFD")

# ============================
# Tlačítko pro manuální refresh
# ============================
st.button("Aktualizovat signály")  # jen spustí refresh, bez experimental_rerun

# ============================
# Načtení signálů
# ============================
st.subheader("Aktuální signály")

signals = get_all_signals()

if not signals:
    st.warning("Žádné silné signály pro tento okamžik.")
else:
    df_signals = pd.DataFrame(signals)

    # Doplnit chybějící sloupce pro bezpečnost
    expected_columns = ['instrument', 'price', 'signal', 'SL', 'TP', 'probability', 'profit_CZK']
    for col in expected_columns:
        if col not in df_signals.columns:
            df_signals[col] = None

    # Vybrat jen potřebné sloupce
    df_display = df_signals[expected_columns]

    # Zobrazit tabulku
    st.dataframe(df_display, use_container_width=True)
