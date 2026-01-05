# signal.py
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from utils import calc_indicators, calc_SL_TP
from config import instruments, instrument_names, trade_risks, lookback_days, interval, prob_threshold

# ============================
# FUNKCE PRO VÝPOČET SIGNÁLU
# ============================
def get_signal(symbol, trade_risk_czk):
    """
    Vrací dict se signálem pro jeden instrument:
    - instrument, cena, LONG/SHORT/HOLD
    - SL/TP v procentech
    - pravděpodobnost a odhad profit v CZK
    """
    try:
        # Stažení historických dat
        data = yf.download(symbol, period=f"{lookback_days}d", interval=interval)
        if data.empty:
            return {"instrument": instrument_names.get(symbol, symbol), "error": "no data"}

        close = data['Close'].squeeze()

        # Výpočet indikátorů přes utilitu
        data = calc_indicators(data, close)

        # Features pro Random Forest
        features = data[['EMA_diff', 'RSI', 'MACD_diff']].fillna(0)
        data['target'] = np.where(data['Close'].shift(-1) > data['Close'], 1, -1)

        # Trénink modelu (můžeme později přepnout na predikci z natrénovaného modelu)
        model = RandomForestClassifier(n_estimators=150, random_state=42)
        model.fit(features, data['target'])

        latest_features = features.iloc[-1].values.reshape(1, -1)
        proba = model.predict_proba(latest_features)[0]
        # Kontrola pořadí tříd
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

        # Filtrace slabých signálů
        if probability_percent < prob_threshold or signal == "HOLD":
            return None

        # SL / TP v procentech přes utilitu
        sl, tp = calc_SL_TP(latest_close, signal, sl_pct=0.5, tp_pct=1.5)

        # Potenciální profit v CZK
        profit_CZK = abs(tp - latest_close) / latest_close * trade_risk_czk * 1000 if tp and sl else None

        return {
            "instrument": instrument_names.get(symbol, symbol),
            "price": latest_close,
            "signal": signal,
            "SL": sl,
            "TP": tp,
            "probability": probability_percent,
            "profit_CZK": profit_CZK
        }

    except Exception as e:
        return {"instrument": instrument_names.get(symbol, symbol), "error": str(e)}


# ============================
# FUNKCE PRO VŠECHNY INSTRUMENTY
# ============================
def get_all_signals():
    """
    Vrací seznam silných signálů pro všechny instrumenty
    """
    results = []
    for i, symbol in enumerate(instruments):
        result = get_signal(symbol, trade_risks[i])
        if result is not None:
            results.append(result)
    return results
