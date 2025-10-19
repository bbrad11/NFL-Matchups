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

# Merge Next Gen Stats passing (example: by player and week)
stats_df = pd.merge(
    stats_df,
    ngs_passing[['player_display_name', 'week', 'pass_expected_points', 'pass_air_yards', 'pass_air_yards_per_att']],
    on=['player_display_name', 'week'],
    how='left'
)

# Position groups
positions = {
    'QB': ['QB'],
    'RB': ['RB', 'FB'],
    'WR': ['WR'],
    'TE': ['TE']
}

def get_defense_stats(stats_df, position_codes):
    pos_stats = stats_df[stats_df['position'].isin(position_codes)].copy()
    agg_dict = {}
    for col in ['passing_tds', 'rushing_tds', 'receiving_tds', 'passing_yards', 'rushing_yards', 'receiving_yards', 'fantasy_points_ppr']:
        if col in pos_stats.columns:
            agg_dict[col] = 'sum'
    if not agg_dict:
        return pd.DataFrame()
    defense_stats = pos_stats.groupby('opponent_team').agg(agg_dict).reset_index()
    defense_stats.columns = ['Defense'] + [col.replace('_', ' ').title() for col in defense_stats.columns[1:]]
    return defense_stats

tab1, tab2, tab3, tab4 = st.tabs(["🛡️ Worst Defenses", "🔥 This Week's Matchups", "🏆 Top Scorers", "📈 DFS Insights"])

with tab1:
    st.header("Which Defenses Give Up The Most?")
    position = st.selectbox("Position", ["QB", "RB", "WR", "TE"], key="worst_def_pos")
    df_filtered = stats_df[(stats_df["position"].isin(positions[position])) & (stats_df["week"] == current_week)].copy()
    defense_stats = get_defense_stats(df_filtered, positions[position])
    if defense_stats.empty:
        st.warning(f"No {position} data available for Week {current_week} in Season {season}")
    else:
        td_cols = [col for col in defense_stats.columns if 'Td' in col]
        sort_col = td_cols[0] if td_cols else defense_stats.columns[1]
        defense_stats = defense_stats.sort_values(sort_col, ascending=False)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"🔴 Worst {position} Defenses")
            st.caption("These defenses allow the most production")
            st.dataframe(defense_stats.head(10).reset_index(drop=True), use_container_width=True, hide_index=True)
        with col2:
            st.subheader(f"🟢 Best {position} Defenses")
            st.caption("These defenses shut down opponents")
            st.dataframe(defense_stats.tail(10).iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
        st.subheader(f"Top 15 Defenses Allowing {sort_col}")
        chart_data = defense_stats.head(15).set_index('Defense')[sort_col]
        st.bar_chart(chart_data)

with tab2:
    st.header(f"Week {current_week} Games")
    games = schedule_df[
        (schedule_df['week'] == current_week) &
        (schedule_df['game_type'] == 'REG')
    ].copy()
    st.write("DEBUG: Raw games for selected week:", games)
    if games.empty:
        st.warning(f"No games found for Week {current_week}")
    else:
        st.subheader(f"📅 {len(games)} Games This Week")
        weak_defenses = {}
        for pos_name, pos_codes in positions.items():
            df_def = stats_df[(stats_df["position"].isin(pos_codes)) & (stats_df["week"] == current_week)].copy()
            defense_stats = get_defense_stats(df_def, pos_codes)
            if not defense_stats.empty:
                td_cols = [col for col in defense_stats.columns if 'Td' in col]
                if td_cols:
                    defense_stats = defense_stats.sort_values(td_cols[0], ascending=False)
                    weak_defenses[pos_name] = defense_stats.head(10)['Defense'].tolist()
        for _, game in games.iterrows():
            away = game['away_team']
            home = game['home_team']
            with st.expander(f"{away} @ {home} - {game['gameday']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{away} Offense**")
                    for pos, weak_teams in weak_defenses.items():
                        if home in weak_teams:
                            rank = weak_teams.index(home) + 1
                            st.success(f"✅ {pos}: Good matchup (vs #{rank} worst defense)")
                with col2:
                    st.markdown(f"**{home} Offense**")
                    for pos, weak_teams in weak_defenses.items():
                        if away in weak_teams:
                            rank = weak_teams.index(away) + 1
                            st.success(f"✅ {pos}: Good matchup (vs #{rank} worst defense)")

with tab3:
    st.header(f"Season Leaders for Week {current_week}")
    sort_option = st.radio(
        "Show leaders by:", ["Touchdowns", "Yards", "Fantasy Points"],
        horizontal=True,
        key="top_scorer_sort"
    )
    def get_leaders(df, pos_codes, pos_name):
        pos_df = df[df['position'].isin(pos_codes)].copy()
        if pos_df.empty:
            return pd.DataFrame()
        has_pass_td = 'passing_tds' in pos_df.columns
        has_rush_td = 'rushing_tds' in pos_df.columns
        has_rec_td = 'receiving_tds' in pos_df.columns
        has_pass_yds = 'passing_yards' in pos_df.columns
        has_rush_yds = 'rushing_yards' in pos_df.columns
        has_rec_yds = 'receiving_yards' in pos_df.columns
        has_fantasy = 'fantasy_points_ppr' in pos_df.columns
        td_cols = []
        if has_pass_td:
            pos_df['passing_tds'] = pos_df['passing_tds'].fillna(0)
            td_cols.append('passing_tds')
        if has_rush_td:
            pos_df['rushing_tds'] = pos_df['rushing_tds'].fillna(0)
            td_cols.append('rushing_tds')
        if has_rec_td:
            pos_df['receiving_tds'] = pos_df['receiving_tds'].fillna(0)
            td_cols.append('receiving_tds')
        yds_cols = []
        if has_pass_yds:
            pos_df['passing_yards'] = pos_df['passing_yards'].fillna(0)
            yds_cols.append('passing_yards')
        if has_rush_yds:
            pos_df['rushing_yards'] = pos_df['rushing_yards'].fillna(0)
            yds_cols.append('rushing_yards')
        if has_rec_yds:
            pos_df['receiving_yards'] = pos_df['receiving_yards'].fillna(0)
            yds_cols.append('receiving_yards')
        agg_dict = {'player_display_name': 'first'}
        for team_col in ['recent_team', 'team', 'team_abbr']:
            if team_col in pos_df.columns:
                agg_dict[team_col] = 'last'
                break
        for col in td_cols + yds_cols:
            agg_dict[col] = 'sum'
        if has_fantasy:
            agg_dict['fantasy_points_ppr'] = 'sum'
        leaders = pos_df.groupby('player_display_name').agg(agg_dict).reset_index(drop=True)
        if td_cols:
            leaders['Total TDs'] = leaders[td_cols].sum(axis=1)
        if yds_cols:
            leaders['Total Yards'] = leaders[yds_cols].sum(axis=1)
        rename_map = {
            'player_display_name': 'Player',
            'recent_team': 'Team',
            'team': 'Team',
            'team_abbr': 'Team',
            'passing_tds': 'Pass TDs',
            'rushing_tds': 'Rush TDs',
            'receiving_tds': 'Rec TDs',
            'passing_yards': 'Pass Yds',
            'rushing_yards': 'Rush Yds',
            'receiving_yards': 'Rec Yds',
            'fantasy_points_ppr': 'Fantasy Pts'
        }
        leaders = leaders.rename(columns=rename_map)
        if sort_option == "Touchdowns":
            sort_col = 'Total TDs' if 'Total TDs' in leaders.columns else leaders.columns[2]
        elif sort_option == "Yards":
            sort_col = 'Total Yards' if 'Total Yards' in leaders.columns else leaders.columns[2]
        else:
            sort_col = 'Fantasy Pts' if 'Fantasy Pts' in leaders.columns else leaders.columns[2]
        leaders = leaders.sort_values(sort_col, ascending=False).head(15)
        return leaders
    df_filtered = stats_df[stats_df['week'] == current_week].copy()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎯 Quarterbacks")
        qb_leaders = get_leaders(df_filtered, positions['QB'], "QB")
        if not qb_leaders.empty:
            st.dataframe(qb_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No QB data available")
        st.subheader("🏃 Running Backs")
        rb_leaders = get_leaders(df_filtered, positions['RB'], "RB")
        if not rb_leaders.empty:
            st.dataframe(rb_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No RB data available")
    with col2:
        st.subheader("📡 Wide Receivers")
        wr_leaders = get_leaders(df_filtered, positions['WR'], "WR")
        if not wr_leaders.empty:
            st.dataframe(wr_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No WR data available")
        st.subheader("🎣 Tight Ends")
        te_leaders = get_leaders(df_filtered, positions['TE'], "TE")
        if not te_leaders.empty:
            st.dataframe(te_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No TE data available")
    
with tab4:
    st.header("DFS Insights: Player Reliability & Upside")
    st.markdown("Identify consistent players for safer bets — and volatile players for tournament upside.")
    pos = st.selectbox("Position", ["QB", "RB", "WR", "TE"], key="dfs_pos_tab4")
    df_filtered = stats_df[(stats_df['position'].isin(positions[pos])) & (stats_df['week'] == current_week)].copy()
    if not df_filtered.empty:
        grouped = df_filtered.groupby('player_display_name')['fantasy_points_ppr'].agg(['mean', 'std']).reset_index()
        grouped.rename(columns={'mean': 'Avg Pts', 'std': 'Std Dev'}, inplace=True)
        grouped['Consistency Rating'] = grouped['Std Dev'] / grouped['Avg Pts']
        quantiles = df_filtered.groupby('player_display_name')['fantasy_points_ppr'].quantile([0.2, 0.8]).unstack().reset_index()
        quantiles.columns = ['Player', 'Floor', 'Ceiling']
        dfs_df = grouped.merge(quantiles, left_on='player_display_name', right_on='Player', how='left')
        dfs_df['Range'] = dfs_df['Ceiling'] - dfs_df['Floor']
        dfs_df = dfs_df.sort_values('Consistency Rating')
        def color_points(val):
            if pd.isna(val):
                return ''
            if val > 20:
                return 'background-color: #d4edda'
            elif val < 10:
                return 'background-color: #f8d7da'
            else:
                return 'background-color: #fff3cd'
        styled_df = dfs_df.style.applymap(color_points, subset=['Avg Pts', 'Ceiling', 'Floor'])
        st.dataframe(styled_df, use_container_width=True)
        st.download_button(label="💾 Download DFS Insights CSV", data=dfs_df.to_csv(index=False).encode('utf-8'), file_name="dfs_insights.csv", mime="text/csv")
    else:
        st.warning(f"No {pos} data available for DFS Insights")

# Footer
st.markdown("---")
st.markdown("📊 Data: [nflverse](https://github.com/nflverse/nflreadpy) | Updated weekly during NFL season")
