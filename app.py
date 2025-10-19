import streamlit as st
import nflreadpy as nfl
import pandas as pd

# Page config
st.set_page_config(page_title="NFL Matchup Analyzer", page_icon="🏈", layout="wide")

# Title
st.title("🏈 NFL Matchup Analyzer")
st.markdown("Find the best matchups by tracking which defenses give up the most points")

# Sidebar controls
st.sidebar.header("Settings")
season = st.sidebar.selectbox("Season", [2025, 2024], index=0, key="season_select")
current_week = st.sidebar.slider("Week", 1, 18, 7, key="week_slider")

# Cache data loading
@st.cache_data
def load_nfl_data(season):
    player_stats = nfl.load_player_stats([season])
    schedules = nfl.load_schedules([season])
    return player_stats.to_pandas(), schedules.to_pandas()

# Load data
with st.spinner('Loading NFL data...'):
    stats_df, schedule_df = load_nfl_data(season)

st.success(f"✅ Loaded {len(stats_df):,} player games")

# Position groups
positions = {
    'QB': ['QB'],
    'RB': ['RB', 'FB'],
    'WR': ['WR'],
    'TE': ['TE']
}

# Analyze defense performance
def get_defense_stats(stats_df, position_codes):
    """Get how each defense performs against a position"""
    pos_stats = stats_df[stats_df['position'].isin(position_codes)].copy()
    
    # Build aggregation based on available columns
    agg_dict = {}
    for col in ['passing_tds', 'rushing_tds', 'receiving_tds', 'passing_yards', 'rushing_yards', 'receiving_yards', 'fantasy_points_ppr']:
        if col in pos_stats.columns:
            agg_dict[col] = 'sum'
    
    if not agg_dict:
        return pd.DataFrame()
    
    defense_stats = pos_stats.groupby('opponent_team').agg(agg_dict).reset_index()
    defense_stats.columns = ['Defense'] + [col.replace('_', ' ').title() for col in defense_stats.columns[1:]]
    
    return defense_stats

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(["🛡️ Worst Defenses", "🔥 This Week's Matchups", "🏆 Top Scorers", "📈 DFS Insights"])

# ============================================================
# TAB 1: WORST DEFENSES
# ============================================================

with tab1:
    st.header("Which Defenses Give Up The Most?")
    st.markdown("Higher numbers = easier matchup for offensive players")
    
    position = st.selectbox("Position", ["QB", "RB", "WR", "TE"], key="worst_def_pos")
    
    # Filter stats_df by week and position
    df_filtered = stats_df[(stats_df["position"].isin(positions[position])) & (stats_df["week"] == current_week)].copy()
    defense_stats = get_defense_stats(df_filtered, positions[position])
    
    if defense_stats.empty:
        st.warning(f"No {position} data available for Week {current_week} in Season {season}")
    else:
        # Sort by TDs (or first available column)
        td_cols = [col for col in defense_stats.columns if 'Td' in col]
        sort_col = td_cols[0] if td_cols else defense_stats.columns[1]
        defense_stats = defense_stats.sort_values(sort_col, ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"🔴 Worst {position} Defenses")
            st.caption("These defenses allow the most production")
            st.dataframe(
                defense_stats.head(10).reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.subheader(f"🟢 Best {position} Defenses")
            st.caption("These defenses shut down opponents")
            st.dataframe(
                defense_stats.tail(10).iloc[::-1].reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )
        
        # Chart
        st.subheader(f"Top 15 Defenses Allowing {sort_col}")
        chart_data = defense_stats.head(15).set_index('Defense')[sort_col]
        st.bar
