# ⚽ Football Player Performance Analytics Dashboard

> An interactive, data-driven football analytics dashboard built with Python and Streamlit — featuring player comparisons, team analysis, position breakdowns, and live-filtering leaderboards.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.22%2B-3F4F75?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Project Overview

The **Football Player Performance Analytics Dashboard** is a portfolio-quality, fully interactive web application that lets you explore and compare simulated footballer statistics across multiple seasons, teams, and positions.

Built entirely in Python, it demonstrates end-to-end data engineering and visualisation skills:

- **Synthetic dataset generation** — 300 rows of reproducible player data across 3 seasons
- **Cascading sidebar filters** — narrow down by Season → Team → Position → Player in real time
- **Multi-page dashboard** — five distinct analytical views accessible from the sidebar
- **Exportable results** — download any filtered slice as a CSV with one click
- **Dark, football-inspired UI** — custom CSS theming with a pitch-green accent palette

It requires no external APIs, no database, and no credentials — just Python and a virtual environment.

---

## ⚠️ Synthetic Data Disclaimer

> **All player data in this project is artificially generated for demonstration and portfolio purposes only.**

- Player names, club names, and all associated statistics are **entirely fabricated** and do **not** represent real footballers, real clubs, or real match statistics from any league or competition.
- The dataset is generated programmatically using **NumPy with a fixed seed of `42`**, ensuring full reproducibility — running the generation script multiple times will always produce the identical CSV.
- This project is **not affiliated with** any football association, club, data provider, or sports organisation.
- The data should **not** be cited, published, or used for any purpose other than software demonstration.

---

## Features

- **Overview KPI Dashboard** — at-a-glance headline metrics: total players, goals, assists, minutes played, and average rating
- **Player Comparison with Radar Chart** — side-by-side spider chart comparing two players across six normalised statistics
- **Team Analysis** — goals, assists, and squad-depth bar charts aggregated by club
- **Position Analysis** — average goals bar, rating box plot, and pass-accuracy violin chart broken down by GK / DEF / MID / FWD
- **Top Rankings Leaderboard** — top-10 scorers, assisters, and highest-rated players with horizontal bar charts
- **Cascading Sidebar Filters** — Season → Team → Position → Player; each selection narrows downstream options
- **Searchable Data Table** — live substring search over player names on a full sortable stats table
- **CSV Export** — download the currently filtered and searched dataset; filename reflects the active filter context
- **Dark Football-Inspired UI** — custom CSS with near-black background (`#0d1117`) and pitch-green accents (`#238636`)
- **Responsive Plotly Charts with Tooltips** — every chart uses `plotly_dark` template with rich hover data

---

## Project Structure

```
football club/
├── app.py                  # Main Streamlit application (all pages and logic)
├── football_players.csv    # Synthetic dataset — generated once, committed to repo
├── generate_data.py        # Standalone data-generation script (optional re-run)
├── requirements.txt        # Pinned Python dependencies
└── README.md               # This file
```

---

## Dataset Schema

The file `football_players.csv` contains **300 rows** (100 unique players × 3 seasons) and **17 columns**:

| Column | Type | Description |
|---|---|---|
| `player_id` | `int` | Unique player identifier (1–100) |
| `player_name` | `str` | Synthetic full name (first + last) |
| `team` | `str` | One of 10 synthetic club names |
| `position` | `str` | Role: `GK`, `DEF`, `MID`, or `FWD` |
| `season` | `str` | One of three seasons: `2022-23`, `2023-24`, `2024-25` |
| `age` | `int` | Player age, 18–35 |
| `matches_played` | `int` | Appearances in the season, 1–38 |
| `minutes_played` | `int` | Approx. `matches_played × 75` ± noise |
| `goals` | `int` | Season goal tally — position-weighted (FWD > MID > DEF > GK) |
| `assists` | `int` | Season assists — position-weighted |
| `shots` | `int` | Total shots (~goals × 4 ± noise) |
| `shots_on_target` | `int` | Shots on target (~shots × 0.45 ± noise) |
| `pass_accuracy` | `float` | Season pass completion rate, 60–95 % |
| `key_passes` | `int` | Chance-creating passes, 0–8 per match |
| `yellow_cards` | `int` | Yellow cards received, 0–10 |
| `red_cards` | `int` | Red cards received, 0–3 |
| `rating` | `float` | Weighted composite score, 5.0–9.5 (1 d.p.) |

> **Rating formula:** derived at generation time from goals, assists, pass accuracy, shots on target, and card penalties — never hardcoded.

---

## Local Setup

### Prerequisites

- Python **3.10** or later
- `pip` (comes with Python)
- A terminal / command prompt

### Step-by-Step Instructions

**Step 1 — Clone or download the project**

```bash
git clone https://github.com/<your-username>/football-dashboard.git
cd football-dashboard
```

Or download and unzip the repository, then open a terminal in the project folder.

---

**Step 2 — Create a virtual environment**

```bash
python -m venv venv
```

---

**Step 3 — Activate the virtual environment**

Windows:
```bash
venv\Scripts\activate
```

macOS / Linux:
```bash
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

---

**Step 4 — Install dependencies**

```bash
pip install -r requirements.txt
```

This installs Streamlit, Pandas, NumPy, and Plotly at the pinned versions.

---

**Step 5 — Run the app**

```bash
streamlit run app.py
```

Streamlit will automatically generate `football_players.csv` on first launch if it does not already exist.

---

**Step 6 — Open in your browser**

```
http://localhost:8501
```

The dashboard opens automatically in most environments. If it does not, copy the URL above into your browser.

---

## Streamlit Community Cloud Deployment

Deploy the app for free on [Streamlit Community Cloud](https://share.streamlit.io) in five steps:

1. **Push to a public GitHub repository**
   Commit all project files (`app.py`, `football_players.csv`, `requirements.txt`, `README.md`) and push to a public repo.

2. **Go to [share.streamlit.io](https://share.streamlit.io)**
   Sign in with your GitHub account if you haven't already.

3. **Connect your GitHub account**
   Authorise Streamlit Community Cloud to access your repositories when prompted.

4. **Select your repo, branch, and main file**
   - Repository: `<your-username>/football-dashboard`
   - Branch: `main` (or `master`)
   - Main file path: `app.py`

5. **Click Deploy**
   Streamlit will install dependencies from `requirements.txt` and launch the app at a public URL of the form `https://<your-app>.streamlit.app`.

> **Tip:** The synthetic CSV is committed to the repo, so no generation step is required on the cloud host.

---

## Screenshots

<!-- Add screenshots here -->
<!--
  Recommended screenshots to add:
    1. Overview page — KPI cards + top-scorer bar chart
    2. Player Analysis — radar/spider comparison chart
    3. Team Analysis — goals and assists by club
    4. Position Analysis — box plot and violin chart
    5. Top Rankings — leaderboard view
    6. Data Table — searchable table with download button

  Place images in a /screenshots folder and reference them like:
    ![Overview](screenshots/overview.png)
-->

*Screenshots coming soon — run the app locally to explore all pages.*

---

## Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| [Python](https://www.python.org/) | 3.10+ | Core language |
| [Pandas](https://pandas.pydata.org/) | ≥ 2.2.0 | Data loading, filtering, aggregation |
| [NumPy](https://numpy.org/) | ≥ 1.26.0 | Synthetic data generation (seed 42) |
| [Streamlit](https://streamlit.io/) | ≥ 1.35.0 | Web app framework and UI components |
| [Plotly](https://plotly.com/python/) | ≥ 5.22.0 | Interactive charts (Express + Graph Objects) |

---

## License

This project is released under the **MIT License**.

```
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
