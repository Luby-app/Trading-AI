# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from trading_signal import get_all_signals
from utils import calc_indicators
from config import interval

st.set_page_config(page_title="AI Trading Signals", layout="wide")
st.title("AI Trading Signals - CFD")

# ============================
# Real-time refresh
# ============================
st_autorefresh = st.experimental_data_editor if hasattr(st, "experimental_data_editor") else None
refresh_interval = 60  # sekundy
st.experimental_rerun() if st_autorefresh else None

# ============================
# Načtení signálů
# ============================
st.subheader("Aktuální signály")
signals = get_all_signals()

if not signals:
    st.warning("Žádné silné signály pro tento okamžik.")
else:
    df_signals = pd.DataFrame(signals)
    df_display = df_signals[['instrument', 'price', 'signal', 'SL', 'TP', 'probability', 'profit_CZK']]
    st.dataframe(df_display, use_container_width=True)

    # ============================
    # Graf pro vybraný instrument
    # ============================
    st.subheader("Graf cen + indikátory")
    selected_instrument = st.selectbox("Vyber instrument:", df_signals['instrument'])

    # Najdi ticker podle názvu
    ticker = [k for k,v in signals[0].items() if v == selected_instrument]
    if not ticker:
        ticker = None
    else:
        ticker = ticker[0]

    if ticker:
        # Stažení dat pro graf
        import yfinance as yf
        data = yf.download(ticker, period="5d", interval=interval)
        close = data['Close'].squeeze()
        data = calc_indicators(data, close)

        fig = go.Figure()

        # Cena + EMA
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close', line=dict(color='black')))
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA10'], mode='lines', name='EMA10', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA50'], mode='lines', name='EMA50', line=dict(color='orange')))

        # MACD + signal v odděleném subplotu
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', yaxis='y2', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD_signal'], mode='lines', name='MACD Signal', yaxis='y2', line=dict(color='red')))

        # RSI v třetím subplotu
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', yaxis='y3', line=dict(color='purple')))

        fig.update_layout(
            yaxis=dict(title="Cena"),
            yaxis2=dict(title="MACD", overlaying='y', side='right'),
            yaxis3=dict(title="RSI", overlaying='y', side='left', position=0.15),
            legend=dict(orientation="h"),
            margin=dict(l=40, r=40, t=40, b=40)
        )

        st.plotly_chart(fig, use_container_width=True)
