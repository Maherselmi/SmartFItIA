#!/usr/bin/env python3


import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

# -------------------------------------------------
# 1) MORE EXPENSIVE BASES (2025 premium gym vibes)
# -------------------------------------------------
TYPES = [
    "Premium Mensuel",
    "Premium Hebdomadaire",
    "Basique Mensuel",
    "Basique Hebdomadaire",
    "Etudiant Mensuel",
    "Pro Annuel",
    "Family Mensuel",
]

# bumped versions
BASE_PRICE = {
    "Premium Mensuel": 69.99,       # was 49.99
    "Premium Hebdomadaire": 19.99,  # was 14.99
    "Basique Mensuel": 39.99,       # was 29.99
    "Basique Hebdomadaire": 12.99,  # was 9.99
    "Etudiant Mensuel": 27.99,      # was 19.99
    "Pro Annuel": 699.99,           # was 499.99
    "Family Mensuel": 79.99,        # was 59.99
}

def base_duration_days(t):
    if "Hebdomadaire" in t:
        return 7
    if "Mensuel" in t:
        return 30
    if "Annuel" in t:
        return 365
    return 30

STATUTS = ["ACTIVE", "EXPIRE", "SUSPENDU"]

def random_start_date():
    year = random.randint(2023, 2026)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime(year, month, day)

def make_row(i: int):
    sub_type = random.choice(TYPES)
    start = random_start_date()

    # base duration
    dur = base_duration_days(sub_type)

    # small random variation so ML can use "period" too
    if dur == 30:
        dur = dur + random.randint(-4, 5)
    elif dur == 7:
        dur = dur + random.randint(-1, 2)
    elif dur == 365:
        dur = dur + random.randint(-7, 10)

    end = start + timedelta(days=dur)

    # --- price logic ---
    base_p = BASE_PRICE[sub_type]

    # seasonality: jan & sept promos (-5%), summer +3%
    month = start.month
    season_coef = 1.0
    if month in (1, 9):
        season_coef = 0.94   # a bit more aggressive promo
    elif month in (6, 7):
        season_coef = 1.04   # summer is expensive

    # longer-than-usual monthly → slight increase
    len_bonus = 0.0
    if "Mensuel" in sub_type and dur > 32:
        len_bonus = 2.5      # increased because base is higher
    if "Hebdomadaire" in sub_type and dur > 7:
        len_bonus = 1.0
    if "Annuel" in sub_type and dur > 370:
        len_bonus = 10.0

    # random noise (keep it small so model can learn structure)
    noise = np.random.normal(loc=0.0, scale=1.8)

    prix = base_p * season_coef + len_bonus + noise

    # enforce minimum
    prix = max(10.0, round(prix, 2))

    # statut distribution: older subs more likely to be expired
    if start.year < 2024:
        statut = random.choices(["EXPIRE", "ACTIVE", "SUSPENDU"], weights=[0.6, 0.3, 0.1])[0]
    else:
        statut = random.choices(["ACTIVE", "EXPIRE", "SUSPENDU"], weights=[0.65, 0.2, 0.15])[0]

    return {
        "id": i,
        "type": sub_type,
        "prix": prix,
        "date_debut": start.strftime("%Y-%m-%d"),
        "date_fin": end.strftime("%Y-%m-%d"),
        "statut": statut,
    }

def main():
    N = 10_000
    rows = [make_row(i) for i in range(1, N + 1)]
    df = pd.DataFrame(rows)

    # optional: shuffle
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)

    out_path = "gym_subscriptions_10k_expensive.csv"
    df.to_csv(out_path, index=False)
    print(f"✅ Generated {len(df)} rows → {out_path}")
    print(df.head(10))

if __name__ == "__main__":
    main()
