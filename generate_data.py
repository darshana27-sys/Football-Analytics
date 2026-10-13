# ===========================================================================
# generate_data.py
# SYNTHETIC DATA — all player names, clubs, and statistics are entirely
# fictional and generated programmatically. This data does not represent
# any real person, club, or event.
# ===========================================================================

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Seed — fixed at 42 for full reproducibility
# ---------------------------------------------------------------------------
RNG = np.random.default_rng(42)

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
SEASONS = ["2022-23", "2023-24", "2024-25"]

CLUBS = [
    "Irongate FC",
    "Redvale United",
    "Northholm City",
    "Westpark Athletic",
    "Silverstone Rovers",
    "Easthaven Town",
    "Blackmoor FC",
    "Goldcrest Villa",
    "Stormfield Athletic",
    "Crestwood Rangers",
]

POSITIONS = ["GK", "DEF", "MID", "FWD"]

# 100 unique synthetic player names
FIRST_NAMES = [
    "Aaron", "Bruno", "Carlos", "Diego", "Emre", "Faisal", "Gabriel", "Hugo",
    "Ivan", "Jaime", "Karim", "Luca", "Marco", "Nils", "Omar", "Pablo",
    "Quentin", "Rafael", "Stefan", "Thiago", "Ugo", "Victor", "Wesley",
    "Xavier", "Yannick", "Zane", "Alexei", "Baptiste", "Cedric", "Damien",
    "Elias", "Fabio", "Gianni", "Henri", "Igor", "Julien", "Kosta", "Leandro",
    "Mateus", "Nico", "Oliver", "Pietro", "Remy", "Santi", "Toni",
    "Uriel", "Vitor", "Wael", "Yusuf", "Zlatan",
]

LAST_NAMES = [
    "Silva", "Muller", "Okonkwo", "Fernandez", "Kovac", "Bianchi", "Dupont",
    "Reyes", "Johansson", "Ibarra", "Nakamura", "Ndiaye", "Petrov", "Costa",
    "Andersen", "Vidal", "Moreau", "Santos", "Klein", "Herrera", "Lombardi",
    "Mbeki", "Tremblay", "Castillo", "Novak", "Guerrero", "Ricci", "Larsson",
    "Alves", "Schäfer", "Diallo", "Pires", "Bogdanov", "Cruz", "Lindqvist",
    "Mensah", "Valente", "Papadopoulos", "Rousseau", "Delgado", "Fontana",
    "Svensson", "Torres", "Graff", "Ortega", "Bakker", "Sousa", "Eriksen",
    "Balogun", "Stein",
]

# Build exactly 100 unique names by pairing first × last (cycling if needed)
_pairs = [(FIRST_NAMES[i % len(FIRST_NAMES)], LAST_NAMES[i % len(LAST_NAMES)])
          for i in range(100)]
PLAYER_NAMES = [f"{f} {l}" for f, l in _pairs]

# ---------------------------------------------------------------------------
# Position-weighted parameters  (goals_mean, goals_std, assists_mean, assists_std)
# ---------------------------------------------------------------------------
POS_PARAMS = {
    "GK":  dict(goals_mean=0.1, goals_std=0.3,  assists_mean=0.1, assists_std=0.3),
    "DEF": dict(goals_mean=1.5, goals_std=1.5,  assists_mean=2.0, assists_std=1.5),
    "MID": dict(goals_mean=5.0, goals_std=3.0,  assists_mean=6.0, assists_std=3.0),
    "FWD": dict(goals_mean=12.0, goals_std=5.0, assists_mean=5.0, assists_std=3.0),
}


def _clamp(arr, lo, hi):
    return np.clip(arr, lo, hi)


def generate_dataset() -> pd.DataFrame:
    """Generate a 300-row synthetic football player dataset (seed=42)."""
    n_players = 100
    rows = []

    # Assign each player a fixed team and position (stable across seasons)
    teams = RNG.choice(CLUBS, size=n_players)
    positions = RNG.choice(POSITIONS, size=n_players, p=[0.10, 0.35, 0.35, 0.20])
    base_ages = RNG.integers(18, 33, size=n_players)  # age in first season

    for season_idx, season in enumerate(SEASONS):
        p = POS_PARAMS  # alias for brevity
        for pid in range(n_players):
            pos = positions[pid]
            params = p[pos]
            age = int(base_ages[pid]) + season_idx

            matches = int(_clamp(RNG.integers(10, 38), 1, 38))
            minutes = int(_clamp(
                matches * 75 + RNG.integers(-10, 10), matches * 45, matches * 90
            ))

            goals = int(_clamp(
                round(RNG.normal(params["goals_mean"], params["goals_std"])), 0, 50
            ))
            assists = int(_clamp(
                round(RNG.normal(params["assists_mean"], params["assists_std"])), 0, 30
            ))

            shots = int(_clamp(goals * 4 + RNG.integers(-2, 6), goals, 80))
            shots_on_target = int(_clamp(
                round(shots * 0.45 + RNG.normal(0, 1)), 0, shots
            ))

            pass_accuracy = round(float(_clamp(
                RNG.normal(75, 8), 60.0, 95.0
            )), 1)

            key_passes = int(_clamp(RNG.integers(0, 8) * (matches / 38), 0, matches))
            yellow_cards = int(_clamp(RNG.integers(0, 10), 0, 10))
            red_cards = int(_clamp(RNG.integers(0, 3), 0, 3))

            # Rating formula — weighted composite, clipped to [5.0, 9.5]
            # Normalise each component to a roughly 0-1 contribution
            card_penalty = (yellow_cards * 0.05 + red_cards * 0.2)
            raw_rating = (
                goals * 0.30
                + assists * 0.20
                + (pass_accuracy / 100) * 0.10 * 10   # rescale to ~0-1 × weight × 10
                + shots_on_target * 0.10
            ) / 4.0 + 5.0 - card_penalty              # base offset of 5.0

            rating = round(float(_clamp(raw_rating, 5.0, 9.5)), 1)

            rows.append({
                "player_id":        pid + 1,
                "player_name":      PLAYER_NAMES[pid],
                "team":             teams[pid],
                "position":         pos,
                "season":           season,
                "age":              age,
                "matches_played":   matches,
                "minutes_played":   minutes,
                "goals":            goals,
                "assists":          assists,
                "shots":            shots,
                "shots_on_target":  shots_on_target,
                "pass_accuracy":    pass_accuracy,
                "key_passes":       key_passes,
                "yellow_cards":     yellow_cards,
                "red_cards":        red_cards,
                "rating":           rating,
            })

    df = pd.DataFrame(rows)
    return df


# ---------------------------------------------------------------------------
# Main — generate and save
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    df = generate_dataset()

    # Verification
    assert len(df) == 300, f"Expected 300 rows, got {len(df)}"
    expected_cols = [
        "player_id", "player_name", "team", "position", "season", "age",
        "matches_played", "minutes_played", "goals", "assists", "shots",
        "shots_on_target", "pass_accuracy", "key_passes", "yellow_cards",
        "red_cards", "rating",
    ]
    assert list(df.columns) == expected_cols, f"Column mismatch: {list(df.columns)}"
    assert df.isnull().sum().sum() == 0, "NaN values detected in output"

    df.to_csv("football_players.csv", index=False)
    print(f"OK football_players.csv saved - {len(df)} rows x {len(df.columns)} columns")
    print("OK No NaN values")
    print("\nSample (5 rows):")
    print(df.sample(5, random_state=42).to_string(index=False))
