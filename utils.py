# utils.py
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

# ============================
# VÝPOČET INDIKÁTORŮ
# ============================
def calc_indicators(df: pd.DataFrame, close: pd.Series) -> pd.DataFrame:
    """
    Přidá do dataframe indikátory:
    - EMA10, EMA50
    - RSI
    - MACD a MACD_signal
    - EMA_diff a MACD_diff
    """
    df = df.copy()

    # EMA
    df['EMA10'] = EMAIndicator(close, window=10).ema_indicator()
    df['EMA50'] = EMAIndicator(close, window=50).ema_indicator()
    df['EMA_diff'] = df['EMA10'] - df['EMA50']

    # RSI
    df['RSI'] = RSIIndicator(close, window=14).rsi()

    # MACD
    macd = MACD(close)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_diff'] = df['MACD'] - df['MACD_signal']

    return df


# ============================
# VÝPOČET STOP LOSS / TAKE PROFIT
# ============================
def calc_SL_TP(price: float, signal: str, sl_pct: float = 0.5, tp_pct: float = 1.5):
    """
    Vrátí SL a TP na základě aktuální ceny a signálu.
    - sl_pct, tp_pct jsou v procentech
    - pro LONG: SL < cena < TP
    - pro SHORT: TP < cena < SL
    """
    if signal == "LONG":
        sl = price * (1 - sl_pct / 100)
        tp = price * (1 + tp_pct / 100)
    elif signal == "SHORT":
        sl = price * (1 + sl_pct / 100)
        tp = price * (1 - tp_pct / 100)
    else:
        sl = tp = None

    return sl, tp
