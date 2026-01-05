# config.py

# ============================
# INSTRUMENTY A NÁZVY
# ============================
instrument_names = {
    "^N225": "JP225",
    "EUR=X": "EU50",
    "CC=F": "COCOA",
    "SI=F": "SILVER",
    "GC=F": "GOLD",
    "CL=F": "CRUDE OIL",
    "NG=F": "NAT GAS",
    "ZC=F": "CORN",
    "ZS=F": "SOYBEAN",
    "ZW=F": "WHEAT",
    "SB=F": "SUGAR",
    "HG=F": "COPPER",
    "PL=F": "PLATINUM",
    "PA=F": "PALLADIUM",
    "RB=F": "RBOB GASOLINE",
    # 16. instrument přidáme (např. SILVER, již v seznamu)
}

# Seznam tickerů
instruments = list(instrument_names.keys())

# ============================
# RIZIKO NA OBCHOD (XTB CFD)
# ============================
trade_risks = [
    1678, 710, 1215, 7479,
    2000, 1500, 1200, 1000,
    1100, 950, 800, 1300,
    2500, 2700, 1800, 750   # poslední 16. trade_risk
]

# ============================
# PARAMETRY DAT A MODELŮ
# ============================
lookback_days = 30          # kolik dní dat stáhnout
interval = "30m"            # časový interval svíček
prob_threshold = 80         # filtr silných signálů (%)
