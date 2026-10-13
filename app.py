# ===========================================================================
# app.py — Football Player Performance Analytics Dashboard
# SYNTHETIC DATA — all player names, clubs, and statistics are entirely
# fictional and generated programmatically. This data does not represent
# any real person, club, or event.
# ===========================================================================

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Streamlit page config — must be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="⚽ Football Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===========================================================================
# SECTION 1 — Theme
# ===========================================================================

def apply_theme():
    """
    Inject custom CSS to style the app with a dark, football-inspired look.

    Colour palette:
      Background : #0d1117  (near-black)
      Sidebar    : #161b22  (dark grey-green)
      Accent     : #238636  (pitch green)
      Text       : #e6edf3  (off-white)
    """
    css = """
    <style>
        /* ── Main background ─────────────────────────────────────── */
        .stApp {
            background-color: #0d1117;
            color: #e6edf3;
            font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
        }

        /* ── Sidebar ─────────────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background-color: #161b22;
            border-right: 1px solid #30363d;
        }
        section[data-testid="stSidebar"] * {
            color: #e6edf3 !important;
        }

        /* ── Headings ─────────────────────────────────────────────── */
        h1, h2, h3, h4, h5, h6 {
            color: #e6edf3 !important;
        }

        /* ── KPI / metric cards ───────────────────────────────────── */
        [data-testid="stMetric"] {
            background-color: #161b22;
            border: 1px solid #238636;
            border-radius: 8px;
            padding: 12px 16px;
        }
        [data-testid="stMetricValue"] {
            color: #238636 !important;
            font-size: 1.6rem !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #8b949e !important;
        }

        /* ── Buttons ──────────────────────────────────────────────── */
        .stButton > button,
        .stDownloadButton > button {
            background-color: #238636;
            color: #ffffff;
            border: none;
            border-radius: 6px;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background-color: #2ea043;
        }

        /* ── Input widgets ────────────────────────────────────────── */
        .stMultiSelect [data-baseweb="tag"] {
            background-color: #238636 !important;
        }
        .stTextInput input,
        .stSelectbox div[data-baseweb="select"] {
            background-color: #21262d !important;
            color: #e6edf3 !important;
            border-color: #30363d !important;
        }

        /* ── Dataframe ────────────────────────────────────────────── */
        .stDataFrame {
            background-color: #161b22;
        }

        /* ── Divider ─────────────────────────────────────────────── */
        hr {
            border-color: #30363d;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ===========================================================================
# SECTION 2 — Dataset generation (mirrors generate_data.py)
# ===========================================================================

# ---------------------------------------------------------------------------
# Reference data — seed fixed at 42 for full reproducibility
# ---------------------------------------------------------------------------
_RNG = np.random.default_rng(42)

_SEASONS = ["2022-23", "2023-24", "2024-25"]

_CLUBS = [
    "Irongate FC", "Redvale United", "Northholm City", "Westpark Athletic",
    "Silverstone Rovers", "Easthaven Town", "Blackmoor FC", "Goldcrest Villa",
    "Stormfield Athletic", "Crestwood Rangers",
]

_POSITIONS = ["GK", "DEF", "MID", "FWD"]

_FIRST_NAMES = [
    "Aaron", "Bruno", "Carlos", "Diego", "Emre", "Faisal", "Gabriel", "Hugo",
    "Ivan", "Jaime", "Karim", "Luca", "Marco", "Nils", "Omar", "Pablo",
    "Quentin", "Rafael", "Stefan", "Thiago", "Ugo", "Victor", "Wesley",
    "Xavier", "Yannick", "Zane", "Alexei", "Baptiste", "Cedric", "Damien",
    "Elias", "Fabio", "Gianni", "Henri", "Igor", "Julien", "Kosta", "Leandro",
    "Mateus", "Nico", "Oliver", "Pietro", "Remy", "Santi", "Toni",
    "Uriel", "Vitor", "Wael", "Yusuf", "Zlatan",
]

_LAST_NAMES = [
    "Silva", "Muller", "Okonkwo", "Fernandez", "Kovac", "Bianchi", "Dupont",
    "Reyes", "Johansson", "Ibarra", "Nakamura", "Ndiaye", "Petrov", "Costa",
    "Andersen", "Vidal", "Moreau", "Santos", "Klein", "Herrera", "Lombardi",
    "Mbeki", "Tremblay", "Castillo", "Novak", "Guerrero", "Ricci", "Larsson",
    "Alves", "Schäfer", "Diallo", "Pires", "Bogdanov", "Cruz", "Lindqvist",
    "Mensah", "Valente", "Papadopoulos", "Rousseau", "Delgado", "Fontana",
    "Svensson", "Torres", "Graff", "Ortega", "Bakker", "Sousa", "Eriksen",
    "Balogun", "Stein",
]

_PLAYER_NAMES = [
    f"{_FIRST_NAMES[i % len(_FIRST_NAMES)]} {_LAST_NAMES[i % len(_LAST_NAMES)]}"
    for i in range(100)
]

# Position-weighted distribution parameters
_POS_PARAMS = {
    "GK":  dict(goals_mean=0.1,  goals_std=0.3,  assists_mean=0.1, assists_std=0.3),
    "DEF": dict(goals_mean=1.5,  goals_std=1.5,  assists_mean=2.0, assists_std=1.5),
    "MID": dict(goals_mean=5.0,  goals_std=3.0,  assists_mean=6.0, assists_std=3.0),
    "FWD": dict(goals_mean=12.0, goals_std=5.0,  assists_mean=5.0, assists_std=3.0),
}

CSV_PATH = "football_players.csv"

# 17 columns that must be present after loading
REQUIRED_COLUMNS = [
    "player_id", "player_name", "team", "position", "season", "age",
    "matches_played", "minutes_played", "goals", "assists", "shots",
    "shots_on_target", "pass_accuracy", "key_passes", "yellow_cards",
    "red_cards", "rating",
]


def generate_dataset() -> None:
    """
    Generate football_players.csv if it does not already exist.

    Produces 300 rows (100 players × 3 seasons) of synthetic data.
    Uses a fixed seed (42) so every run produces the identical file.
    This function is a no-op when the CSV is already present.
    """
    if os.path.exists(CSV_PATH):
        return  # Nothing to do — file already exists

    rng = np.random.default_rng(42)
    rows = []
    n_players = 100

    teams     = rng.choice(_CLUBS, size=n_players)
    positions = rng.choice(_POSITIONS, size=n_players, p=[0.10, 0.35, 0.35, 0.20])
    base_ages = rng.integers(18, 33, size=n_players)

    for season_idx, season in enumerate(_SEASONS):
        for pid in range(n_players):
            pos    = positions[pid]
            params = _POS_PARAMS[pos]
            age    = int(base_ages[pid]) + season_idx

            matches = int(np.clip(rng.integers(10, 38), 1, 38))
            minutes = int(np.clip(
                matches * 75 + rng.integers(-10, 10),
                matches * 45, matches * 90,
            ))

            goals = int(np.clip(
                round(rng.normal(params["goals_mean"], params["goals_std"])), 0, 50
            ))
            assists = int(np.clip(
                round(rng.normal(params["assists_mean"], params["assists_std"])), 0, 30
            ))

            shots = int(np.clip(goals * 4 + rng.integers(-2, 6), goals, 80))
            shots_on_target = int(np.clip(
                round(shots * 0.45 + rng.normal(0, 1)), 0, shots
            ))

            pass_accuracy = round(float(np.clip(rng.normal(75, 8), 60.0, 95.0)), 1)
            key_passes    = int(np.clip(rng.integers(0, 8) * (matches / 38), 0, matches))
            yellow_cards  = int(np.clip(rng.integers(0, 10), 0, 10))
            red_cards     = int(np.clip(rng.integers(0, 3), 0, 3))

            card_penalty = yellow_cards * 0.05 + red_cards * 0.2
            raw_rating = (
                goals * 0.30
                + assists * 0.20
                + (pass_accuracy / 100) * 0.10 * 10
                + shots_on_target * 0.10
            ) / 4.0 + 5.0 - card_penalty
            rating = round(float(np.clip(raw_rating, 5.0, 9.5)), 1)

            rows.append({
                "player_id":       pid + 1,
                "player_name":     _PLAYER_NAMES[pid],
                "team":            teams[pid],
                "position":        pos,
                "season":          season,
                "age":             age,
                "matches_played":  matches,
                "minutes_played":  minutes,
                "goals":           goals,
                "assists":         assists,
                "shots":           shots,
                "shots_on_target": shots_on_target,
                "pass_accuracy":   pass_accuracy,
                "key_passes":      key_passes,
                "yellow_cards":    yellow_cards,
                "red_cards":       red_cards,
                "rating":          rating,
            })

    pd.DataFrame(rows).to_csv(CSV_PATH, index=False)


# ===========================================================================
# SECTION 3 — Data loading and validation
# ===========================================================================

@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Read football_players.csv, validate the schema, clean missing values,
    and return the ready-to-use DataFrame.

    Validation:
      - All 17 required columns must be present; if not, st.error + st.stop.
    Cleaning:
      - Numeric NaN → column median.
      - String NaN  → "Unknown".
    """
    df = pd.read_csv(CSV_PATH)

    # --- Schema validation --------------------------------------------------
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        st.error(
            f"football_players.csv is missing required columns: {missing_cols}. "
            "Delete the file and restart the app to regenerate it."
        )
        st.stop()

    # --- Fill missing values ------------------------------------------------
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].median())

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Unknown")

    return df


# ===========================================================================
# SECTION 4 — Sidebar filters
# ===========================================================================

def render_sidebar(df: pd.DataFrame) -> dict:
    """
    Render the sidebar navigation header and cascading multiselect filters.

    Filter chain:  Season → Team → Position → Player
    Each level constrains the options available at the next level.

    Returns a dict with keys: 'seasons', 'teams', 'positions', 'players'.
    An empty list means "all values selected" for that filter.
    """
    st.sidebar.markdown("## ⚽ Football Analytics")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filters")

    # -- Season --------------------------------------------------------------
    all_seasons = sorted(df["season"].unique().tolist())
    selected_seasons = st.sidebar.multiselect(
        "Season",
        options=all_seasons,
        default=all_seasons,
        help="Select one or more seasons to analyse.",
    )
    # Treat an empty selection as "all seasons"
    if not selected_seasons:
        selected_seasons = all_seasons

    # Narrow the dataset for subsequent filter option generation
    df_by_season = df[df["season"].isin(selected_seasons)]

    # -- Team ----------------------------------------------------------------
    all_teams = sorted(df_by_season["team"].unique().tolist())
    selected_teams = st.sidebar.multiselect(
        "Team",
        options=all_teams,
        default=all_teams,
        help="Teams are limited to those with players in the selected season(s).",
    )
    if not selected_teams:
        selected_teams = all_teams

    df_by_team = df_by_season[df_by_season["team"].isin(selected_teams)]

    # -- Position ------------------------------------------------------------
    all_positions = sorted(df_by_team["position"].unique().tolist())
    selected_positions = st.sidebar.multiselect(
        "Position",
        options=all_positions,
        default=all_positions,
        help="Positions available within the selected seasons and teams.",
    )
    if not selected_positions:
        selected_positions = all_positions

    df_by_position = df_by_team[df_by_team["position"].isin(selected_positions)]

    # -- Player --------------------------------------------------------------
    all_players = sorted(df_by_position["player_name"].unique().tolist())
    selected_players = st.sidebar.multiselect(
        "Player",
        options=all_players,
        default=all_players,
        help="Individual players available with the above filter selections.",
    )
    if not selected_players:
        selected_players = all_players

    st.sidebar.markdown("---")

    return {
        "seasons":   selected_seasons,
        "teams":     selected_teams,
        "positions": selected_positions,
        "players":   selected_players,
    }


# ===========================================================================
# SECTION 5 — Filter application
# ===========================================================================

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply the filter dict returned by render_sidebar() to the full DataFrame.

    Parameters
    ----------
    df      : The full, unfiltered DataFrame from load_data().
    filters : Dict with keys 'seasons', 'teams', 'positions', 'players'.

    Returns
    -------
    A filtered DataFrame.  May be empty if the combination yields no rows.
    """
    mask = (
        df["season"].isin(filters["seasons"])
        & df["team"].isin(filters["teams"])
        & df["position"].isin(filters["positions"])
        & df["player_name"].isin(filters["players"])
    )
    return df[mask].reset_index(drop=True)


# ===========================================================================
# SECTION 6 — Page stubs (full implementations come in later sub-tasks)
# ===========================================================================

def render_overview(df: pd.DataFrame) -> None:
    """Overview page — KPI cards, top-scorer bar, goals histogram."""
    st.title("📊 Overview")
    st.subheader("Season snapshot across all filtered players")

    # ------------------------------------------------------------------
    # Row 1 — KPI cards
    # ------------------------------------------------------------------
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Players", df["player_name"].nunique())
    with col2:
        st.metric("Total Goals", int(df["goals"].sum()))
    with col3:
        st.metric("Total Assists", int(df["assists"].sum()))
    with col4:
        st.metric(
            "Minutes Played",
            f"{int(df['minutes_played'].sum()):,}",
        )
    with col5:
        st.metric("Avg Rating", round(df["rating"].mean(), 2))

    st.markdown("---")

    # ------------------------------------------------------------------
    # Row 2 — Charts side-by-side
    # ------------------------------------------------------------------
    chart_left, chart_right = st.columns(2)

    # ── Top 10 Scorers ────────────────────────────────────────────────
    with chart_left:
        top10 = (
            df.groupby("player_name", as_index=False)["goals"]
            .sum()
            .sort_values("goals", ascending=False)
            .head(10)
            .sort_values("goals", ascending=True)   # ascending so longest bar is at top
        )
        fig_bar = px.bar(
            top10,
            x="goals",
            y="player_name",
            orientation="h",
            color="goals",
            color_continuous_scale="Greens",
            labels={"goals": "Goals", "player_name": "Player"},
            title="Top 10 Goal Scorers",
            template="plotly_dark",
        )
        fig_bar.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Goals Distribution ────────────────────────────────────────────
    with chart_right:
        fig_hist = px.histogram(
            df,
            x="goals",
            nbins=20,
            title="Goals Distribution",
            template="plotly_dark",
            labels={"goals": "Goals"},
        )
        fig_hist.update_traces(marker_color="#238636")
        st.plotly_chart(fig_hist, use_container_width=True)


def render_player_analysis(df: pd.DataFrame) -> None:
    """Player Analysis page — scatter plots and radar comparison."""
    st.title("👤 Player Analysis")

    # ------------------------------------------------------------------
    # Row 1 — Scatter plots side-by-side
    # ------------------------------------------------------------------
    col_left, col_right = st.columns(2)

    # ── Goals vs Assists ──────────────────────────────────────────────
    with col_left:
        fig_ga = px.scatter(
            df,
            x="assists",
            y="goals",
            color="position",
            hover_data=["player_name", "team", "season", "rating"],
            labels={"assists": "Assists", "goals": "Goals", "position": "Position"},
            title="Goals vs Assists by Position",
            template="plotly_dark",
        )
        st.plotly_chart(fig_ga, use_container_width=True)

    # ── Shots vs Goals (with LOWESS trendline) ────────────────────────
    with col_right:
        fig_sg = px.scatter(
            df,
            x="shots",
            y="goals",
            color="position",
            trendline="lowess",
            hover_data=["player_name", "team", "shots_on_target"],
            labels={"shots": "Shots", "goals": "Goals", "position": "Position"},
            title="Shots vs Goals (with Trend Line)",
            template="plotly_dark",
        )
        st.plotly_chart(fig_sg, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------------------
    # Player Comparison Section
    # ------------------------------------------------------------------
    st.subheader("🆚 Player Comparison")

    unique_players = df["player_name"].unique().tolist()
    if len(unique_players) < 2:
        st.warning("At least 2 players are required for comparison. Adjust the sidebar filters.")
        return

    # Default to the top-2 scorers (summed across all seasons in the filtered df)
    top_scorers = (
        df.groupby("player_name")["goals"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )
    default_a = top_scorers[0]
    default_b = top_scorers[1]

    sel_col_a, sel_col_b = st.columns(2)
    with sel_col_a:
        player_a = st.selectbox(
            "Select Player A",
            options=unique_players,
            index=unique_players.index(default_a),
        )
    with sel_col_b:
        player_b = st.selectbox(
            "Select Player B",
            options=unique_players,
            index=unique_players.index(default_b),
        )

    # ------------------------------------------------------------------
    # Radar / Spider Chart
    # ------------------------------------------------------------------
    radar_stats = ["goals", "assists", "shots", "key_passes", "pass_accuracy", "rating"]
    stat_labels = ["Goals", "Assists", "Shots", "Key Passes", "Pass Accuracy", "Rating"]

    # Aggregate per player (sum numeric, mean for pass_accuracy & rating)
    agg_funcs = {
        "goals": "sum",
        "assists": "sum",
        "shots": "sum",
        "key_passes": "sum",
        "pass_accuracy": "mean",
        "rating": "mean",
    }
    player_agg = df.groupby("player_name")[radar_stats].agg(agg_funcs)

    # Normalise using min/max from the FULL filtered df aggregation
    col_min = player_agg[radar_stats].min()
    col_max = player_agg[radar_stats].max()
    col_range = col_max - col_min
    # Avoid division by zero for constant columns
    col_range = col_range.replace(0, 1)

    def normalise(player_name: str) -> list:
        vals = player_agg.loc[player_name, radar_stats]
        return ((vals - col_min) / col_range).tolist()

    vals_a = normalise(player_a)
    vals_b = normalise(player_b)

    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(
        r=vals_a + [vals_a[0]],
        theta=stat_labels + [stat_labels[0]],
        fill="toself",
        name=player_a,
        line_color="#238636",
    ))

    fig_radar.add_trace(go.Scatterpolar(
        r=vals_b + [vals_b[0]],
        theta=stat_labels + [stat_labels[0]],
        fill="toself",
        name=player_b,
        line_color="#3b82d4",
    ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        template="plotly_dark",
        title="Player Attribute Comparison (Radar)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )

    st.plotly_chart(fig_radar, use_container_width=True)


def render_team_analysis(df: pd.DataFrame) -> None:
    """Team Analysis page — team-level bar charts."""
    st.title("🏆 Team Analysis")

    # ── Aggregate by team ─────────────────────────────────────────────────
    team_df = (
        df.groupby("team", as_index=False)
        .agg(
            total_goals=("goals", "sum"),
            total_assists=("assists", "sum"),
            player_count=("player_name", "nunique"),
        )
    )

    # ── Goals by Team (horizontal bar) ────────────────────────────────────
    goals_sorted = team_df.sort_values("total_goals", ascending=True)
    fig_goals = px.bar(
        goals_sorted,
        x="total_goals",
        y="team",
        orientation="h",
        color="total_goals",
        color_continuous_scale="Greens",
        template="plotly_dark",
        title="Total Goals by Team",
        labels={"total_goals": "Goals", "team": "Team"},
    )
    fig_goals.update_layout(coloraxis_showscale=False)

    # ── Assists by Team (horizontal bar) ──────────────────────────────────
    assists_sorted = team_df.sort_values("total_assists", ascending=True)
    fig_assists = px.bar(
        assists_sorted,
        x="total_assists",
        y="team",
        orientation="h",
        color="total_assists",
        color_continuous_scale="Blues",
        template="plotly_dark",
        title="Total Assists by Team",
        labels={"total_assists": "Assists", "team": "Team"},
    )
    fig_assists.update_layout(coloraxis_showscale=False)

    # ── Player Count per Team (vertical bar) ──────────────────────────────
    count_sorted = team_df.sort_values("player_count", ascending=False)
    fig_count = px.bar(
        count_sorted,
        x="team",
        y="player_count",
        template="plotly_dark",
        title="Player Count by Team",
        labels={"player_count": "Players", "team": "Team"},
    )
    fig_count.update_traces(marker_color="#238636")

    # ── Layout ────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_goals, use_container_width=True)
    with col2:
        st.plotly_chart(fig_assists, use_container_width=True)

    st.plotly_chart(fig_count, use_container_width=True)


def render_position_analysis(df: pd.DataFrame) -> None:
    """Position Analysis page — positional bars, box plots, violin."""
    st.title("📐 Position Analysis")
    st.caption(
        "An analysis of key player statistics broken down by playing position "
        "(GK · DEF · MID · FWD). Use the sidebar filters to narrow the squad."
    )

    # Canonical position order used by every chart on this page
    pos_order = ["GK", "DEF", "MID", "FWD"]
    cat_orders = {"position": pos_order}

    # ------------------------------------------------------------------
    # Aggregate: average goals per position
    # ------------------------------------------------------------------
    pos_avg = (
        df.groupby("position", as_index=False)["goals"]
        .mean()
        .rename(columns={"goals": "goals"})
    )
    # Ensure the category order is respected even for positions with no data
    pos_avg["position"] = pd.Categorical(pos_avg["position"], categories=pos_order, ordered=True)
    pos_avg = pos_avg.sort_values("position")

    fig_goals = px.bar(
        pos_avg,
        x="position",
        y="goals",
        category_orders=cat_orders,
        color_discrete_sequence=["#238636"],
        template="plotly_dark",
        title="Average Goals by Position",
        labels={"goals": "Avg Goals", "position": "Position"},
    )
    fig_goals.update_layout(showlegend=False)

    # ------------------------------------------------------------------
    # Rating distribution box plot
    # ------------------------------------------------------------------
    fig_rating = px.box(
        df,
        x="position",
        y="rating",
        color="position",
        category_orders=cat_orders,
        template="plotly_dark",
        title="Rating Distribution by Position",
        labels={"rating": "Rating", "position": "Position"},
    )
    fig_rating.update_layout(showlegend=False)

    # ------------------------------------------------------------------
    # Pass accuracy violin chart
    # ------------------------------------------------------------------
    fig_pass = px.violin(
        df,
        x="position",
        y="pass_accuracy",
        color="position",
        box=True,
        points="outliers",
        category_orders=cat_orders,
        template="plotly_dark",
        title="Pass Accuracy Distribution by Position",
        labels={"pass_accuracy": "Pass Accuracy (%)", "position": "Position"},
    )
    fig_pass.update_layout(showlegend=False)

    # ------------------------------------------------------------------
    # Layout: two charts side-by-side on top, violin full-width below
    # ------------------------------------------------------------------
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(fig_goals, use_container_width=True)
    with col_right:
        st.plotly_chart(fig_rating, use_container_width=True)

    st.plotly_chart(fig_pass, use_container_width=True)


def render_top_rankings(df: pd.DataFrame) -> None:
    """Top Rankings page — leaderboard bar charts."""
    st.title("🥇 Top Rankings")
    st.caption(
        "Top 10 players by goals, assists, and overall rating — based on current filters."
    )

    # Edge case: empty dataframe
    if df is None or len(df) == 0:
        st.warning("No data available for rankings with current filters.")
        return

    # ------------------------------------------------------------------
    # 1. Top Scorers
    # ------------------------------------------------------------------
    st.subheader("⚽ Top Goal Scorers")
    scorers = (
        df.groupby(["player_name", "team", "position"], as_index=False)["goals"]
        .sum()
        .sort_values("goals", ascending=False)
        .head(min(10, len(df["player_name"].unique())))
        .sort_values("goals", ascending=True)   # ascending so highest is at top in h-bar
    )
    fig_scorers = px.bar(
        scorers,
        x="goals",
        y="player_name",
        orientation="h",
        color="goals",
        color_continuous_scale="Greens",
        hover_data=["team", "position"],
        template="plotly_dark",
        title="⚽ Top 10 Goal Scorers",
        labels={"player_name": "Player", "goals": "Goals"},
    )
    fig_scorers.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_scorers, use_container_width=True)

    # ------------------------------------------------------------------
    # 2. Top Assisters
    # ------------------------------------------------------------------
    st.subheader("🎯 Top Assisters")
    assisters = (
        df.groupby(["player_name", "team", "position"], as_index=False)["assists"]
        .sum()
        .sort_values("assists", ascending=False)
        .head(min(10, len(df["player_name"].unique())))
        .sort_values("assists", ascending=True)
    )
    fig_assisters = px.bar(
        assisters,
        x="assists",
        y="player_name",
        orientation="h",
        color="assists",
        color_continuous_scale="Blues",
        hover_data=["team", "position"],
        template="plotly_dark",
        title="🎯 Top 10 Assisters",
        labels={"player_name": "Player", "assists": "Assists"},
    )
    fig_assisters.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_assisters, use_container_width=True)

    # ------------------------------------------------------------------
    # 3. Highest Rated
    # ------------------------------------------------------------------
    st.subheader("⭐ Highest Rated Players")
    rated = (
        df.groupby(["player_name", "team", "position"], as_index=False)["rating"]
        .mean()
        .sort_values("rating", ascending=False)
        .head(min(10, len(df["player_name"].unique())))
        .sort_values("rating", ascending=True)
    )
    fig_rated = px.bar(
        rated,
        x="rating",
        y="player_name",
        orientation="h",
        color="rating",
        color_continuous_scale="Oranges",
        hover_data=["team", "position"],
        template="plotly_dark",
        title="⭐ Top 10 Highest Rated Players",
        labels={"player_name": "Player", "rating": "Rating"},
    )
    fig_rated.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_rated, use_container_width=True)


def render_data_table(df: pd.DataFrame, filters: dict) -> None:
    """Data Table page — searchable table with CSV download."""
    st.title("📋 Data Table")

    # ------------------------------------------------------------------
    # 1. Player-name search
    # ------------------------------------------------------------------
    search_query = st.text_input(
        "🔍 Search player name...",
        placeholder="e.g. Marcus, Johnson...",
    )

    if search_query.strip():
        search_df = df[
            df["player_name"].str.contains(search_query.strip(), case=False, na=False)
        ].reset_index(drop=True)
    else:
        search_df = df.reset_index(drop=True)

    # ------------------------------------------------------------------
    # 2. Quick stats row
    # ------------------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows shown", len(search_df))
    col2.metric("Unique players", search_df["player_name"].nunique())
    col3.metric(
        "Unique teams",
        search_df["team"].nunique() if "team" in search_df.columns else "—",
    )
    col4.metric(
        "Unique positions",
        search_df["position"].nunique() if "position" in search_df.columns else "—",
    )

    # ------------------------------------------------------------------
    # 3. Result count caption + table
    # ------------------------------------------------------------------
    st.caption(f"Showing {len(search_df)} of {len(df)} players")
    st.dataframe(search_df, use_container_width=True)

    # ------------------------------------------------------------------
    # 4. Dynamic filename from active filters + CSV download
    # ------------------------------------------------------------------
    season_part   = filters.get("season",   "all") or "all"
    team_part     = filters.get("team",     "all") or "all"
    position_part = filters.get("position", "all") or "all"

    # Sanitise each part so it's safe in a filename
    def _safe(value: str) -> str:
        return str(value).replace(" ", "").replace("/", "-").replace("\\", "-")

    filename = f"players_{_safe(season_part)}_{_safe(team_part)}_{_safe(position_part)}.csv"

    st.download_button(
        label="⬇️ Download CSV",
        data=search_df.to_csv(index=False),
        file_name=filename,
        mime="text/csv",
    )


# ===========================================================================
# SECTION 7 — Main entry point
# ===========================================================================

PAGE_NAMES = [
    "Overview",
    "Player Analysis",
    "Team Analysis",
    "Position Analysis",
    "Top Rankings",
    "Data Table",
]

_PAGE_ROUTER = {
    "Overview":          lambda df, f: render_overview(df),
    "Player Analysis":   lambda df, f: render_player_analysis(df),
    "Team Analysis":     lambda df, f: render_team_analysis(df),
    "Position Analysis": lambda df, f: render_position_analysis(df),
    "Top Rankings":      lambda df, f: render_top_rankings(df),
    "Data Table":        lambda df, f: render_data_table(df, f),
}


def main() -> None:
    """
    Application entry point.

    Order of operations:
      1. Apply CSS theme.
      2. Regenerate CSV if missing.
      3. Load and validate data.
      4. Render sidebar filters.
      5. Apply filters to the full DataFrame.
      6. Guard against an empty result set.
      7. Route to the selected page renderer.
    """
    # 1. Theme
    apply_theme()

    # 2. Ensure the dataset exists
    generate_dataset()

    # 3. Load data (cached — only reads the file once per session)
    df_full = load_data()

    # 4. Sidebar filters
    filters = render_sidebar(df_full)

    # 5. Apply filters
    df = apply_filters(df_full, filters)

    # 6. Guard: empty result
    if df.empty:
        st.warning("No players match the selected filters.")
        st.stop()

    # 7. Page navigation
    page = st.sidebar.radio("Navigate to", PAGE_NAMES, label_visibility="collapsed")
    _PAGE_ROUTER[page](df, filters)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
