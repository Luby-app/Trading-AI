# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from trading_signal import get_all_signals
from utils import calc_indicators
from config import interval
import yfinance as yf

# ============================
# Nastavení stránky
# ============================
st.set_page_config(page_title="AI Trading Signals", layout="wide")
st.title("AI Trading Signals - CFD")

# ============================
# Tlačítko pro manuální refresh
# ============================
refresh_clicked = st.button("Aktualizovat signály")

# ============================
# Načtení signálů
# ============================
st.subheader("Aktuální signály")
signals = get_all_signals()  # vždy se zavolá při načtení nebo po kliknutí

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

    # Správné získání tickeru
    selected_row = df_signals[df_signals['instrument'] == selected_instrument]
    if not selected_row.empty:
        ticker = selected_row['ticker'].values[0]

        data = yf.download(ticker, period="5d", interval=interval)
        if not data.empty:
            close = data['Close'].squeeze()
            data = calc_indicators(data, close)

            fig = go.Figure()

            # Cena + EMA
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close', line=dict(color='black')))
            fig.add_trace(go.Scatter(x=data.index, y=data['EMA10'], mode='lines', name='EMA10', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=data.index, y=data['EMA50'], mode='lines', name='EMA50', line=dict(color='orange')))

            # MACD + signal
            fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', yaxis='y2', line=dict(color='green')))
            fig.add_trace(go.Scatter(x=data.index, y=data['MACD_signal'], mode='lines', name='MACD Signal', yaxis='y2', line=dict(color='red')))

            # RSI
            fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', yaxis='y3', line=dict(color='purple')))

            fig.update_layout(
                yaxis=dict(title="Cena"),
                yaxis2=dict(title="MACD", overlaying='y', side='right'),
                yaxis3=dict(title="RSI", overlaying='y', side='left', position=0.15),
                legend=dict(orientation="h"),
                margin=dict(l=40, r=40, t=40, b=40)
            )

            st.plotly_chart(fig, use_container_width=True)
