import streamlit as st
import nflreadpy as nfl
import pandas as pd
import requests
import io

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
    """Load Next Gen Stats using nflreadpy"""
    try:
        ngs_passing = nfl.load_nextgen_stats(seasons=[season], stat_type="passing").to_pandas()
        ngs_receiving = nfl.load_nextgen_stats(seasons=[season], stat_type="receiving").to_pandas()
        ngs_rushing = nfl.load_nextgen_stats(seasons=[season], stat_type="rushing").to_pandas()
        st.sidebar.success("✅ Next Gen Stats loaded via nflreadpy")
        return ngs_passing, ngs_receiving, ngs_rushing
    except Exception as e:
        st.sidebar.warning(f"⚠️ Could not load Next Gen Stats: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

@st.cache_data
def load_nextgen_data_fallback(season):
    """Fallback method to load Next Gen Stats from nflverse-data directly"""
    try:
        datasets = {}
        
        # Rushing Next Gen Stats
        try:
            rushing_url = f"https://github.com/nflverse/nflverse-data/releases/download/ngs/ngs_rushing_{season}.csv"
            rushing_response = requests.get(rushing_url)
            if rushing_response.status_code == 200:
                datasets['rushing'] = pd.read_csv(io.StringIO(rushing_response.text))
                st.sidebar.success("✅ Next Gen Rushing Stats loaded (fallback)")
        except Exception as e:
            st.sidebar.warning(f"⚠️ Could not load Next Gen Rushing Stats: {str(e)}")
        
        # Receiving Next Gen Stats
        try:
            receiving_url = f"https://github.com/nflverse/nflverse-data/releases/download/ngs/ngs_receiving_{season}.csv"
            receiving_response = requests.get(receiving_url)
            if receiving_response.status_code == 200:
                datasets['receiving'] = pd.read_csv(io.StringIO(receiving_response.text))
                st.sidebar.success("✅ Next Gen Receiving Stats loaded (fallback)")
        except Exception as e:
            st.sidebar.warning(f"⚠️ Could not load Next Gen Receiving Stats: {str(e)}")
        
        # Passing Next Gen Stats
        try:
            passing_url = f"https://github.com/nflverse/nflverse-data/releases/download/ngs/ngs_passing_{season}.csv"
            passing_response = requests.get(passing_url)
            if passing_response.status_code == 200:
                datasets['passing'] = pd.read_csv(io.StringIO(passing_response.text))
                st.sidebar.success("✅ Next Gen Passing Stats loaded (fallback)")
        except Exception as e:
            st.sidebar.warning(f"⚠️ Could not load Next Gen Passing Stats: {str(e)}")
        
        return datasets
    except Exception as e:
        st.sidebar.error(f"❌ Error loading Next Gen Stats: {str(e)}")
        return {}

# Load data
with st.spinner('Loading NFL data...'):
    stats_df, schedule_df = load_nfl_data(season)

with st.spinner('Loading Next Gen Stats...'):
    ngs_passing, ngs_receiving, ngs_rushing = load_ngs_stats(season)
    
    # If nflreadpy method fails, try fallback
    if ngs_passing.empty and ngs_receiving.empty and ngs_rushing.empty:
        nextgen_data = load_nextgen_data_fallback(season)
    else:
        # Convert to the format expected by our analysis functions
        nextgen_data = {}
        if not ngs_passing.empty:
            nextgen_data['passing'] = ngs_passing
        if not ngs_receiving.empty:
            nextgen_data['receiving'] = ngs_receiving
        if not ngs_rushing.empty:
            nextgen_data['rushing'] = ngs_rushing

# Merge a few key passing Next Gen Stats fields as an example:
if not ngs_passing.empty:
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

# Next Gen Stats analysis functions
def analyze_nextgen_rushing(nextgen_data):
    """Analyze Next Gen rushing statistics"""
    if 'rushing' not in nextgen_data:
        return pd.DataFrame()
    
    rushing_df = nextgen_data['rushing'].copy()
    
    # Handle different column naming conventions
    rush_yards_col = 'rush_yards' if 'rush_yards' in rushing_df.columns else 'rushing_yards'
    rush_td_col = 'rush_touchdowns' if 'rush_touchdowns' in rushing_df.columns else 'rushing_tds'
    rush_att_col = 'rush_attempts' if 'rush_attempts' in rushing_df.columns else 'rushing_att'
    
    # Group by player and calculate totals
    agg_dict = {
        rush_yards_col: 'sum',
        rush_td_col: 'sum',
        rush_att_col: 'sum'
    }
    
    # Add additional columns if they exist
    additional_cols = {
        'rush_yards_over_expected': 'sum',
        'rush_yards_over_expected_per_att': 'mean',
        'rush_pct_over_expected': 'mean',
        'rush_epa': 'sum',
        'rush_touchdown_pct': 'mean'
    }
    
    for col, agg_func in additional_cols.items():
        if col in rushing_df.columns:
            agg_dict[col] = agg_func
    
    player_stats = rushing_df.groupby('player_display_name').agg(agg_dict).reset_index()
    
    # Calculate efficiency metrics
    if rush_yards_col in player_stats.columns and rush_att_col in player_stats.columns:
        player_stats['yards_per_carry'] = player_stats[rush_yards_col] / player_stats[rush_att_col]
    if rush_td_col in player_stats.columns and rush_att_col in player_stats.columns:
        player_stats['touchdown_rate'] = player_stats[rush_td_col] / player_stats[rush_att_col]
    
    # Sort by rush yards
    sort_col = rush_yards_col if rush_yards_col in player_stats.columns else player_stats.columns[1]
    return player_stats.sort_values(sort_col, ascending=False)

def analyze_nextgen_receiving(nextgen_data):
    """Analyze Next Gen receiving statistics"""
    if 'receiving' not in nextgen_data:
        return pd.DataFrame()
    
    receiving_df = nextgen_data['receiving'].copy()
    
    # Handle different column naming conventions
    rec_yards_col = 'receiving_yards' if 'receiving_yards' in receiving_df.columns else 'rec_yards'
    rec_td_col = 'receiving_touchdowns' if 'receiving_touchdowns' in receiving_df.columns else 'rec_tds'
    
    # Group by player and calculate totals
    agg_dict = {
        rec_yards_col: 'sum',
        rec_td_col: 'sum',
        'receptions': 'sum',
        'targets': 'sum'
    }
    
    # Add additional columns if they exist
    additional_cols = {
        'avg_separation': 'mean',
        'avg_cushion': 'mean',
        'avg_intended_air_yards': 'mean',
        'avg_yac': 'mean',
        'catch_percentage': 'mean',
        'avg_air_yards_differential': 'mean',
        'avg_yac_above_expectation': 'mean',
        'receiving_epa': 'sum'
    }
    
    for col, agg_func in additional_cols.items():
        if col in receiving_df.columns:
            agg_dict[col] = agg_func
    
    player_stats = receiving_df.groupby('player_display_name').agg(agg_dict).reset_index()
    
    # Calculate efficiency metrics
    if rec_yards_col in player_stats.columns and 'receptions' in player_stats.columns:
        player_stats['yards_per_reception'] = player_stats[rec_yards_col] / player_stats['receptions']
    if rec_yards_col in player_stats.columns and 'targets' in player_stats.columns:
        player_stats['yards_per_target'] = player_stats[rec_yards_col] / player_stats['targets']
    
    # Sort by receiving yards
    sort_col = rec_yards_col if rec_yards_col in player_stats.columns else player_stats.columns[1]
    return player_stats.sort_values(sort_col, ascending=False)

def analyze_nextgen_passing(nextgen_data):
    """Analyze Next Gen passing statistics"""
    if 'passing' not in nextgen_data:
        return pd.DataFrame()
    
    passing_df = nextgen_data['passing'].copy()
    
    # Handle different column naming conventions
    pass_yards_col = 'pass_yards' if 'pass_yards' in passing_df.columns else 'passing_yards'
    pass_td_col = 'pass_touchdowns' if 'pass_touchdowns' in passing_df.columns else 'passing_tds'
    
    # Group by player and calculate totals
    agg_dict = {
        pass_yards_col: 'sum',
        pass_td_col: 'sum',
        'completions': 'sum',
        'attempts': 'sum'
    }
    
    # Add additional columns if they exist
    additional_cols = {
        'avg_air_yards': 'mean',
        'avg_air_yards_to_sticks': 'mean',
        'avg_completed_air_yards': 'mean',
        'avg_intended_air_yards': 'mean',
        'avg_air_yards_differential': 'mean',
        'passing_epa': 'sum',
        'completion_percentage': 'mean',
        'avg_time_to_throw': 'mean',
        'avg_velocity': 'mean'
    }
    
    for col, agg_func in additional_cols.items():
        if col in passing_df.columns:
            agg_dict[col] = agg_func
    
    player_stats = passing_df.groupby('player_display_name').agg(agg_dict).reset_index()
    
    # Calculate efficiency metrics
    if pass_yards_col in player_stats.columns and 'attempts' in player_stats.columns:
        player_stats['yards_per_attempt'] = player_stats[pass_yards_col] / player_stats['attempts']
    if pass_yards_col in player_stats.columns and 'completions' in player_stats.columns:
        player_stats['yards_per_completion'] = player_stats[pass_yards_col] / player_stats['completions']
    
    # Sort by pass yards
    sort_col = pass_yards_col if pass_yards_col in player_stats.columns else player_stats.columns[1]
    return player_stats.sort_values(sort_col, ascending=False)

# Tabs Setup - Updated to include Next Gen Stats tab
tab1, tab2, tab3, tab4 = st.tabs(["🛡️ Worst Defenses", "🔥 This Week's Matchups", "🏆 Top Scorers", "📊 Next Gen Stats"])

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

# Tab 4: Next Gen Stats Analysis
with tab4:
    st.header("📊 Next Gen Stats Analysis")
    st.markdown("Advanced metrics powered by NFL's Next Gen Stats data")
    
    if not nextgen_data:
        st.warning("⚠️ No Next Gen Stats data available for this season")
        st.info("Next Gen Stats data is only available for recent seasons (2020+)")
    else:
        # Position selector for Next Gen Stats
        ngs_position = st.selectbox(
            "Select Position for Next Gen Analysis",
            ["Rushing", "Receiving", "Passing"],
            key="ngs_position"
        )
        
        if ngs_position == "Rushing":
            st.subheader("🏃 Advanced Rushing Metrics")
            
            rushing_stats = analyze_nextgen_rushing(nextgen_data)
            if not rushing_stats.empty:
                # Display key metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    rush_yards_col = 'rush_yards' if 'rush_yards' in rushing_stats.columns else 'rushing_yards'
                    if rush_yards_col in rushing_stats.columns:
                        st.metric("Total Rush Yards", f"{rushing_stats[rush_yards_col].sum():,}")
                with col2:
                    rush_td_col = 'rush_touchdowns' if 'rush_touchdowns' in rushing_stats.columns else 'rushing_tds'
                    if rush_td_col in rushing_stats.columns:
                        st.metric("Total Rush TDs", f"{rushing_stats[rush_td_col].sum():,}")
                with col3:
                    rush_att_col = 'rush_attempts' if 'rush_attempts' in rushing_stats.columns else 'rushing_att'
                    if rush_att_col in rushing_stats.columns:
                        st.metric("Total Rush Attempts", f"{rushing_stats[rush_att_col].sum():,}")
                
                # Top performers
                st.subheader("🏆 Top Rushing Performers")
                
                # Sort options
                sort_options = ["rush_yards", "rush_touchdowns", "yards_per_carry"]
                available_sort_options = [opt for opt in sort_options if opt in rushing_stats.columns]
                
                if available_sort_options:
                    sort_by = st.selectbox(
                        "Sort by:",
                        available_sort_options,
                        format_func=lambda x: {
                            "rush_yards": "Total Rush Yards",
                            "rush_touchdowns": "Rush Touchdowns", 
                            "yards_per_carry": "Yards Per Carry"
                        }.get(x, x)
                    )
                    
                    top_rushers = rushing_stats.sort_values(sort_by, ascending=False).head(15)
                    
                    # Display table
                    display_cols = ['player_display_name']
                    for col in ['rush_yards', 'rush_touchdowns', 'rush_attempts', 'yards_per_carry']:
                        if col in top_rushers.columns:
                            display_cols.append(col)
                    
                    st.dataframe(
                        top_rushers[display_cols].rename(columns={
                            'player_display_name': 'Player',
                            'rush_yards': 'Rush Yards',
                            'rush_touchdowns': 'Rush TDs',
                            'rush_attempts': 'Attempts',
                            'yards_per_carry': 'YPC'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Chart if we have data
                    if len(top_rushers) > 0:
                        st.subheader("📈 Top Rushing Performers")
                        chart_col = 'rush_yards' if 'rush_yards' in top_rushers.columns else display_cols[1]
                        chart_data = top_rushers.set_index('player_display_name')[chart_col]
                        st.bar_chart(chart_data)
            else:
                st.info("No rushing Next Gen Stats data available")
        
        elif ngs_position == "Receiving":
            st.subheader("📡 Advanced Receiving Metrics")
            
            receiving_stats = analyze_nextgen_receiving(nextgen_data)
            if not receiving_stats.empty:
                # Display key metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    rec_yards_col = 'receiving_yards' if 'receiving_yards' in receiving_stats.columns else 'rec_yards'
                    if rec_yards_col in receiving_stats.columns:
                        st.metric("Total Receiving Yards", f"{receiving_stats[rec_yards_col].sum():,}")
                with col2:
                    if 'receptions' in receiving_stats.columns:
                        st.metric("Total Receptions", f"{receiving_stats['receptions'].sum():,}")
                with col3:
                    if 'targets' in receiving_stats.columns:
                        st.metric("Total Targets", f"{receiving_stats['targets'].sum():,}")
                
                # Top performers
                st.subheader("🏆 Top Receiving Performers")
                
                # Sort options
                sort_options = ["receiving_yards", "receptions", "yards_per_reception"]
                available_sort_options = [opt for opt in sort_options if opt in receiving_stats.columns]
                
                if available_sort_options:
                    sort_by = st.selectbox(
                        "Sort by:",
                        available_sort_options,
                        format_func=lambda x: {
                            "receiving_yards": "Total Receiving Yards",
                            "receptions": "Receptions",
                            "yards_per_reception": "Yards Per Reception"
                        }.get(x, x)
                    )
                    
                    top_receivers = receiving_stats.sort_values(sort_by, ascending=False).head(15)
                    
                    # Display table
                    display_cols = ['player_display_name']
                    for col in ['receiving_yards', 'receptions', 'targets', 'yards_per_reception']:
                        if col in top_receivers.columns:
                            display_cols.append(col)
                    
                    st.dataframe(
                        top_receivers[display_cols].rename(columns={
                            'player_display_name': 'Player',
                            'receiving_yards': 'Rec Yards',
                            'receptions': 'Receptions',
                            'targets': 'Targets',
                            'yards_per_reception': 'YPR'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Chart if we have data
                    if len(top_receivers) > 0:
                        st.subheader("📈 Top Receiving Performers")
                        chart_col = 'receiving_yards' if 'receiving_yards' in top_receivers.columns else display_cols[1]
                        chart_data = top_receivers.set_index('player_display_name')[chart_col]
                        st.bar_chart(chart_data)
            else:
                st.info("No receiving Next Gen Stats data available")
        
        elif ngs_position == "Passing":
            st.subheader("🎯 Advanced Passing Metrics")
            
            passing_stats = analyze_nextgen_passing(nextgen_data)
            if not passing_stats.empty:
                # Display key metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    pass_yards_col = 'pass_yards' if 'pass_yards' in passing_stats.columns else 'passing_yards'
                    if pass_yards_col in passing_stats.columns:
                        st.metric("Total Pass Yards", f"{passing_stats[pass_yards_col].sum():,}")
                with col2:
                    if 'completions' in passing_stats.columns:
                        st.metric("Total Completions", f"{passing_stats['completions'].sum():,}")
                with col3:
                    if 'attempts' in passing_stats.columns:
                        st.metric("Total Attempts", f"{passing_stats['attempts'].sum():,}")
                
                # Top performers
                st.subheader("🏆 Top Passing Performers")
                
                # Sort options
                sort_options = ["pass_yards", "completions", "yards_per_attempt"]
                available_sort_options = [opt for opt in sort_options if opt in passing_stats.columns]
                
                if available_sort_options:
                    sort_by = st.selectbox(
                        "Sort by:",
                        available_sort_options,
                        format_func=lambda x: {
                            "pass_yards": "Total Pass Yards",
                            "completions": "Completions",
                            "yards_per_attempt": "Yards Per Attempt"
                        }.get(x, x)
                    )
                    
                    top_passers = passing_stats.sort_values(sort_by, ascending=False).head(15)
                    
                    # Display table
                    display_cols = ['player_display_name']
                    for col in ['pass_yards', 'completions', 'attempts', 'yards_per_attempt']:
                        if col in top_passers.columns:
                            display_cols.append(col)
                    
                    st.dataframe(
                        top_passers[display_cols].rename(columns={
                            'player_display_name': 'Player',
                            'pass_yards': 'Pass Yards',
                            'completions': 'Completions',
                            'attempts': 'Attempts',
                            'yards_per_attempt': 'YPA'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Chart if we have data
                    if len(top_passers) > 0:
                        st.subheader("📈 Top Passing Performers")
                        chart_col = 'pass_yards' if 'pass_yards' in top_passers.columns else display_cols[1]
                        chart_data = top_passers.set_index('player_display_name')[chart_col]
                        st.bar_chart(chart_data)
            else:
                st.info("No passing Next Gen Stats data available")

st.markdown("---")
st.markdown("📊 Data: [nflverse](https://github.com/nflverse/nflreadpy) | Next Gen Stats: [nflverse-data](https://github.com/nflverse/nflverse-data) | Updated weekly during NFL season")
