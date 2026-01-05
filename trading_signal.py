# trading_signal.py
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from utils import calc_indicators, calc_SL_TP
from config import instruments, instrument_names, trade_risks, lookback_days, interval, prob_threshold
from ta.volatility import AverageTrueRange

LOOKAHEAD = 3  # počet svíček dopředu pro target
ATR_WINDOW = 14  # perioda pro ATR

# ============================
# FUNKCE PRO VÝPOČET SIGNÁLU
# ============================
def get_signal(symbol, trade_risk_czk):
    try:
        data = yf.download(symbol, period=f"{lookback_days}d", interval=interval)
        if data.empty:
            return {"ticker": symbol, "instrument": instrument_names.get(symbol, symbol), "error": "no data"}

        close = data['Close'].squeeze()
        data = calc_indicators(data, close)

        # Features
        features = data[['EMA_diff', 'RSI', 'MACD_diff']].fillna(0)
        # Target - lookahead 3 svíčky
        data['target'] = np.where(data['Close'].shift(-LOOKAHEAD) > data['Close'], 1, -1)

        # Model
        model = RandomForestClassifier(n_estimators=150, random_state=42)
        model.fit(features, data['target'])

        latest_features = features.iloc[-1].values.reshape(1, -1)
        proba = model.predict_proba(latest_features)[0]
        class_order = model.classes_
        if list(class_order) == [-1, 1]:
            long_prob = proba[1]
            short_prob = proba[0]
        else:
            long_prob = proba[0]
            short_prob = proba[1]

        signal = "LONG" if long_prob > 0.6 else "SHORT" if short_prob > 0.6 else "HOLD"
        latest_close = float(data['Close'].iloc[-1])
        probability_percent = max(long_prob, short_prob) * 100

        if probability_percent < prob_threshold or signal == "HOLD":
            return None

        # ATR pro adaptivní SL/TP
        atr = AverageTrueRange(data['High'], data['Low'], data['Close'], window=ATR_WINDOW).average_true_range().iloc[-1]
        sl, tp = calc_SL_TP(latest_close, signal, atr=atr, sl_mult=1, tp_mult=2)

        profit_CZK = abs(tp - latest_close) / latest_close * trade_risk_czk * 1000 if tp and sl else None

        return {
            "ticker": symbol,
            "instrument": instrument_names.get(symbol, symbol),
            "price": latest_close,
            "signal": signal,
            "SL": sl,
            "TP": tp,
            "probability": probability_percent,
            "profit_CZK": profit_CZK
        }

    except Exception as e:
        return {"ticker": symbol, "instrument": instrument_names.get(symbol, symbol), "error": str(e)}


# ============================
# FUNKCE PRO VŠECHNY INSTRUMENTY
# ============================
def get_all_signals():
    results = []
    for i, symbol in enumerate(instruments):
        result = get_signal(symbol, trade_risks[i])
        if result is not None:
            results.append(result)
    return results
