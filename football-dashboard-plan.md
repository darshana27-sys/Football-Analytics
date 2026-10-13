# Football Player Performance Analytics Dashboard — Implementation Plan

## Top-Level Overview

**Goal:** Build a portfolio-quality, interactive football (soccer) analytics dashboard using Python and Streamlit. The app will ingest a synthetic CSV dataset of 100+ players, expose sidebar filters, and render multiple analytic pages with Plotly charts, KPI cards, a searchable data table, and a CSV download button — all inside a dark, green-themed UI.

**Scope:**
- 4 deliverable files: `app.py`, `football_players.csv`, `requirements.txt`, `README.md`
- Synthetic dataset (clearly labelled) — no external APIs or real-world data
- 4 dashboard pages: Overview, Player Analysis, Team Analysis, Position Analysis
- Full sidebar filter chain: Season → Team → Position → Player
- No external dependencies beyond Pandas, NumPy, Streamlit, and Plotly

**Non-goals:**
- Live data ingestion, API calls, or database connections
- User authentication or multi-user state
- Deployment configuration beyond README instructions

---

## Dataset Schema

**File:** `football_players.csv`

| Column | Type | Description |
|---|---|---|
| `player_id` | int | Unique identifier (1–N) |
| `player_name` | str | Synthetic full name |
| `team` | str | One of 10 synthetic club names |
| `position` | str | GK / DEF / MID / FWD |
| `season` | str | One of 3 seasons: 2022-23, 2023-24, 2024-25 |
| `age` | int | 18–35 |
| `matches_played` | int | 1–38 |
| `minutes_played` | int | matches_played × ~75 ± noise |
| `goals` | int | Position-weighted random integer |
| `assists` | int | Position-weighted random integer |
| `shots` | int | goals × ~4 ± noise |
| `shots_on_target` | int | shots × ~0.45 ± noise |
| `pass_accuracy` | float | 60–95 % |
| `key_passes` | int | 0–8 per match |
| `yellow_cards` | int | 0–10 |
| `red_cards` | int | 0–3 |
| `rating` | float | Weighted composite 5.0–9.5, 1 d.p. |

**Generation rules:**
- Seed fixed at `42` for full reproducibility
- Goals/assists scaled per position: FWD > MID > DEF > GK
- Rating derived from goals, assists, pass accuracy, and card penalties (not hardcoded)
- 300 rows total (100 players × 3 seasons) — same player_name appears once per season with realistic season-to-season variation

---

## KPI Calculations (Overview Page)

All computed at runtime from the filtered DataFrame — never hardcoded.

| KPI Card | Formula |
|---|---|
| Total Players | `df['player_name'].nunique()` |
| Total Goals | `df['goals'].sum()` |
| Total Assists | `df['assists'].sum()` |
| Total Minutes Played | `df['minutes_played'].sum()` |
| Average Player Rating | `df['rating'].mean()` rounded to 2 d.p. |

---

## Chart Inventory

| Page | Chart | Library | Purpose |
|---|---|---|---|
| Overview | 5 KPI metric cards | Streamlit `st.metric` | At-a-glance headline numbers |
| Overview | Top 10 scorers bar chart | Plotly Express | Immediate engagement hook |
| Overview | Goals distribution histogram | Plotly Express | Show spread of scoring across all players |
| Player Analysis | Goals vs Assists scatter | Plotly Express | Identify creative attackers |
| Player Analysis | Shots vs Goals scatter | Plotly Express | Shot conversion efficiency |
| Player Analysis | Player radar / spider comparison | Plotly Graph Objects | Side-by-side multi-stat comparison |
| Team Analysis | Goals by team grouped bar | Plotly Express | Club offensive output |
| Team Analysis | Assists by team grouped bar | Plotly Express | Club creative output |
| Team Analysis | Player count per team | Plotly Express | Squad depth |
| Position Analysis | Avg goals by position bar | Plotly Express | Positional scoring norms |
| Position Analysis | Avg rating by position box plot | Plotly Express | Rating distribution by role |
| Position Analysis | Pass accuracy violin | Plotly Express | Technical profile by role |

---

## Project Structure

```
Football club/
├── app.py                  # Main Streamlit application
├── football_players.csv    # Synthetic dataset (generated once, committed)
├── requirements.txt        # Pinned Python dependencies
└── README.md               # Setup, run, and deploy instructions
```

### `app.py` Internal Modules (functions, not separate files)

| Function | Responsibility |
|---|---|
| `generate_dataset()` | Creates and saves `football_players.csv` if it does not exist |
| `load_data()` | Reads CSV, validates schema, handles missing values |
| `apply_filters(df, filters)` | Applies sidebar selections and returns filtered DataFrame |
| `render_sidebar(df)` | Builds Season / Team / Position / Player multiselects, returns filter dict |
| `render_overview(df)` | KPI cards + top-scorer bar + goals histogram |
| `render_player_analysis(df)` | Scatter plots + radar comparison |
| `render_team_analysis(df)` | Team-level grouped bar charts |
| `render_position_analysis(df)` | Position-level bars, box plots, violin |
| `render_data_table(df)` | Searchable `st.dataframe` + CSV download button |
| `apply_theme()` | Injects custom CSS for dark green theme |
| `main()` | Entry point: page router using `st.sidebar.radio` |

---

## UI / Theme Specification

- **Background:** `#0d1117` (near-black)
- **Sidebar:** `#161b22` (dark grey-green)
- **Accent / KPI cards:** `#238636` (football-pitch green)
- **Text:** `#e6edf3` (off-white)
- **Chart template:** Plotly `plotly_dark` with green accent colours
- **Font:** System sans-serif stack
- Custom CSS injected via `st.markdown(..., unsafe_allow_html=True)`

---

## Sidebar Filter Logic

Filters are **cascading** — each selection constrains the options in the filter below it:

```
Season  →  (filters teams available)  →  Team
        →  (filters positions available)  →  Position
        →  (filters players available)  →  Player
```

"All" option is the default for every filter. Selecting specific values narrows subsequent filters.

---

## Input Validation & Error Handling

- If `football_players.csv` is missing, `generate_dataset()` recreates it automatically on startup.
- If required columns are absent after load, display `st.error()` with the missing column names and stop execution (`st.stop()`).
- If any filter combination returns an empty DataFrame, display `st.warning("No players match the selected filters.")` and skip chart rendering.
- Numeric columns with NaN values are filled with column medians on load.
- String columns with NaN values are filled with `"Unknown"`.

---

## Sub-Tasks

---

### Sub-Task 1 — Generate Synthetic Dataset

**Intent:** Create `football_players.csv` with reproducible, realistic synthetic data so every other sub-task has a stable data foundation.

**Expected Outcomes:**
- `football_players.csv` exists in the workspace root
- 300 rows, 17 columns matching the schema above
- No NaN values in the output CSV
- Running the generation script a second time produces the identical file (seed=42)
- A comment at the top of the generation block clearly labels the data as synthetic

**Todo List:**
1. Write a standalone Python script (or inline function) that uses NumPy seed 42 to generate the dataset.
2. Define 10 club names, 4 positions, 3 seasons, and a synthetic name pool of 100 unique players.
3. For each player × season row, compute goals/assists/shots using position-weighted distributions.
4. Compute `rating` as a weighted formula: `(goals*0.3 + assists*0.2 + pass_accuracy*0.1 + shots_on_target*0.1) / scale + card_penalty`, clipped to [5.0, 9.5].
5. Save to `football_players.csv` with no index column.
6. Verify row count, column names, and dtype correctness before saving.

**Relevant Context:** Generation logic lives inside `generate_dataset()` in `app.py`; also invoked as a standalone check at module level.

**Status:** `[ ] pending`

---

### Sub-Task 2 — Project Scaffold and Data Loading

**Intent:** Set up `requirements.txt`, the `app.py` skeleton, `apply_theme()`, and `load_data()` / `apply_filters()` so the app boots, loads data, and handles errors correctly before any pages are built.

**Expected Outcomes:**
- `streamlit run app.py` launches without errors
- Sidebar renders Season / Team / Position / Player filters correctly
- `apply_filters()` returns the correctly narrowed DataFrame for any filter combination
- Missing CSV triggers auto-regeneration
- Empty filter result shows a warning instead of crashing

**Todo List:**
1. Write `requirements.txt` with pinned versions: `streamlit`, `pandas`, `numpy`, `plotly`.
2. Write `app.py` with imports, `apply_theme()` CSS injection, `load_data()`, `generate_dataset()` call-guard, and `apply_filters()`.
3. Write `render_sidebar()` with cascading multiselect widgets.
4. Write `main()` with `st.sidebar.radio` page navigation calling stub functions for each page.
5. Confirm app boots and filters work end-to-end with a full dataset load.

**Relevant Context:** Theme colours and CSS defined in the UI/Theme Specification section above.

**Status:** `[ ] pending`

---

### Sub-Task 3 — Overview Page

**Intent:** Implement `render_overview()` with the 5 KPI metric cards, top-10 scorers bar chart, and goals distribution histogram.

**Expected Outcomes:**
- 5 `st.metric` cards display correct live-computed values that update when filters change
- Top-10 scorers bar chart is sorted descending, labelled, and uses the green theme
- Goals histogram shows binned distribution with axis labels and tooltip
- All charts use `plotly_dark` template

**Todo List:**
1. Implement `render_overview(df)` — compute all 5 KPIs from the filtered `df`.
2. Lay out KPI cards in a 5-column `st.columns` row.
3. Build the top-10 scorers horizontal bar chart with Plotly Express.
4. Build the goals distribution histogram with Plotly Express.
5. Arrange charts in a 2-column layout using `st.columns`.

**Relevant Context:** KPI formulas defined in the KPI Calculations section above.

**Status:** `[ ] pending`

---

### Sub-Task 4 — Player Analysis Page

**Intent:** Implement `render_player_analysis(df)` with the Goals vs Assists scatter, Shots vs Goals scatter, and a radar/spider chart comparison for a user-selected pair of players.

**Expected Outcomes:**
- Goals vs Assists scatter colours points by position and shows player name on hover
- Shots vs Goals scatter adds a linear trend line and shows shot conversion efficiency
- Player comparison selector shows two dropdowns defaulting to the top-2 scorers
- Comparison renders a radar/spider chart using go.Scatterpolar for 6 normalised stats: goals, assists, shots, key_passes, pass_accuracy, rating

**Todo List:**
1. Implement Goals vs Assists scatter (colour=position, hover_data=[player_name, team, season]).
2. Implement Shots vs Goals scatter with trendline="ols" from Plotly Express.
3. Add two st.selectbox widgets for player A and player B selection.
4. Normalise the 6 comparison stats to 0-1 scale so the radar axes are comparable.
5. Build a radar/spider chart using go.Scatterpolar with one trace per player.
6. Handle edge case: if fewer than 2 players exist after filtering, show a warning and skip radar render.

**Relevant Context:** Player comparison uses `render_player_analysis(df)`; player list derived from filtered df.

**Status:** `[ ] pending`

---

### Sub-Task 5 — Team Analysis Page

**Intent:** Implement `render_team_analysis(df)` with team-level goals, assists, and player count charts.

**Expected Outcomes:**
- Goals by team bar chart (sorted by total goals, descending)
- Assists by team bar chart (sorted by total assists, descending)
- Player count per team bar chart
- All charts correctly reflect the currently applied sidebar filters

**Todo List:**
1. Aggregate `df` by team: sum goals, sum assists, count unique players.
2. Build sorted bar chart for goals per team.
3. Build sorted bar chart for assists per team.
4. Build bar chart for player count per team.
5. Arrange in a responsive layout (2 charts top row, 1 chart below).

**Relevant Context:** Team aggregation uses `groupby('team').agg(...)` on the filtered df.

**Status:** `[ ] pending`

---

### Sub-Task 6 — Position Analysis Page

**Intent:** Implement `render_position_analysis(df)` with average goals by position, average rating box plot, and pass accuracy violin chart.

**Expected Outcomes:**
- Average goals bar chart ordered GK → DEF → MID → FWD
- Rating box plot shows quartile spread per position
- Pass accuracy violin chart shows distribution shape per position
- Position order is consistent across all three charts

**Todo List:**
1. Define canonical position order: `["GK", "DEF", "MID", "FWD"]`.
2. Build avg goals bar chart with explicit category order.
3. Build rating box plot using `px.box(df, x="position", y="rating", ...)`.
4. Build pass accuracy violin using `px.violin(df, x="position", y="pass_accuracy", ...)`.
5. Arrange in a 2+1 layout matching the team page pattern.

**Relevant Context:** Position order must be enforced via `category_orders` parameter in Plotly Express.

**Status:** `[ ] pending`

---

### Sub-Task 7 — Data Table and CSV Download

**Intent:** Add `render_data_table(df)` with a searchable player statistics table and a one-click CSV download button.

**Expected Outcomes:**
- `st.dataframe` renders all filtered rows with sortable columns
- A text input above the table filters rows client-side by player name substring
- "Download CSV" button exports the currently displayed (filtered + searched) data
- Download filename includes the current filter context (e.g. `players_2024-25_all_FWD.csv`)

**Todo List:**
1. Add a `st.text_input("Search player name...")` widget.
2. Filter the df further by the search string (case-insensitive substring on `player_name`).
3. Render `st.dataframe(search_df, use_container_width=True)`.
4. Build the dynamic filename from active filter values.
5. Add `st.download_button` with `search_df.to_csv(index=False)` as the data payload.

**Relevant Context:** This page is accessible from the sidebar nav as "Data Table".

**Status:** `[ ] pending`

---

### Sub-Task 8 — Top Rankings Page

**Intent:** Implement `render_top_rankings(df)` as a leaderboard page showing the top scorers, top assisters, and highest-rated players.

**Expected Outcomes:**
- Three ranked leaderboard bar charts each showing the Top 10 players
- Scorers leaderboard: player_name, team, position, goals (sorted by goals desc)
- Assisters leaderboard: player_name, team, position, assists (sorted by assists desc)
- Highest rated leaderboard: player_name, team, position, rating (sorted by rating desc)
- All rankings correctly reflect the currently applied sidebar filters

**Todo List:**
1. Implement `render_top_rankings(df)` function.
2. Build top-10 scorers horizontal bar chart (sorted desc, labelled with team).
3. Build top-10 assisters horizontal bar chart.
4. Build top-10 highest rated horizontal bar chart.
5. Arrange in a 1-column stacked layout with clear section headers.
6. Handle edge case: if fewer than 10 players in filtered df, show however many exist without error.

**Relevant Context:** Rankings are derived entirely from the filtered df. Accessible from sidebar nav as "Top Rankings".

**Status:** `[ ] pending`

---

### Sub-Task 9 — README

**Intent:** Write a professional `README.md` that documents the project, the synthetic data disclaimer, local setup instructions, and deployment steps.

**Expected Outcomes:**
- Clear project description and feature list
- Prominent **Synthetic Data Disclaimer** section
- Step-by-step local run instructions (clone → venv → pip install → streamlit run)
- Streamlit Community Cloud deployment walkthrough
- Screenshot placeholder section for portfolio use

**Todo List:**
1. Write project overview and feature list.
2. Add synthetic data disclaimer.
3. Write local setup steps.
4. Write Streamlit Community Cloud deploy steps.
5. Add dataset schema table.
6. Add screenshot placeholder section.

**Status:** `[ ] pending`

---

## Dependency Versions (requirements.txt)

```
streamlit>=1.35.0
pandas>=2.2.0
numpy>=1.26.0
plotly>=5.22.0
```

No other dependencies required.
