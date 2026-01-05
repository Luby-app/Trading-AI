# train_ai.py
import pandas as pd
import numpy as np
import yfinance as yf
import os
from sklearn.ensemble import RandomForestClassifier
from utils import calc_indicators
from config import instruments, instrument_names, lookback_days, interval

# Složka pro uložení tréninkových dat
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ============================
# Parametry modelu
# ============================
n_estimators = 150
random_state = 42

# ============================
# Funkce pro přípravu dat pro jeden instrument
# ============================
def prepare_data(symbol: str):
    """
    Stáhne historická data a připraví dataframe s features a target.
    """
    data = yf.download(symbol, period=f"{lookback_days}d", interval=interval)
    if data.empty:
        print(f"{symbol}: žádná data")
        return None

    close = data['Close'].squeeze()
    data = calc_indicators(data, close)

    # Features
    features = data[['EMA_diff', 'RSI', 'MACD_diff']].fillna(0)
    # Target: 1 pokud cena vzroste, -1 pokud klesne
    data['target'] = np.where(data['Close'].shift(-1) > data['Close'], 1, -1)
    
    df_train = features.copy()
    df_train['target'] = data['target']
    df_train.dropna(inplace=True)

    return df_train

# ============================
# Trénink a uložení dat pro všechny instrumenty
# ============================
def train_all():
    for symbol in instruments:
        df_train = prepare_data(symbol)
        if df_train is None:
            continue

        # Trénink Random Forest
        model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
        X = df_train[['EMA_diff', 'RSI', 'MACD_diff']]
        y = df_train['target']
        model.fit(X, y)

        # Uložení dat pro budoucí použití / analýzu
        filename = os.path.join(DATA_DIR, f"{instrument_names[symbol]}_train.csv")
        df_train.to_csv(filename, index=True)
        print(f"{symbol} ({instrument_names[symbol]}): uložen tréninkový dataset ({len(df_train)} řádků)")

if __name__ == "__main__":
    train_all()
