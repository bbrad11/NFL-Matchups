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
season = st.sidebar.selectbox("Season", [2025, 2024, 2023], index=0)
current_week = st.sidebar.slider("Week", 1, 18, 7)

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

tab1, tab2, tab3 = st.tabs(["🛡️ Worst Defenses", "🔥 This Week's Matchups", "🏆 Top Scorers"])

# ============================================================
# TAB 1: WORST DEFENSES
# ============================================================

with tab1:
    st.header("Which Defenses Give Up The Most?")
    st.markdown("Higher numbers = easier matchup for offensive players")
    
    position = st.selectbox("Position", ["QB", "RB", "WR", "TE"])
    
    defense_stats = get_defense_stats(stats_df, positions[position])
    
    if defense_stats.empty:
        st.warning(f"No {position} data available for {season}")
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
        st.bar_chart(chart_data)

# ============================================================
# TAB 2: THIS WEEK'S MATCHUPS
# ============================================================

with tab2:
    st.header(f"Week {current_week} Games")
    st.markdown("Find favorable matchups where strong offenses meet weak defenses")
    
    # Get this week's games
    games = schedule_df[
        (schedule_df['week'] == current_week) & 
        (schedule_df['game_type'] == 'REG')
    ].copy()
    
    if games.empty:
        st.warning(f"No games found for Week {current_week}")
    else:
        st.subheader(f"📅 {len(games)} Games This Week")
        
        # Get weak defenses for each position
        weak_defenses = {}
        for pos_name, pos_codes in positions.items():
            defense_stats = get_defense_stats(stats_df, pos_codes)
            if not defense_stats.empty:
                # Get column with TDs
                td_cols = [col for col in defense_stats.columns if 'Td' in col]
                if td_cols:
                    defense_stats = defense_stats.sort_values(td_cols[0], ascending=False)
                    weak_defenses[pos_name] = defense_stats.head(10)['Defense'].tolist()
        
        # Show each game
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

# ============================================================
# TAB 3: TOP SCORERS
# ============================================================

with tab3:
    st.header("Season Leaders")
    
    sort_option = st.radio(
        "Show leaders by:",
        ["Touchdowns", "Yards", "Fantasy Points"],
        horizontal=True
    )
    
    def get_leaders(df, pos_codes, pos_name):
        """Get top players at a position"""
        pos_df = df[df['position'].isin(pos_codes)].copy()
        
        if pos_df.empty:
            return pd.DataFrame()
        
        # Determine what columns exist
        has_pass_td = 'passing_tds' in pos_df.columns
        has_rush_td = 'rushing_tds' in pos_df.columns
        has_rec_td = 'receiving_tds' in pos_df.columns
        has_pass_yds = 'passing_yards' in pos_df.columns
        has_rush_yds = 'rushing_yards' in pos_df.columns
        has_rec_yds = 'receiving_yards' in pos_df.columns
        has_fantasy = 'fantasy_points_ppr' in pos_df.columns
        
        # Calculate totals
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
        
        # Build aggregation
        agg_dict = {'player_display_name': 'first'}
        
        # Add team column
        for team_col in ['recent_team', 'team', 'team_abbr']:
            if team_col in pos_df.columns:
                agg_dict[team_col] = 'last'
                break
        
        # Add stat columns
        for col in td_cols + yds_cols:
            agg_dict[col] = 'sum'
        
        if has_fantasy:
            agg_dict['fantasy_points_ppr'] = 'sum'
        
        # Group by player
        leaders = pos_df.groupby('player_display_name').agg(agg_dict).reset_index(drop=True)
        
        # Calculate total TDs and yards
        if td_cols:
            leaders['Total TDs'] = leaders[td_cols].sum(axis=1)
        if yds_cols:
            leaders['Total Yards'] = leaders[yds_cols].sum(axis=1)
        
        # Rename columns for display
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
        
        # Sort based on user preference
        if sort_option == "Touchdowns":
            sort_col = 'Total TDs' if 'Total TDs' in leaders.columns else leaders.columns[2]
        elif sort_option == "Yards":
            sort_col = 'Total Yards' if 'Total Yards' in leaders.columns else leaders.columns[2]
        else:  # Fantasy Points
            sort_col = 'Fantasy Pts' if 'Fantasy Pts' in leaders.columns else leaders.columns[2]
        
        leaders = leaders.sort_values(sort_col, ascending=False).head(15)
        
        return leaders
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Quarterbacks")
        qb_leaders = get_leaders(stats_df, positions['QB'], "QB")
        if not qb_leaders.empty:
            st.dataframe(qb_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No QB data available")
        
        st.subheader("🏃 Running Backs")
        rb_leaders = get_leaders(stats_df, positions['RB'], "RB")
        if not rb_leaders.empty:
            st.dataframe(rb_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No RB data available")
    
    with col2:
        st.subheader("📡 Wide Receivers")
        wr_leaders = get_leaders(stats_df, positions['WR'], "WR")
        if not wr_leaders.empty:
            st.dataframe(wr_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No WR data available")
        
        st.subheader("🎣 Tight Ends")
        te_leaders = get_leaders(stats_df, positions['TE'], "TE")
        if not te_leaders.empty:
            st.dataframe(te_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No TE data available")

# ============================================================
# TAB 4: DFS INSIGHTS
# ============================================================

tab4 = st.tabs(["📈 DFS Insights"])[0]

with tab4:
    st.header("DFS Insights: Player Reliability & Upside")
    st.markdown("Identify consistent players for safer bets — and volatile players for tournament upside.")

    # Filter
    pos = st.selectbox("Position", ["QB", "RB", "WR", "TE"], key="dfs_pos")

    df = stats_df[stats_df['position'].isin(positions[pos])].copy()
    
    if not df.empty:
        # Group player weekly performance
        grouped = df.groupby('player_display_name')['fantasy_points_ppr'].agg(['mean', 'std']).reset_index()
        grouped.rename(columns={'mean': 'Avg Pts', 'std': 'Std Dev'}, inplace=True)
        grouped['Consistency Rating'] = grouped['Std Dev'] / grouped['Avg Pts']
        
        # Floor / ceiling from quantiles
        quantiles = df.groupby('player_display_name')['fantasy_points_ppr'].quantile([0.2, 0.8]).unstack().reset_index()
        quantiles.columns = ['Player', 'Floor', 'Ceiling']

        dfs_df = grouped.merge(quantiles, left_on='player_display_name', right_on='Player', how='left')
        dfs_df['Range'] = dfs_df['Ceiling'] - dfs_df['Floor']
        dfs_df = dfs_df.sort_values('Consistency Rating')

        st.subheader("Top 10 Safest Plays (Lowest Variance)")
        st.dataframe(dfs_df.head(10)[['Player', 'Avg Pts', 'Std Dev', 'Consistency Rating']], use_container_width=True)

        st.subheader("Top 10 Boom/Bust Plays (Highest Range)")
        st.dataframe(
            dfs_df.sort_values('Range', ascending=False).head(10)[['Player', 'Avg Pts', 'Floor', 'Ceiling', 'Range']],
            use_container_width=True
        )

        # Merge with defense stats for matchup edge
        defense_stats = get_defense_stats(stats_df, positions[pos])
        if not defense_stats.empty:
            df_comb = df.merge(defense_stats, left_on='opponent_team', right_on='Defense', how='left')
            avg_matchup = df_comb.groupby('player_display_name')['Fantasy Points Ppr'].mean().reset_index()
            dfs_df = dfs_df.merge(avg_matchup, left_on='Player', right_on='player_display_name', how='left')

        # Export option
        st.download_button(
            label="💾 Download DFS Insights CSV",
            data=dfs_df.to_csv(index=False).encode('utf-8'),
            file_name="dfs_insights.csv",
            mime="text/csv"
        )

    else:
        st.warning(f"No {pos} data available for DFS Insights")

# === Begin of DFS Insights Tab Code ===

tab4 = st.tabs(["📈 DFS Insights"])[0]

with tab4:
    st.header("DFS Insights: Player Reliability & Upside")
    st.markdown("Identify consistent players for safer bets and high-upside players for tournaments.")

    # Select position
    pos = st.selectbox("Position", ["QB", "RB", "WR", "TE"], key="dfs_pos")
    df = stats_df[stats_df['position'].isin(positions[pos])].copy()

    if not df.empty:
        # Calculate weekly performance stats
        grouped = df.groupby('player_display_name')['fantasy_points_ppr'].agg(['mean', 'std']).reset_index()
        grouped.rename(columns={'mean': 'Avg Pts', 'std': 'Std Dev'}, inplace=True)
        grouped['Consistency Rating'] = grouped['Std Dev'] / grouped['Avg Pts']

        # Compute 20th/80th percentiles for ceiling/floor
        quantiles = df.groupby('player_display_name')['fantasy_points_ppr'].quantile([0.2, 0.8]).unstack().reset_index()
        quantiles.columns = ['Player', 'Floor', 'Ceiling']

        # Merge and sort
        dfs_df = grouped.merge(quantiles, left_on='player_display_name', right_on='Player', how='left')
        dfs_df['Range'] = dfs_df['Ceiling'] - dfs_df['Floor']
        dfs_df = dfs_df.sort_values('Consistency Rating')

        # Color coding function
        def color_points(val):
            if pd.isna(val):
                return ''
            if val > 20:
                return 'background-color: #d4edda'  # light green
            elif val < 10:
                return 'background-color: #f8d7da'  # light red
            else:
                return 'background-color: #fff3cd'  # light yellow

        # Apply color styling
        styled_df = dfs_df.style.applymap(
            color_points,
            subset=['Avg Pts', 'FanDuel Projection', 'Ceiling', 'Floor']
        )

        # Display styled data frame
        st.dataframe(styled_df, use_container_width=True)

        # Download button for the data
        csv_bytes = dfs_df.to_csv(index=False).encode()
        st.download_button(
            label="💾 Download DFS Insights CSV",
            data=csv_bytes,
            file_name="dfs_insights_fantasy_points.csv",
            mime="text/csv"
        )

        # Optional: Add a bar chart for projections vs actuals
        if 'FanDuel Projection' in dfs_df.columns:
            st.subheader("Projection vs Actual")
            chart_data = dfs_df[['Player', 'Avg Pts', 'FanDuel Projection']].set_index('Player')
            st.bar_chart(chart_data)
    else:
        st.warning(f"No data available for {pos}")

# === End of DFS Insights Tab Code ===



# Footer
st.markdown("---")
st.markdown("📊 Data: [nflverse](https://github.com/nflverse/nflreadpy) | Updated weekly during NFL season")
