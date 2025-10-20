# nfl_app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import nflreadpy as nfl
from betting_analyzer import render_betting_tab  # Ensure this file exists in same directory


def run():
    # ---------------- Page Config ----------------
    st.set_page_config(page_title="NFL Matchup Analyzer", page_icon="🏈", layout="wide")

    # ---------------- Custom CSS ----------------
    st.markdown("""
        <style>
        .main h1 { color: #1E3A8A; font-size: 3rem !important; font-weight: 800 !important; margin-bottom: 0.5rem !important; }
        [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] { height: 50px; background-color: #F3F4F6; border-radius: 8px; padding: 0 24px; font-weight: 600; }
        .stTabs [aria-selected="true"] { background-color: #1E3A8A; color: white; }
        </style>
    """, unsafe_allow_html=True)

    # ---------------- Title ----------------
    st.markdown("""
        <h1 style='text-align:center;'>🏈 NFL Matchup Analyzer</h1>
        <p style='text-align:center;color:#6B7280;font-size:1.2rem;'>Analyze performances, matchups, and betting insights</p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ---------------- Sidebar ----------------
    st.sidebar.header("⚙️ NFL Settings")
    season = st.sidebar.selectbox("Season", [2025, 2024, 2023], index=0)
    current_week = st.sidebar.slider("Week", 1, 18, 7)

    @st.cache_data
    def load_nfl_data(season):
        try:
            player_stats = nfl.load_player_stats([season])
            schedule = nfl.load_schedule([season])
            return player_stats, schedule
        except Exception:
            return pd.DataFrame(), pd.DataFrame()

    stats_df, schedule_df = load_nfl_data(season)

    if stats_df.empty:
        st.error("No player data could be loaded for this season.")
        return
    if schedule_df.empty:
        st.warning("Schedule data not available.")

    # ---------------- Validate Player Column ----------------
    if 'player_display_name' not in stats_df.columns:
        possible_player_cols = [c for c in ['player_name', 'name', 'display_name'] if c in stats_df.columns]
        if possible_player_cols:
            stats_df = stats_df.rename(columns={possible_player_cols[0]: 'player_display_name'})
        else:
            st.warning("⚠️ Missing player name column in stats data.")

    # ---------------- Helper Functions ----------------
    positions = {'QB': ['QB'], 'RB': ['RB', 'FB'], 'WR': ['WR'], 'TE': ['TE']}

    def get_defense_stats(df, pos_codes):
        pos_df = df[df['position'].isin(pos_codes)].copy()
        if pos_df.empty:
            return pd.DataFrame()
        agg_dict = {col: 'sum' for col in 
                    ['passing_tds', 'rushing_tds', 'receiving_tds',
                     'passing_yards', 'rushing_yards', 'receiving_yards', 'fantasy_points_ppr']
                    if col in pos_df.columns}
        defense = pos_df.groupby('opponent_team').agg(agg_dict).reset_index()
        defense.columns = ['Defense'] + [col.replace('_', ' ').title() for col in defense.columns[1:]]
        return defense

    # ---------------- Tabs ----------------
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🛡️ Worst Defenses", 
        "🔥 Matchups", 
        "🏆 Top Scorers",
        "📊 Consistency", 
        "⚡ NextGen Stats", 
        "💰 Betting"
    ])

    # ---------------- TAB 1: Worst Defenses ----------------
    with tab1:
        st.header("🛡️ Which Defenses Give Up The Most?")
        position = st.selectbox("Select Position", list(positions.keys()))
        defense_stats = get_defense_stats(stats_df, positions[position])
        if defense_stats.empty:
            st.info("No defensive data available.")
        else:
            st.dataframe(defense_stats.sort_values(defense_stats.columns[1], ascending=False), use_container_width=True)

    # ---------------- TAB 2: Matchups ----------------
    with tab2:
        st.header(f"🔥 Week {current_week} Matchups")
        games = schedule_df[schedule_df['week'] == current_week]
        if games.empty:
            st.warning(f"No games for Week {current_week}")
        else:
            for _, g in games.iterrows():
                st.subheader(f"{g['away_team']} @ {g['home_team']}")

    # ---------------- TAB 3: Top Scorers ----------------
    with tab3:
        st.header("🏆 Top Scorers")
        pos = st.selectbox("Position", list(positions.keys()), key="leader_pos")
        pos_df = stats_df[stats_df['position'].isin(positions[pos])]
        if 'fantasy_points_ppr' in pos_df.columns:
            leaders = pos_df.groupby('player_display_name')['fantasy_points_ppr'].sum().reset_index()
            st.dataframe(leaders.sort_values('fantasy_points_ppr', ascending=False).head(15), use_container_width=True)
        else:
            st.info("Fantasy points unavailable.")

    # ---------------- TAB 4: Consistency ----------------
    with tab4:
        st.header("📊 Player Consistency Ratings")
        pos = st.selectbox("Position", list(positions.keys()), key="consistency_pos")
        pos_df = stats_df[stats_df['position'].isin(positions[pos])]
        if 'fantasy_points_ppr' not in pos_df.columns:
            st.warning("No fantasy data available.")
        else:
            data = pos_df.groupby('player_display_name')['fantasy_points_ppr'].agg(['mean', 'std', 'count'])
            data = data[data['count'] >= 3]
            data['CV'] = data['std'] / data['mean'] * 100
            data['Consistency Rating'] = 100 - (data['CV'] / data['CV'].max() * 100)
            st.dataframe(data.sort_values('Consistency Rating', ascending=False).head(15), use_container_width=True)

    # ---------------- TAB 5: NextGen Stats ----------------
    with tab5:
        st.header("⚡ NextGen Stats")
        st.markdown("Advanced metrics from NFL player tracking")
        stat_type = st.selectbox("Category", ["rushing", "receiving", "passing"])
        @st.cache_data
        def load_nextgen_data(season, stat_type):
            try:
                return nfl.load_nextgen_stats(season, stat_type)
            except Exception:
                return pd.DataFrame()
        ng = load_nextgen_data(season, stat_type)
        if ng.empty:
            st.warning("No NextGen data available.")
        else:
            st.dataframe(ng.head(20), use_container_width=True)

    # ---------------- TAB 6: Betting ----------------
    with tab6:
        st.header("💰 Betting Insights")
        st.markdown("Explore potential betting edges and trends.")
        try:
            render_betting_tab(sport="NFL", stats_df=stats_df, schedule_df=schedule_df)
        except Exception as e:
            st.error(f"Betting tab error: {e}")

    # ---------------- Footer ----------------
    st.markdown("---")
    st.caption("Data from nflverse (nflreadpy). Updated weekly.")


if __name__ == "__main__":
    run()
