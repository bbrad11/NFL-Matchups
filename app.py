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
season = st.sidebar.selectbox("Season", [2025, 2024, 2023], index=0, key="season_select")
current_week = st.sidebar.slider("Week", 1, 18, 7, key="week_slider")

# Cache data loading
@st.cache_data
def load_nfl_data(season):
    player_stats = nfl.load_player_stats([season])
    schedules = nfl.load_schedules([season])
    return player_stats.to_pandas(), schedules.to_pandas()

@st.cache_data
def load_ngs_stats(season):
    ngs_passing = nfl.load_nextgen_stats(seasons=[season], stat_type="passing").to_pandas()
    ngs_receiving = nfl.load_nextgen_stats(seasons=[season], stat_type="receiving").to_pandas()
    ngs_rushing = nfl.load_nextgen_stats(seasons=[season], stat_type="rushing").to_pandas()
    return ngs_passing, ngs_receiving, ngs_rushing

with st.spinner('Loading NFL data...'):
    stats_df, schedule_df = load_nfl_data(season)

with st.spinner('Loading Next Gen Stats...'):
    ngs_passing, ngs_receiving, ngs_rushing = load_ngs_stats(season)

# Merge a few key passing Next Gen Stats fields as an example:
ngs_cols = ['player_display_name', 'week']
for c in ['pass_expected_points', 'pass_air_yards', 'pass_air_yards_per_att']:
    if c in ngs_passing.columns:
        ngs_cols.append(c)
ngs_passing_trim = ngs_passing[ngs_cols]

stats_df = pd.merge(stats_df, ngs_passing_trim, how='left', on=['player_display_name', 'week'])

# Position groups definition
positions = {
    'QB': ['QB'],
    'RB': ['RB', 'FB'],
    'WR': ['WR'],
    'TE': ['TE']
}

def get_defense_stats(stats_df, position_codes):
    df = stats_df[stats_df['position'].isin(position_codes)].copy()
    agg_cols = ['passing_tds', 'rushing_tds', 'receiving_tds', 'passing_yards', 'rushing_yards', 'receiving_yards', 'fantasy_points_ppr']
    agg_dict = {col: 'sum' for col in agg_cols if col in df.columns}
    if not agg_dict:
        return pd.DataFrame()
    grouped = df.groupby('opponent_team').agg(agg_dict).reset_index()
    grouped.columns = ['Defense'] + [col.replace('_', ' ').title() for col in grouped.columns[1:]]
    return grouped

# Tabs Setup
tab1, tab2, tab3 = st.tabs(["🛡️ Worst Defenses", "🔥 This Week's Matchups", "🏆 Top Scorers"])

# Tab 1: Worst Defenses
with tab1:
    st.header("Which Defenses Give Up The Most?")
    st.markdown("Higher numbers = easier matchup for offensive players")
    position = st.selectbox("Position", ["QB", "RB", "WR", "TE"], key="worst_def_pos")
    df_filtered = stats_df[(stats_df['position'].isin(positions[position])) & (stats_df['week'] == current_week)]
    defense_stats = get_defense_stats(df_filtered, positions[position])
    if defense_stats.empty:
        st.warning(f"No {position} data for Week {current_week} Season {season}")
    else:
        td_cols = [c for c in defense_stats.columns if 'Td' in c]
        sort_col = td_cols[0] if td_cols else defense_stats.columns[1]
        defense_stats = defense_stats.sort_values(sort_col, ascending=False)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Worst {position} Defenses")
            st.dataframe(defense_stats.head(10).reset_index(drop=True), use_container_width=True, hide_index=True)
        with col2:
            st.subheader(f"Best {position} Defenses")
            st.dataframe(defense_stats.tail(10).iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
        st.subheader(f"Top 15 Defenses Allowing {sort_col}")
        st.bar_chart(defense_stats.head(15).set_index('Defense')[sort_col])

# Tab 2: This Week's Matchups
with tab2:
    st.header(f"Week {current_week} Games")
    games = schedule_df[(schedule_df['week'] == current_week) & (schedule_df['game_type'] == 'REG')]
    st.write("DEBUG: Games this week:", games)
    if games.empty:
        st.warning(f"No games found for Week {current_week}")
    else:
        st.subheader(f"📅 {len(games)} Games")
        weak_defenses = {}
        for pos, pos_codes in positions.items():
            df_pos = stats_df[(stats_df['position'].isin(pos_codes)) & (stats_df['week'] == current_week)]
            defense_stats = get_defense_stats(df_pos, pos_codes)
            if not defense_stats.empty:
                td_cols = [c for c in defense_stats.columns if 'Td' in c]
                if td_cols:
                    defense_stats = defense_stats.sort_values(td_cols[0], ascending=False)
                    weak_defenses[pos] = defense_stats.head(10)['Defense'].tolist()

        for _, game in games.iterrows():
            away, home = game['away_team'], game['home_team']
            with st.expander(f"{away} @ {home} - {game['gameday']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{away} Offense**")
                    for pos, weak_list in weak_defenses.items():
                        if home in weak_list:
                            rank = weak_list.index(home) + 1
                            st.success(f"✅ {pos}: Good matchup vs #{rank} worst defense")
                with col2:
                    st.markdown(f"**{home} Offense**")
                    for pos, weak_list in weak_defenses.items():
                        if away in weak_list:
                            rank = weak_list.index(away) + 1
                            st.success(f"✅ {pos}: Good matchup vs #{rank} worst defense")

# Tab 3: Top Scorers
with tab3:
    st.header(f"Season Leaders - Week {current_week}")
    sort_option = st.radio("Show leaders by:",["Touchdowns", "Yards", "Fantasy Points"], horizontal=True, key="top_scorer_sort")

    def get_leaders(df, pos_codes):
        pos_df = df[df['position'].isin(pos_codes)].copy()
        if pos_df.empty:
            return pd.DataFrame()
        # Totals and aggregation as before ...
        # Keep your existing aggregation code here

    df_filtered = stats_df[stats_df['week'] == current_week]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Quarterbacks")
        qb_leaders = get_leaders(df_filtered, positions['QB'])
        if not qb_leaders.empty:
            st.dataframe(qb_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No QB data available")
        st.subheader("Running Backs")
        rb_leaders = get_leaders(df_filtered, positions['RB'])
        if not rb_leaders.empty:
            st.dataframe(rb_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No RB data available")
    with col2:
        st.subheader("Wide Receivers")
        wr_leaders = get_leaders(df_filtered, positions['WR'])
        if not wr_leaders.empty:
            st.dataframe(wr_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No WR data available")
        st.subheader("Tight Ends")
        te_leaders = get_leaders(df_filtered, positions['TE'])
        if not te_leaders.empty:
            st.dataframe(te_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No TE data available")

st.markdown("---")
st.markdown("📊 Data: [nflverse](https://github.com/nflverse/nflreadpy) | Updated weekly during NFL season")
